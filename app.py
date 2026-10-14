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

# --- 2. KHỞI TẠO DỰ TRỮ PHIÊN ĐĂNG NHẬP QUA QUERY PARAMS (GIỮ NGUYÊN KHI F5) ---
query_params = st.query_params

if "logged_in" not in st.session_state:
    if "user" in query_params and "role" in query_params:
        st.session_state.logged_in = True
        st.session_state.username = query_params["user"]
        st.session_state.role = query_params["role"]
        # Lấy lại tên đầy đủ từ database
        try:
            res_u = execute_query(conn.table("users").select("name").eq("username", query_params["user"]), ttl=0)
            if res_u.data:
                st.session_state.name = res_u.data[0]["name"]
            else:
                st.session_state.name = query_params["user"]
        except:
            st.session_state.name = query_params["user"]
    else:
        st.session_state.logged_in = False
        st.session_state.name = ""
        st.session_state.role = ""
        st.session_state.username = ""

if "lang" not in st.session_state:
    st.session_state.lang = "Tiếng Việt"

# --- BẢNG TỪ ĐIỂN ĐA NGÔN NGỮ ---
translations = {
    "Tiếng Việt": {
        "lang_label": "🌐 Ngôn ngữ / Language",
        "login_title": "🔑 Đăng nhập Hệ thống Dự án",
        "username": "Tài khoản (Username)",
        "username_ph": "Nhập tên tài khoản viết liền không dấu",
        "password": "Mật khẩu",
        "password_ph": "Nhập mật khẩu",
        "login_btn": "Đăng nhập",
        "login_success": "Đăng nhập thành công!",
        "login_err_empty": "Vui lòng điền đầy đủ tài khoản và mật khẩu!",
        "login_err_wrong": "Mật khẩu nhập vào không chính xác!",
        "login_err_notfound": "Tài khoản này không tồn tại trên hệ thống!",
        "logout_btn": "🔓 Đăng xuất",
        "hello": "👋 Chào",
        "role": "Vai trò",
        "role_super_admin": "General Manager",
        "role_sub_admin": "Associate/Senior",
        "role_staff": "Nhân viên",
        "st_not_started": "Chưa bắt đầu",
        "st_in_progress": "Đang làm",
        "st_completed": "Hoàn thành",
        # Menu
        "menu_overview": "📊 Báo cáo tổng quan",
        "menu_project_mgmt": "📁 Quản lý & Cập nhật Dự án",
        "menu_add_task": "➕ Giao việc mới",
        "menu_overlap": "🔀 Phân tích Chồng chéo & Phân bổ",
        "menu_time_log": "⏱️ Log thời gian công việc",
        "menu_change_pw": "🔑 Đổi mật khẩu cá nhân",
        "menu_user_mgmt": "👤 Quản lý nhân sự",
        "main_title": "📋 Hệ thống Quản lý Dự án & Tiến độ Nhân sự",
        "filter_project": "🔍 Lọc theo Dự án:",
        "filter_staff": "👤 Lọc theo Nhân sự:",
        "all": "Tất cả (All)",
        "dashboard_title": "Bảng số liệu tổng quan & Dashboard Nâng cao",
        "project_progress_title": "📈 **Tiến độ % hoàn thành các Dự án:**",
        "gantt_title": "🗓️ **Biểu đồ Lịch trình công việc (Gantt Chart):**",
        "detailed_task_list": "📋 **Danh sách chi tiết công việc:**",
        "no_data": "Hiện tại chưa có dữ liệu công việc nào thuộc quyền quản lý của bạn.",
        "filter_warning": "Không có dữ liệu phù hợp với bộ lọc/tìm kiếm đã chọn.",
    },
    "English": {
        "lang_label": "🌐 Language / Ngôn ngữ",
        "login_title": "🔑 Project System Login",
        "username": "Username",
        "username_ph": "Enter username without spaces",
        "password": "Password",
        "password_ph": "Enter password",
        "login_btn": "Login",
        "login_success": "Login successful!",
        "login_err_empty": "Please fill in both username and password!",
        "login_err_wrong": "Incorrect password!",
        "login_err_notfound": "This account does not exist in the system!",
        "logout_btn": "🔓 Logout",
        "hello": "👋 Hello",
        "role": "Role",
        "role_super_admin": "General Manager",
        "role_sub_admin": "Associate/Senior",
        "role_staff": "Staff",
        "st_not_started": "Not Started",
        "st_in_progress": "In Progress",
        "st_completed": "Completed",
        # Menu
        "menu_overview": "📊 Overview Report",
        "menu_project_mgmt": "📁 Project Management & Update",
        "menu_add_task": "➕ Assign New Task",
        "menu_overlap": "🔀 Overlap & Workload Analysis",
        "menu_time_log": "⏱️ Time Logging & Progress",
        "menu_change_pw": "🔑 Change Password",
        "menu_user_mgmt": "👤 User Management",
        "main_title": "📋 Project Management & Staff Progress System",
        "filter_project": "🔍 Filter by Project:",
        "filter_staff": "🔍 Filter by Staff:",
        "all": "All",
        "dashboard_title": "Overview Report & Advanced Dashboard",
        "project_progress_title": "📈 **Project Completion Progress (%):**",
        "gantt_title": "🗓️ **Task Timeline (Gantt Chart):**",
        "detailed_task_list": "📋 **Detailed Task List:**",
        "no_data": "No task data available under your management.",
        "filter_warning": "No data matches the selected filters/search.",
    }
}

t = translations[st.session_state.lang]

# --- 3. GIAO DIỆN ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    selected_lang = st.sidebar.selectbox(translations["Tiếng Việt"]["lang_label"], ["Tiếng Việt", "English"], index=0 if st.session_state.lang == "Tiếng Việt" else 1)
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

    t = translations[st.session_state.lang]
    st.title(t["login_title"])

    with st.form("login_form"):
        username_input = st.text_input(t["username"], placeholder=t["username_ph"])
        password_input = st.text_input(t["password"], type="password", placeholder=t["password_ph"])
        submit = st.form_submit_button(t["login_btn"])

        if submit:
            if not username_input or not password_input:
                st.error(t["login_err_empty"])
            else:
                try:
                    clean_username = username_input.strip().lower()
                    res = execute_query(
                        conn.table("users").select("*").eq("username", clean_username),
                        ttl=0
                    )

                    if res.data:
                        user_info = res.data[0]
                        if str(user_info["password"]) == str(password_input):
                            st.session_state.logged_in = True
                            st.session_state.role = str(user_info["role"]).strip()
                            st.session_state.name = user_info["name"]
                            st.session_state.username = user_info["username"]
                            
                            # Lưu vào URL query params để giữ trạng thái khi F5
                            st.query_params["user"] = user_info["username"]
                            st.query_params["role"] = str(user_info["role"]).strip()

                            st.success(t["login_success"])
                            st.rerun()
                        else:
                            st.error(t["login_err_wrong"])
                    else:
                        st.error(t["login_err_notfound"])
                except Exception as e:
                    st.error(f"System Error: {e}")
else:
    # --- 4. GIAO DIỆN CHÍNH ---
    selected_lang = st.sidebar.selectbox(t["lang_label"], ["Tiếng Việt", "English"], index=0 if st.session_state.lang == "Tiếng Việt" else 1)
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

    t = translations[st.session_state.lang]

    SUPER_ADMIN_ROLES = ["Quản lý", "Tổng quản lý", "Quản trị viên", "Admin", "Super Admin", "General Manager"]
    SUB_ADMIN_ROLES = ["Quản lý phó", "Phó phòng", "Sub Manager", "Associate/Senior", "Associate", "Senior"]

    role_val = st.session_state.role

    is_super_admin = any(role.lower() == role_val.lower() for role in SUPER_ADMIN_ROLES)
    is_sub_admin = any(role.lower() == role_val.lower() for role in SUB_ADMIN_ROLES)

    if is_super_admin:
        display_role = t["role_super_admin"]
    elif is_sub_admin:
        display_role = t["role_sub_admin"]
    else:
        display_role = t["role_staff"]

    st.sidebar.title(f"{t['hello']}, {st.session_state.name}")
    st.sidebar.info(f"{t['role']}: **{display_role}**")
    if st.sidebar.button(t["logout_btn"]):
        st.session_state.logged_in = False
        st.session_state.name, st.session_state.role, st.session_state.username = "", "", ""
        # Xóa query params khi đăng xuất
        st.query_params.clear()
        st.rerun()

    menu = [
        t["menu_overview"], 
        t["menu_overlap"], 
        t["menu_time_log"], 
        t["menu_change_pw"]
    ]
    
    # Cả General Manager và Associate/Senior đều thấy menu quản lý dự án, giao việc và nhân sự
    if is_super_admin or is_sub_admin:
        menu.insert(1, t["menu_project_mgmt"])
        menu.insert(2, t["menu_add_task"])
        menu.append(t["menu_user_mgmt"])

    choice = st.sidebar.selectbox("Function / Chức năng", menu)
    st.title(t["main_title"])

    # --- HÀM BẢO MẬT: LỌC DỮ LIỆU ĐÚNG THEO PHÂN QUYỀN ---
    def get_scoped_tasks_df():
        res = execute_query(conn.table("tasks").select("*"), ttl=0)
        df_all = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        
        if df_all.empty:
            return pd.DataFrame()
            
        if is_super_admin:
            return df_all
        elif is_sub_admin:
            # Associate/Senior chỉ thấy task do chính họ tạo hoặc được giao cho họ
            if 'created_by' in df_all.columns:
                return df_all[(df_all['created_by'] == st.session_state.name) | (df_all['assignee'] == st.session_state.name)]
            else:
                return df_all[df_all['assignee'] == st.session_state.name]
        else:
            return df_all[df_all['assignee'] == st.session_state.name]

    # --- CHỨC NĂNG: BÁO CÁO TỔNG QUAN ---
    if choice == t["menu_overview"]:
        st.subheader(t["dashboard_title"])
        try:
            df = get_scoped_tasks_df()

            if df.empty:
                st.info(t["no_data"])
            else:
                st.markdown("---")
                
                col_f1, col_f2 = st.columns(2)
                projects_list = [t["all"]] + sorted(df['project'].unique().tolist())
                staff_list_filter = [t["all"]] + sorted(df['assignee'].unique().tolist())

                with col_f1:
                    selected_proj_filter = st.selectbox(t["filter_project"], projects_list)
                with col_f2:
                    selected_staff_filter = st.selectbox(t["filter_staff"], staff_list_filter)

                search_kw = st.text_input("🔍 Tìm kiếm nhanh từ khóa (Tên task, Dự án, Nhân sự):", placeholder="Nhập từ khóa...")

                df_filtered = df.copy()
                if selected_proj_filter != t["all"]:
                    df_filtered = df_filtered[df_filtered['project'] == selected_proj_filter]
                if selected_staff_filter != t["all"]:
                    df_filtered = df_filtered[df_filtered['assignee'] == selected_staff_filter]
                if search_kw.strip():
                    mask = df_filtered.apply(lambda row: row.astype(str).str.contains(search_kw.strip(), case=False).any(), axis=1)
                    df_filtered = df_filtered[mask]

                if df_filtered.empty:
                    st.warning(t["filter_warning"])
                else:
                    if st.session_state.lang == "English":
                        status_map_en = {"Chưa bắt đầu": "Not Started", "Đang làm": "In Progress", "Hoàn thành": "Completed"}
                        df_filtered['status'] = df_filtered['status'].map(status_map_en).fillna(df_filtered['status'])

                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric("Total Projects" if st.session_state.lang == "English" else "Tổng số lượng dự án", df_filtered['project'].nunique())
                    kpi2.metric("Total Hours Spent" if st.session_state.lang == "English" else "Tổng thời gian đã cống hiến", f"{df_filtered['hours_spent'].sum():.1f} hrs" if st.session_state.lang == "English" else f"{df_filtered['hours_spent'].sum():.1f} giờ")
                    completed_count = len(df_filtered[df_filtered['status'].isin(['Hoàn thành', 'Completed'])])
                    kpi3.metric("Completed Tasks" if st.session_state.lang == "English" else "Số việc hoàn thành", f"{completed_count}/{len(df_filtered)}")

                    st.markdown("---")

                    c1, c2 = st.columns(2)
                    with c1:
                        df_bar = df_filtered.groupby('project')['hours_spent'].sum().reset_index()
                        fig_bar = px.bar(df_bar, x='project', y='hours_spent', title="Total Hours by Project" if st.session_state.lang == "English" else "Tổng giờ làm theo từng Dự án", color='project')
                        st.plotly_chart(fig_bar, use_container_width=True)
                    with c2:
                        df_pie = df_filtered['status'].value_counts().reset_index()
                        fig_pie = px.pie(df_pie, names='status', values='count', title="Task Status Distribution" if st.session_state.lang == "English" else "Tỷ trọng trạng thái công việc")
                        st.plotly_chart(fig_pie, use_container_width=True)

                    st.markdown("---")
                    st.write(t["project_progress_title"])
                    proj_progress = []
                    for p in df_filtered['project'].unique():
                        p_df = df_filtered[df_filtered['project'] == p]
                        total_p_tasks = len(p_df)
                        done_p_tasks = len(p_df[p_df['status'].isin(['Hoàn thành', 'Completed'])])
                        pct = int((done_p_tasks / total_p_tasks) * 100) if total_p_tasks > 0 else 0
                        proj_progress.append({"project": p, "progress": pct, "done": done_p_tasks, "total": total_p_tasks})

                    for pp in proj_progress:
                        st.text(f"📁 {pp['project']} ({pp['done']}/{pp['total']} tasks - {pp['progress']}%)")
                        st.progress(pp['progress'] / 100)

                    st.markdown("---")
                    if 'start_date' in df_filtered.columns and 'end_date' in df_filtered.columns:
                        df_gantt = df_filtered.dropna(subset=['start_date', 'end_date'])
                        if not df_gantt.empty:
                            st.write(t["gantt_title"])
                            fig_gantt = px.timeline(
                                df_gantt, 
                                x_start="start_date", 
                                x_end="end_date", 
                                y="task_name", 
                                color="project",
                                hover_name="assignee",
                                title="Timeline of Tasks by Project & Staff"
                            )
                            fig_gantt.update_yaxes(autorange="reversed")
                            st.plotly_chart(fig_gantt, use_container_width=True)

                    st.markdown("---")
                    st.write(t["detailed_task_list"])
                    st.dataframe(df_filtered, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading report: {e}" if st.session_state.lang == "English" else f"Lỗi tải báo cáo: {e}")

    # --- CHỨC NĂNG: QUẢN LÝ DỰ ÁN & NHIỆM VỤ ---
    elif choice == t["menu_project_mgmt"]:
        st.subheader("Project & Task Management" if st.session_state.lang == "English" else "Quản lý Danh mục Dự án & Nhiệm vụ")
        try:
            res_pj = execute_query(conn.table("projects").select("*").order("id", desc=True), ttl=0)
            df_pj = pd.DataFrame(res_pj.data) if res_pj.data else pd.DataFrame()

            # Associate/Senior chỉ thấy các dự án liên quan đến nhiệm vụ do mình tạo, hoặc toàn bộ nếu muốn (hoặc nếu là General Manager)
            if not is_super_admin:
                df_scoped_tasks = get_scoped_tasks_df()
                if not df_scoped_tasks.empty:
                    allowed_projects = df_scoped_tasks['project'].unique().tolist()
                    df_pj = df_pj[df_pj['project_name'].isin(allowed_projects)]

            tab_labels = ["📋 Project List", "✏️ Edit / Delete Project", "🛠️ Task Management"] if st.session_state.lang == "English" else ["📋 Danh sách dự án", "✏️ Sửa / Xóa Dự án", "🛠️ Quản lý Nhiệm vụ"]
            tab_list, tab_edit, tab_tasks = st.tabs(tab_labels)

            with tab_list:
                if not df_pj.empty:
                    search_pj_box = st.text_input("🔍 Tìm kiếm nhanh dự án:", placeholder="Nhập tên dự án...")
                    df_pj_display = df_pj.copy()
                    if search_pj_box.strip():
                        df_pj_display = df_pj_display[df_pj_display['project_name'].str.contains(search_pj_box.strip(), case=False, na=False)]
                    st.dataframe(df_pj_display, use_container_width=True)
                else:
                    st.info("No projects created yet." if st.session_state.lang == "English" else "Chưa có dự án nào được khởi tạo.")
                
                st.markdown("---")
                st.write("➕ **Create New Project:**" if st.session_state.lang == "English" else "➕ **Khởi tạo Dự án mới:**")
                with st.form("create_project_form", clear_on_submit=True):
                    p_name = st.text_input("Project Name" if st.session_state.lang == "English" else "Tên dự án mới", placeholder="e.g. Tower A Project...")
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        start_d = st.date_input("Start Date" if st.session_state.lang == "English" else "Ngày bắt đầu dự án", datetime.now())
                    with col_d2:
                        end_d = st.date_input("Estimated End Date" if st.session_state.lang == "English" else "Ngày kết thúc dự kiến", datetime.now())

                    if st.form_submit_button("Create Project" if st.session_state.lang == "English" else "Tạo Dự án"):
                        if not p_name.strip():
                            st.error("Project name cannot be empty!" if st.session_state.lang == "English" else "Tên dự án không được để trống!")
                        elif start_d > end_d:
                            st.error("Start date cannot be later than end date!" if st.session_state.lang == "English" else "Ngày bắt đầu không được lớn hơn ngày kết thúc dự kiến!")
                        else:
                            check_dup = execute_query(conn.table("projects").select("*").eq("project_name", p_name.strip()), ttl=0)
                            if check_dup.data:
                                st.error(f"⚠️ Cảnh báo trùng lặp: Dự án '{p_name.strip()}' đã tồn tại trên hệ thống!")
                            else:
                                conn.table("projects").insert({
                                    "project_name": p_name.strip(),
                                    "start_date": str(start_d),
                                    "end_date": str(end_d),
                                    "status": "Đang triển khai"
                                }).execute()
                                st.success(f"Successfully created project '{p_name}'!" if st.session_state.lang == "English" else f"Đã tạo thành công dự án '{p_name}'!")
                                st.rerun()

            with tab_edit:
                if df_pj.empty:
                    st.warning("No projects available to edit." if st.session_state.lang == "English" else "Không có dự án nào để chỉnh sửa.")
                else:
                    selected_pj_name = st.selectbox("Select project to edit or delete:" if st.session_state.lang == "English" else "Chọn dự án cần chỉnh sửa hoặc xóa:", df_pj['project_name'].tolist())
                    pj_info = df_pj[df_pj['project_name'] == selected_pj_name].iloc[0]
                    pj_id = int(pj_info['id'])

                    with st.form("update_project_form"):
                        new_p_name = st.text_input("Project Name" if st.session_state.lang == "English" else "Tên dự án", value=pj_info['project_name'])
                        
                        default_start = datetime.strptime(pj_info['start_date'], "%Y-%m-%d").date() if pj_info['start_date'] else datetime.now().date()
                        default_end = datetime.strptime(pj_info['end_date'], "%Y-%m-%d").date() if pj_info['end_date'] else datetime.now().date()
                        
                        c_u1, c_u2 = st.columns(2)
                        with c_u1:
                            new_start_d = st.date_input("Start Date" if st.session_state.lang == "English" else "Ngày bắt đầu", value=default_start)
                        with c_u2:
                            new_end_d = st.date_input("End Date" if st.session_state.lang == "English" else "Ngày kết thúc dự kiến", value=default_end)
                        
                        status_options = ["Đang triển khai", "Tạm dừng", "Hoàn thành"]
                        current_status_idx = status_options.index(pj_info['status']) if pj_info['status'] in status_options else 0
                        new_status = st.selectbox("Project Status" if st.session_state.lang == "English" else "Trạng thái dự án", status_options, index=current_status_idx)

                        submitted_update = st.form_submit_button("Save Changes" if st.session_state.lang == "English" else "Lưu thay đổi dự án")
                        if submitted_update:
                            conn.table("projects").update({
                                "project_name": new_p_name.strip(),
                                "start_date": str(new_start_d),
                                "end_date": str(new_end_d),
                                "status": new_status
                            }).eq("id", pj_id).execute()
                            
                            if new_p_name.strip() != selected_pj_name:
                                conn.table("tasks").update({"project": new_p_name.strip()}).eq("project", selected_pj_name).execute()

                            st.success("Project updated successfully!" if st.session_state.lang == "English" else f"Đã cập nhật thông tin dự án '{new_p_name}' thành công!")
                            st.rerun()

                    st.markdown("---")
                    st.error("⚠️ **Khu vực nguy hiểm (Xóa dự án):**")
                    confirm_delete_proj = st.checkbox("Tôi xác nhận muốn xóa vĩnh viễn dự án này và toàn bộ các nhiệm vụ bên trong.")
                    if confirm_delete_proj:
                        if st.button("🗑️ Xóa vĩnh viễn dự án này"):
                            conn.table("tasks").delete().eq("project", selected_pj_name).execute()
                            conn.table("projects").delete().eq("id", pj_id).execute()
                            st.success(f"Đã xóa vĩnh viễn dự án '{selected_pj_name}' và toàn bộ các nhiệm vụ liên quan!")
                            st.rerun()

            with tab_tasks:
                df_all_tasks = get_scoped_tasks_df()

                if df_all_tasks.empty:
                    st.info("No tasks found in the system." if st.session_state.lang ==
