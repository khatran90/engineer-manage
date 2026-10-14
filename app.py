import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from st_supabase_connection import SupabaseConnection, execute_query

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Quản lý Dự án & Nhân sự", layout="wide")

# --- 1. KẾT NỐI DATABASE SUPABASE ---
conn = st.connection(
    "supabase",
    type=SupabaseConnection,
    url=st.secrets["SUPABASE_URL"],
    key=st.secrets["SUPABASE_KEY"]
)

# --- 2. KHỞI TẠO SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.name = ""
    st.session_state.role = ""
    st.session_state.username = ""

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.logged_in:
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
                    clean_username = username_input.strip().lower()
                    # Sử dụng cú pháp bảng Supabase thay cho lệnh query SQL
                    res = execute_query(
                        conn.table("users").select("*").eq("username", clean_username),
                        ttl=0
                    )

                    if res.data:
                        user_info = res.data[0]
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
                    st.error(f"Lỗi hệ thống khi đăng nhập: {e}")
else:
    # --- 4. GIAO DIỆN CHÍNH ---
    st.sidebar.title(f"👋 Chào, {st.session_state.name}")
    st.sidebar.info(f"Vai trò: **{st.session_state.role}**")
    if st.sidebar.button("🔓 Đăng xuất"):
        st.session_state.logged_in = False
        st.session_state.name, st.session_state.role, st.session_state.username = "", "", ""
        st.rerun()

    menu = ["📊 Báo cáo tổng quan", "⏱️ Log thời gian công việc"]
    if st.session_state.role == "Quản lý":
        menu.insert(1, "📁 Quản lý & Tạo dự án (Quản lý)")
        menu.insert(2, "➕ Giao việc mới (Quản lý)")
        menu.insert(3, "🔀 Phân tích Chồng chéo & Phân bổ")
        menu.append("👤 Quản lý nhân sự (Quản lý)")

    choice = st.sidebar.selectbox("Lựa chọn chức năng", menu)
    st.title("📋 Hệ thống Quản lý Dự án & Tiến độ Nhân sự")

    # --- CHỨC NĂNG: BÁO CÁO TỔNG QUAN ---
    if choice == "📊 Báo cáo tổng quan":
        st.subheader("Bảng số liệu tổng quan & Tiến độ dự án")
        try:
            res_tasks = execute_query(conn.table("tasks").select("*"), ttl=0)
            df = pd.DataFrame(res_tasks.data) if res_tasks.data else pd.DataFrame()

            if df.empty:
                st.info("Hiện tại chưa có dữ liệu công việc nào.")
            else:
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Tổng số lượng dự án", df['project'].nunique())
                kpi2.metric("Tổng thời gian đã cống hiến", f"{df['hours_spent'].sum():.1f} giờ")
                kpi3.metric("Số việc hoàn thành", f"{len(df[df['status'] == 'Hoàn thành'])}/{len(df)}")

                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    df_bar = df.groupby('project')['hours_spent'].sum().reset_index()
                    fig_bar = px.bar(df_bar, x='project', y='hours_spent', title="Tổng giờ làm theo từng Dự án", color='project')
                    st.plotly_chart(fig_bar, use_container_width=True)
                with c2:
                    df_pie = df['status'].value_counts().reset_index()
                    fig_pie = px.pie(df_pie, names='status', values='count', title="Tỷ trọng trạng thái công việc")
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown("---")
                st.write("📋 **Danh sách chi tiết công việc:**")
                st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Lỗi tải báo cáo: {e}")

    # --- CHỨC NĂNG: QUẢN LÝ & TẠO DỰ ÁN ---
    elif choice == "📁 Quản lý & Tạo dự án (Quản lý)":
        st.subheader("Quản lý Danh mục Dự án")

        try:
            res_pj = execute_query(conn.table("projects").select("*").order("id", desc=True), ttl=0)
            df_pj = pd.DataFrame(res_pj.data) if res_pj.data else pd.DataFrame()

            if not df_pj.empty:
                st.write("📋 **Danh sách Dự án đang triển khai:**")
                st.dataframe(df_pj, use_container_width=True)
            else:
                st.info("Chưa có dự án nào được khởi tạo.")

            st.markdown("---")
            st.write("➕ **Khởi tạo Dự án mới:**")
            with st.form("create_project_form", clear_on_submit=True):
                p_name = st.text_input("Tên dự án mới", placeholder="Ví dụ: Dự án Tòa nhà A, Dự án Cầu B...")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    start_d = st.date_input("Ngày bắt đầu dự án", datetime.now())
                with col_d2:
                    end_d = st.date_input("Ngày kết thúc dự kiến", datetime.now())

                if st.form_submit_button("Tạo Dự án"):
                    if not p_name.strip():
                        st.error("Tên dự án không được để trống!")
                    elif start_d > end_d:
                        st.error("Ngày bắt đầu không được lớn hơn ngày kết thúc dự kiến!")
                    else:
                        conn.table("projects").insert({
                            "project_name": p_name.strip(),
                            "start_date": str(start_d),
                            "end_date": str(end_d),
                            "status": "Đang triển khai"
                        }).execute()
                        st.success(f"Đã tạo thành công dự án '{p_name}'!")
                        st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi quản lý dự án: {e}")

    # --- CHỨC NĂNG: GIAO VIỆC MỚI ---
    elif choice == "➕ Giao việc mới (Quản lý)":
        st.subheader("Giao nhiệm vụ cho Nhân viên")

        try:
            res_us = execute_query(conn.table("users").select("name").eq("role", "Nhân viên"), ttl=0)
            res_pj = execute_query(conn.table("projects").select("project_name").eq("status", "Đang triển khai"), ttl=0)

            staff_list = [u["name"] for u in res_us.data] if res_us.data else []
            project_list = [p["project_name"] for p in res_pj.data] if res_pj.data else []

            if not staff_list:
                st.warning("Chưa có nhân viên nào trên hệ thống. Vui lòng thêm nhân viên trước.")
            elif not project_list:
                st.warning("Chưa có dự án nào đang mở. Vui lòng vào mục 'Quản lý & Tạo dự án' để thêm dự án trước.")
            else:
                with st.form("add_task_form"):
                    project_select = st.selectbox("Chọn Dự án:", project_list)
                    task_title = st.text_input("Tên đầu việc cần xử lý", placeholder="Ví dụ: Thiết kế bản vẽ móng, Lập báo cáo...")
                    assignee_select = st.selectbox("Giao cho nhân viên:", staff_list)

                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        task_start = st.date_input("Ngày bắt đầu công việc", datetime.now())
                    with col_t2:
                        task_end = st.date_input("Ngày dự kiến hoàn thành", datetime.now())

                    if st.form_submit_button("Xác nhận giao việc"):
                        if not task_title.strip():
                            st.error("Vui lòng nhập tên đầu việc!")
                        elif task_start > task_end:
                            st.error("Ngày bắt đầu công việc không được lớn hơn ngày kết thúc!")
                        else:
                            conn.table("tasks").insert({
                                "project": project_select,
                                "task_name": task_title.strip(),
                                "assignee": assignee_select,
                                "status": "Chưa bắt đầu",
                                "hours_spent": 0.0,
                                "date_updated": datetime.now().strftime("%Y-%m-%d"),
                                "start_date": str(task_start),
                                "end_date": str(task_end)
                            }).execute()
                            st.success(f"Đã giao việc '{task_title}' cho {assignee_select} thuộc dự án [{project_select}]!")
                            st.rerun()
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")

    # --- CHỨC NĂNG: PHÂN TÍCH CHỒNG CHÉO & PHÂN BỔ NHÂN SỰ ---
    elif choice == "🔀 Phân tích Chồng chéo & Phân bổ":
        st.subheader("Phân tích Tải công việc & Sự chồng chéo Dự án của Nhân sự")

        try:
            res_tasks = execute_query(conn.table("tasks").select("*").neq("status", "Hoàn thành"), ttl=0)
            df_tasks = pd.DataFrame(res_tasks.data) if res_tasks.data else pd.DataFrame()
            
            if df_tasks.empty:
                st.info("Hiện không có công việc nào đang dở dang hoặc chưa bắt đầu.")
            else:
                df_user_projects = df_tasks.groupby('assignee')['project'].nunique().reset_index()
                df_user_projects.columns = ['Nhân sự', 'Số lượng Dự án đang phụ trách']

                overloaded_users = df_user_projects[df_user_projects['Số lượng Dự án đang phụ trách'] > 1]

                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.write("📊 **Số lượng Dự án đang xử lý theo từng Nhân sự:**")
                    fig_workload = px.bar(
                        df_user_projects, 
                        x='Nhân sự', 
                        y='Số lượng Dự án đang phụ trách', 
                        color='Số lượng Dự án đang phụ trách',
                        color_continuous_scale='Reds'
                    )
                    st.plotly_chart(fig_workload, use_container_width=True)

                with col_stat2:
                    st.write("⚠️ **Cảnh báo Chồng chéo Dự án:**")
                    if not overloaded_users.empty:
                        for _, row in overloaded_users.iterrows():
                            st.error(f"🚨 **{row['Nhân sự']}** đang tham gia **{row['Số lượng Dự án đang phụ trách']} dự án** cùng lúc!")
                            user_pjs = df_tasks[df_tasks['assignee'] == row['Nhân sự']]['project'].unique()
                            st.write(f"👉 Các dự án: *{', '.join(user_pjs)}*")
                    else:
                        st.success("✅ Hiện không có nhân sự nào bị phân bổ hơn 1 dự án đồng thời.")

                st.markdown("---")
                st.write("🔍 **Ma trận phân bổ Đầu việc theo Nhân sự & Dự án:**")
                pivot_df = pd.pivot_table(
                    df_tasks, 
                    index='assignee', 
                    columns='project', 
                    values='task_name', 
                    aggfunc='count', 
                    fill_value=0
                )
                st.dataframe(pivot_df, use_container_width=True)

        except Exception as e:
            st.error(f"Lỗi khi phân tích chồng chéo: {e}")

    # --- CHỨC NĂNG: LOG THỜI GIAN CÔNG VIỆC ---
    elif choice == "⏱️ Log thời gian công việc":
        st.subheader("Cập nhật báo cáo tiến độ công việc hàng ngày")
        try:
            res_all = execute_query(conn.table("tasks").select("*"), ttl=0)
            df_all = pd.DataFrame(res_all.data) if res_all.data else pd.DataFrame()

            if st.session_state.role == "Nhân viên":
                df_display = df_all[df_all['assignee'] == st.session_state.name] if not df_all.empty else pd.DataFrame()
            else:
                df_display = df_all

            if df_display.empty:
                st.warning("Bạn chưa được giao bất kỳ công việc nào hoặc danh sách trống.")
            else:
                task_options = df_display.apply(lambda r: f"[{r['project']}] {r['task_name']}", axis=1).tolist()
                selected_task = st.selectbox("Chọn đầu việc vừa thực hiện:", task_options)

                task_index = task_options.index(selected_task)
                task_db_id = int(df_display.iloc[task_index]['id'])
                current_logged_hours = float(df_display.iloc[task_index]['hours_spent'])

                col_left, col_right = st.columns(2)
                with col_left:
                    status_update = st.selectbox(
                        "Cập nhật trạng thái thực tế:",
                        ["Chưa bắt đầu", "Đang làm", "Hoàn thành"],
                        index=["Chưa bắt đầu", "Đang làm", "Hoàn thành"].index(df_display.iloc[task_index]['status'])
                    )
                with col_right:
                    added_hours_today = st.number_input("Số giờ cống hiến thêm hôm nay:", min_value=0.0, step=0.5, format="%.1f")

                if st.button("Lưu Logs & Cộng dồn thời gian"):
                    new_cumulative_hours = current_logged_hours + added_hours_today
                    conn.table("tasks").update({
                        "status": status_update,
                        "hours_spent": new_cumulative_hours,
                        "date_updated": datetime.now().strftime("%Y-%m-%d")
                    }).eq("id", task_db_id).execute()
                    st.success(f"Đã lưu thành công! Tổng thời gian: {new_cumulative_hours} giờ.")
                    st.rerun()
        except Exception as e:
            st.error(f"Lỗi cập nhật dữ liệu: {e}")

    # --- CHỨC NĂNG: QUẢN LÝ NHÂN SỰ ---
    elif choice == "👤 Quản lý nhân sự (Quản lý)":
        st.subheader("Quản lý tài khoản nhân sự")
        try:
            res_users = execute_query(conn.table("users").select("username, name, role"), ttl=0)
            df_users = pd.DataFrame(res_users.data) if res_users.data else pd.DataFrame()

            if not df_users.empty:
                st.write("📋 **Danh sách tài khoản hiện có:**")
                st.dataframe(df_users, use_container_width=True)

            st.markdown("---")
            st.write("➕ **Thêm tài khoản mới:**")
            with st.form("add_user_form", clear_on_submit=True):
                new_username = st.text_input("Tài khoản (viết liền không dấu)")
                new_password = st.text_input("Mật khẩu", type="password")
                new_name = st.text_input("Họ và tên")
                new_role = st.selectbox("Vai trò", ["Nhân viên", "Quản lý"])

                if st.form_submit_button("Tạo tài khoản"):
                    clean_new_username = new_username.strip().lower()
                    if not clean_new_username or not new_password or not new_name.strip():
                        st.error("Vui lòng điền đầy đủ thông tin!")
                    elif not df_users.empty and clean_new_username in df_users["username"].str.lower().tolist():
                        st.error("Tài khoản này đã tồn tại!")
                    else:
                        conn.table("users").insert({
                            "username": clean_new_username,
                            "password": new_password,
                            "name": new_name.strip(),
                            "role": new_role
                        }).execute()
                        st.success(f"Đã tạo tài khoản '{clean_new_username}'!")
                        st.rerun()

            st.markdown("---")
            st.write("🗑️ **Xóa tài khoản:**")
            if not df_users.empty:
                del_options = [u for u in df_users["username"].tolist() if u != st.session_state.username]
                if del_options:
                    del_user = st.selectbox("Chọn tài khoản cần xóa", del_options)
                    if st.button("Xóa tài khoản"):
                        conn.table("users").delete().eq("username", del_user).execute()
                        st.success(f"Đã xóa tài khoản '{del_user}'!")
                        st.rerun()
                else:
                    st.info("Không có tài khoản nào khác để xóa.")
        except Exception as e:
            st.error(f"Lỗi quản lý nhân sự: {e}")
