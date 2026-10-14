import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from st_supabase_connection import SupabaseConnection

# --- CẤU HÌNH TRANG (BẮT BUỘC ĐẶT ĐẦU TIÊN CỦA FILE) ---
st.set_page_config(page_title="Hệ thống Quản lý Dự án", layout="wide")

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
                    # Truy vấn ép buộc không lưu cache bằng conn.query(..., ttl=0)
                    clean_username = username_input.strip().lower()
                    query_user = f"SELECT * FROM users WHERE username = '{clean_username}'"
                    res = conn.query(query_user, ttl=0)

                    if res is not None and not res.empty:
                        user_info = res.iloc[0]  # Lấy hàng đầu tiên tìm thấy trong DataFrame

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
                    st.error(f"Lỗi hệ thống khi đăng nhập: {e}")
else:
    # --- 4. GIAO DIỆN CHÍNH SAU KHI ĐĂNG NHẬP THÀNH CÔNG ---

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

        try:
            # Đọc danh sách tác vụ trực tiếp không qua cache
            df = conn.query("SELECT * FROM tasks", ttl=0)

            if df is None or df.empty:
                st.info("Hiện tại chưa có dữ liệu công việc nào được tạo lập trên hệ thống.")
            else:
                # Khu vực bảng thẻ KPI tổng hợp nhanh số liệu toàn công ty
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Tổng số lượng dự án", df['project'].nunique())
                kpi2.metric("Tổng thời gian đã cống hiến", f"{df['hours_spent'].sum()} giờ")
                kpi3.metric("Tỷ lệ hoàn thành công việc", f"{len(df[df['status'] == 'Hoàn thành'])}/{len(df)} đầu việc")

                st.markdown("---")

                # Trực quan hóa dữ liệu bằng đồ thị động
                c1, c2 = st.columns(2)
                with c1:
                    df_bar = df.groupby('project')['hours_spent'].sum().reset_index()
                    fig_bar = px.bar(df_bar, x='project', y='hours_spent',
                                     title="Tổng thời gian thực tế đã phân bổ theo từng Dự án", color='project',
                                     labels={'project': 'Tên dự án', 'hours_spent': 'Tổng số giờ làm'})
                    st.plotly_chart(fig_bar, use_container_width=True)
                with c2:
                    df_pie = df['status'].value_counts().reset_index()
                    fig_pie = px.pie(df_pie, names='status', values='count',
                                     title="Biểu đồ tỷ trọng trạng thái tiến độ các đầu việc")
                    st.plotly_chart(fig_pie, use_container_width=True)

                st.markdown("---")
                st.write("📋 **Bảng thống kê chi tiết toàn bộ danh mục công việc:**")
                st.dataframe(df[['project', 'task_name', 'assignee', 'status', 'hours_spent', 'date_updated']],
                             use_container_width=True)
        except Exception as e:
            st.error(f"Lỗi tải dữ liệu báo cáo: {e}")

    # --- CHỨC NĂNG 2: GIAO VIỆC MỚI (CHỈ QUẢN LÝ THẤY) ---
    elif choice == "➕ Giao việc mới (Quản lý)":
        st.subheader("Giao chỉ tiêu, phân phối nhiệm vụ mới cho nhân viên")

        try:
            # Truy vấn danh sách nhân viên từ database
            df_us = conn.query("SELECT name FROM users WHERE role = 'Nhân viên'", ttl=0)
            staff_list = df_us['name'].tolist() if (df_us is not None and not df_us.empty) else []

            if not staff_list:
                st.warning(
                    "Hệ thống chưa có nhân viên nào. Vui lòng vào mục 'Quản lý nhân sự' để thêm tài khoản nhân viên trước.")
            else:
                with st.form("add_task_form"):
                    project_name = st.text_input("Nhập tên dự án",
                                                 placeholder="Ví dụ: Dự án Thiết kế, Dự án Xây dựng...")
                    task_title = st.text_input("Nhập tên đầu việc cần xử lý",
                                               placeholder="Ví dụ: Lập trình giao diện, Thiết kế bản vẽ...")
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
                            st.success(f"Đã tạo và giao thành công việc '{task_title}' cho {assignee_select}!")
                            st.rerun()
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")

    # --- CHỨC NĂNG 3: LOG THỜI GIAN VÀ TIẾN ĐỘ ---
    elif choice == "⏱️ Log thời gian công việc":
        st.subheader("Bảng chấm công và cập nhật báo cáo tiến độ công việc hàng ngày")

        try:
            df_all = conn.query("SELECT * FROM tasks", ttl=0)

            # Cơ chế lọc thông minh: Nếu là nhân viên, hệ thống ép buộc chỉ được sửa việc mang tên mình.
            if st.session_state.role == "Nhân viên":
                df_display = df_all[df_all['assignee'] == st.session_state.name] if (
                            df_all is not None and not df_all.empty) else pd.DataFrame()
            else:
                df_display = df_all

            if df_display is None or df_display.empty:
                st.warning("Bạn chưa được giao bất kỳ công việc nào trên hệ thống hoặc danh sách trống.")
            else:
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
                    added_hours_today = st.number_input("Số giờ làm việc cống hiến thêm hôm nay:", min_value=0.0,
                                                        step=0.5, format="%.1f")

                if st.button("Lưu Logs & Cộng dồn thời gian"):
                    new_cumulative_hours = current_logged_hours + added_hours_today
                    conn.table("tasks").update({
                        "status": status_update,
                        "hours_spent": new_cumulative_hours,
                        "date_updated": datetime.now().strftime("%Y-%m-%d")
                    }).eq("id", task_db_id).execute()
                    st.success(f"Đã lưu! Tổng thời gian của đầu việc: {new_cumulative_hours} giờ.")
                    st.rerun()
                except Exception as e:
                st.error(f"Lỗi cập nhật dữ liệu: {e}")

            # --- CHỨC NĂNG 4: QUẢN LÝ NHÂN SỰ (CHỈ QUẢN LÝ THẤY) ---
            elif choice == "👤 Quản lý nhân sự (Quản lý)":
            st.subheader("Quản lý tài khoản nhân sự")

            try:
                df_users = conn.query("SELECT username, name, role FROM users", ttl=0)
                if df_users is not None and not df_users.empty:
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
                        elif df_users is not None and not df_users.empty and \
                                clean_new_username in df_users["username"].str.lower().tolist():
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
                if df_users is not None and not df_users.empty:
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
