import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from st_supabase_connection import SupabaseConnection
import os

# --- 1. KẾT NỐI DATABASE ĐÁM MÂY SUPABASE ---
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["SUPABASE_URL"],
    key=st.secrets["SUPABASE_KEY"]
)

# --- 2. KHỞI TẠO TRẠNG THÁI ĐĂNG NHẬP (SESSION STATE) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.name = ""
    st.session_state.role = ""
    st.session_state.username = ""

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    st.set_page_config(page_title="Đăng nhập hệ thống", layout="centered")
    st.title("🔑 Đăng nhập Hệ thống Dự án")
    
    with st.form("login_form"):
        username_input = st.text_input("Tài khoản (Username)", placeholder="Nhập tên tài khoản viết liền không dấu")
        password_input = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu")
        submit = st.form_submit_button("Đăng nhập")
        
        if submit:
            if not username_input or not password_input:
                st.error("Vui lòng điền đầy đủ tài khoản và mật khẩu!")
            else:
                try:
                    # Truy vấn tìm tài khoản trong bảng 'users' trên Supabase
                    res = conn.table("users").select("*").eq("username", username_input.strip().lower()).execute()
                    
                    # SỬA ĐÚNG LOGIC ĐỌC PHẦN TỬ TRONG MẢNG (LIST DATA):
                    if res.data and len(res.data) > 0:
                        user_info = res.data[0]  # Thêm chỉ mục [0] để lấy bản ghi đầu tiên trả về
                        
                        # Kiểm tra mật khẩu (so sánh chuỗi thuần)
                        if str(user_info["password"]) == str(password_input):
                            st.session_state.logged_in = True
                            st.session_state.role = user_info["role"]
                            st.session_state.name = user_info["name"]
                            st.session_state.username = user_info["username"]
                            st.success("Đăng nhập thành công!")
                            st.rerun()
                        else:
                            st.error("Mật khẩu nhập vào không chính xác!")
                    else:
                        st.error("Tài khoản này không tồn tại trên hệ thống!")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
else:
    # --- 4. GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP THÀNH CÔNG ---
    st.set_page_config(page_title="Hệ thống Quản lý Dự án", layout="wide")
    
    # Thanh điều hướng Sidebar trái
    st.sidebar.title(f"👋 Chào, {st.session_state.name}")
    st.sidebar.info(f"Vai trò quyền hạn: **{st.session_state.role}**")
    if st.sidebar.button("🔓 Đăng xuất khỏi hệ thống"):
        st.session_state.logged_in = False
        st.session_state.name, st.session_state.role, st.session_state.username = "", "", ""
        st.rerun()

    # Cấu hình Menu linh hoạt dựa trên quyền Role của người dùng
    menu = ["📊 Báo cáo tổng quan", "⏱️ Log thời gian công việc"]
    if st.session_state.role == "Quản lý":
        menu.insert(1, "➕ Giao việc mới (Quản lý)")
        menu.append("👤 Quản lý nhân sự (Quản lý)")
        
    choice = st.sidebar.selectbox("Lựa chọn chức năng", menu)
    st.title("📋 Hệ thống Điều hành Dự án & Báo cáo Giờ làm việc")

    # --- CHỨC NĂNG 1: BÁO CÁO TỔNG QUAN ---
    if choice == "📊 Báo cáo tổng quan":
        st.subheader("Bảng số liệu và đồ thị tiến độ trực tuyến")
        
        # Đọc danh sách tác vụ từ bảng 'tasks'
        res_tasks = conn.table("tasks").select("*").execute()
        df = pd.DataFrame(res_tasks.data)
        
        if df.empty:
            st.info("Hiện tại chưa có dữ liệu công việc nào được tạo lập trên hệ thống.")
        else:
            # Khu vực bảng thẻ KPI tổng hợp nhanh số liệu toàn công ty
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Tổng số lượng dự án", df['project'].nunique())
            kpi2.metric("Tổng thời gian đã cống hiến", f"{df['hours_spent'].sum()} giờ")
            kpi3.metric("Tỷ lệ hoàn thành công việc", f"{len(df[df['status']=='Hoàn thành'])}/{len(df)} đầu việc")
            
            st.markdown("---")
            
            # Trực quan hóa dữ liệu bằng đồ thị động
            c1, c2 = st.columns(2)
            with c1:
                df_bar = df.groupby('project')['hours_spent'].sum().reset_index()
                fig_bar = px.bar(df_bar, x='project', y='hours_spent', title="Tổng thời gian thực tế đã phân bổ theo từng Dự án", color='project', labels={'project':'Tên dự án', 'hours_spent':'Tổng số giờ làm'})
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                df_pie = df['status'].value_counts().reset_index()
                fig_pie = px.pie(df_pie, names='status', values='count', title="Biểu đồ tỷ trọng trạng thái tiến độ các đầu việc")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            st.markdown("---")
            st.write("📋 **Bảng thống kê chi tiết toàn bộ danh mục công việc:**")
            st.dataframe(df[['project', 'task_name', 'assignee', 'status', 'hours_spent', 'date_updated']], use_container_width=True)

    # --- CHỨC NĂNG 2: GIAO VIỆC MỚI (CHỈ QUẢN LÝ THẤY) ---
    elif choice == "➕ Giao việc mới (Quản lý)":
        st.subheader("Giao chỉ tiêu, phân phối nhiệm vụ mới cho nhân viên")
        
        # Truy vấn danh sách nhân viên từ database để hiển thị vào ô lựa chọn
        res_us = conn.table("users").select("name").eq("role", "Nhân viên").execute()
        staff_list = [u["name"] for u in res_us.data] if res_us.data else []
        
        if not staff_list:
            st.warning("Hệ thống chưa có nhân viên nào. Vui lòng vào mục 'Quản lý nhân sự' để thêm tài khoản nhân viên trước.")
        else:
            with st.form("add_task_form"):
                project_name = st.text_input("Nhập tên dự án", placeholder="Ví dụ: Dự án Thiết kế, Dự án Xây dựng...")
                task_title = st.text_input("Nhập tên đầu việc cần xử lý", placeholder="Ví dụ: Lập trình giao diện, Thiết kế bản vẽ...")
                assignee_select = st.selectbox("Giao nhiệm vụ cho nhân viên:", staff_list)
                
                if st.form_submit_button("Xác nhận giao việc"):
                    if not project_name or not task_title:
                        st.error("Vui lòng không để trống thông tin Tên dự án và Tên đầu việc!")
                    else:
                        conn.table("tasks").insert({
                            "project": project_name.strip(),
                            "task_name": task_title.strip(),
                            "assignee": assignee_select,
                            "status": "Chưa bắt đầu",
                            "hours_spent": 0.0,
                            "date_updated": datetime.now().strftime("%Y-%m-%d")
                        }).execute()
                        st.success(f"Đã tạo và giao thành công việc '{task_title}' cho {assignee_select} lên cơ sở dữ liệu mây!")

    # --- CHỨC NĂNG 3: LOG THỜI GIAN VÀ TIẾN ĐỘ ---
    elif choice == "⏱️ Log thời gian công việc":
        st.subheader("Bảng chấm công và cập nhật báo cáo tiến độ công việc hàng ngày")
        
        res_tk = conn.table("tasks").select("*").execute()
        df_all = pd.DataFrame(res_tk.data)
        
        # Cơ chế lọc thông minh: Nếu là nhân viên, hệ thống ép buộc chỉ được sửa việc mang tên mình.
        if st.session_state.role == "Nhân viên":
            df_display = df_all[df_all['assignee'] == st.session_state.name] if not df_all.empty else pd.DataFrame()
        else:
            df_display = df_all # Quản lý có quyền xem và log hộ thời gian cho tất cả mọi việc
            
        if df_display.empty:
            st.warning("Bạn chưa được giao bất kỳ công việc nào trên hệ thống hoặc danh sách trống.")
        else:
            # Tạo chuỗi văn bản gợi ý tường minh để lựa chọn công việc
            task_options = df_display.apply(lambda r: f"[{r['project']}] {r['task_name']}", axis=1).tolist()
            selected_task = st.selectbox("Vui lòng chọn đầu việc bạn vừa thực hiện xử lý:", task_options)
            
            task_index = task_options.index(selected_task)
            task_db_id = int(df_display.iloc[task_index]['id'])
            current_logged_hours = float(df_display.iloc[task_index]['hours_spent'])
            
            col_left, col_right = st.columns(2)
            with col_left:
                status_update = st.selectbox(
                    "Cập nhật lại trạng thái thực tế:", 
                    ["Chưa bắt đầu", "Đang làm", "Hoàn thành"], 
                    index=["Chưa bắt đầu", "Đang làm", "Hoàn thành"].index(df_display.iloc[task_index]['status'])
                )
            with col_right:
                added_hours_today = st.number_input("Số giờ làm việc cống hiến thêm hôm nay (Ví dụ: 1.5, 2.0, ...):", min_value=0.0, step=0.5, format="%.1f")
                
            if st.button("Lưu Logs & Cộng dồn thời gian"):
                new_cumulative_hours = current_logged_hours + added_hours_today
                conn.table("tasks").update({
                    "status": status_update,
                    "hours_spent": new_cumulative_hours,
                    "date_updated": datetime.now().strftime("%Y-%m-%d")
                }).eq("id", task_db_id).execute()
                st.success(f"Đã đồng bộ thành công! Tổng thời gian tích lũy cho việc này hiện tại là: {new_cumulative_hours} giờ.")

    # --- CHỨC NĂNG 4: QUẢN LÝ NHÂN SỰ VÀ TÀI KHOẢN (CHỈ QUẢN LÝ THẤY) ---
    elif choice == "👤 Quản lý nhân sự (Quản lý)":
        st.subheader("Hệ thống khởi tạo và cấp phát tài khoản nhân sự")
        
