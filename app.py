import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from st_supabase_connection import SupabaseConnection

# --- 1. KẾT NỐI DATABASE ĐÁM MÂY SUPABASE ---
# Streamlit sẽ tự động đọc cấu hình URL và Key từ phần Secrets (sẽ hướng dẫn ở Bước 3)
conn = st.connection("supabase", type=SupabaseConnection)

# --- 2. HỆ THỐNG TÀI KHOẢN ---
USER_CREDENTIALS = {
    "quanly1": {"password": "123", "role": "Quản lý", "name": "Nguyễn Văn A"},
    "nhanvien1": {"password": "456", "role": "Nhân viên", "name": "Trần Thị B"},
    "nhanvien2": {"password": "789", "role": "Nhân viên", "name": "Lê Văn C"}
}

# --- 3. XỬ LÝ ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.name, st.session_state.role, st.session_state.username = "", "", ""

if not st.session_state.logged_in:
    st.set_page_config(page_title="Đăng nhập", layout="centered")
    st.title("🔑 Đăng nhập Hệ thống Dự án (Internet)")
    with st.form("login_form"):
        username = st.text_input("Tài khoản")
        password = st.text_input("Mật khẩu", type="password")
        if st.form_submit_button("Đăng nhập"):
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.role = USER_CREDENTIALS[username]["role"]
                st.session_state.name = USER_CREDENTIALS[username]["name"]
                st.rerun()
            else:
                st.error("Sai tài khoản hoặc mật khẩu")
else:
    st.set_page_config(page_title="Quản lý Dự án", layout="wide")
    
    # Sidebar
    st.sidebar.title(f"👋 Chào, {st.session_state.name}")
    st.sidebar.info(f"Vai trò: **{st.session_state.role}**")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.logged_in = False
        st.rerun()

    menu = ["📊 Báo cáo tổng quan", "⏱️ Log thời gian (Nhân viên)"]
    if st.session_state.role == "Quản lý":
        menu.insert(1, "➕ Giao việc mới (Chỉ Quản lý)")
    choice = st.sidebar.selectbox("Chức năng", menu)
    st.title("📋 Hệ thống Quản lý Tiến độ trực tuyến")

    # --- CHỨC NĂNG 1: BÁO CÁO TỔNG QUAN ---
    if choice == "📊 Báo cáo tổng quan":
        st.subheader("Bảng theo dõi tiến độ thời gian thực")
        
        # Đọc dữ liệu từ Supabase đám mây
        response = conn.table("tasks").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if df.empty:
            st.info("Chưa có dữ liệu dự án trên hệ thống.")
        else:
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Tổng dự án", df['project'].nunique())
            kpi2.metric("Tổng giờ đã làm", f"{df['hours_spent'].sum()} giờ")
            kpi3.metric("Hoàn thành", f"{len(df[df['status']=='Hoàn thành'])}/{len(df)} việc")
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                fig_bar = px.bar(df.groupby('project')['hours_spent'].sum().reset_index(), x='project', y='hours_spent', title="Tổng giờ theo Dự án", color='project')
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                fig_pie = px.pie(df['status'].value_counts().reset_index(), names='status', values='count', title="Trạng thái công việc")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            st.dataframe(df[['project', 'task_name', 'assignee', 'status', 'hours_spent', 'date_updated']], use_container_width=True)

    # --- CHỨC NĂNG 2: GIAO VIỆC MỚI (CHỈ QUẢN LÝ) ---
    elif choice == "➕ Giao việc mới (Chỉ Quản lý)":
        st.subheader("Giao việc mới cho nhân viên")
        with st.form("add_task"):
            project = st.text_input("Tên dự án")
            task_name = st.text_input("Tên đầu việc")
            staff_list = [USER_CREDENTIALS[u]["name"] for u in USER_CREDENTIALS if USER_CREDENTIALS[u]["role"] == "Nhân viên"]
            assignee = st.selectbox("Giao cho nhân viên", staff_list)
            
            if st.form_submit_button("Tạo công việc"):
                # Thêm dòng dữ liệu mới vào Supabase
                conn.table("tasks").insert({
                    "project": project, "task_name": task_name, "assignee": assignee,
                    "status": "Chưa bắt đầu", "hours_spent": 0.0, "date_updated": datetime.now().strftime("%Y-%m-%d")
                }).execute()
                st.success("Đã giao việc lên hệ thống đám mây!")

    # --- CHỨC NĂNG 3: LOG THỜI GIAN ---
    elif choice == "⏱️ Log thời gian (Nhân viên)":
        st.subheader("Cập nhật giờ làm việc của bạn")
        response = conn.table("tasks").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if st.session_state.role == "Nhân viên":
            df_user = df[df['assignee'] == st.session_state.name]
        else:
            df_user = df
            
        if df_user.empty:
            st.warning("Bạn chưa có công việc nào.")
        else:
            task_options = df_user.apply(lambda r: f"[{r['project']}] {r['task_name']}", axis=1).tolist()
            selected_task = st.selectbox("Chọn công việc vừa làm:", task_options)
            
            idx = task_options.index(selected_task)
            task_id = int(df_user.iloc[idx]['id'])
            current_hours = float(df_user.iloc[idx]['hours_spent'])
            
            c1, c2 = st.columns(2)
            with c1:
                new_status = st.selectbox("Trạng thái:", ["Chưa bắt đầu", "Đang làm", "Hoàn thành"], index=["Chưa bắt đầu", "Đang làm", "Hoàn thành"].index(df_user.iloc[idx]['status']))
            with c2:
                add_hours = st.number_input("Số giờ làm thêm hôm nay:", min_value=0.0, step=0.5)
                
            if st.button("Lưu Logs Thời Gian"):
                # Cập nhật số giờ cộng dồn lên Supabase
                conn.table("tasks").update({
                    "status": new_status, "hours_spent": current_hours + add_hours, "date_updated": datetime.now().strftime("%Y-%m-%d")
                }).eq("id", task_id).execute()
                st.success("Đã cập nhật dữ liệu thành công!")
