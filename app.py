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
                    st.info("No tasks found in the system." if st.session_state.lang == "English" else "Chưa có nhiệm vụ nào thuộc quyền quản lý.")
                else:
                    st.write("📋 **Danh sách tất cả nhiệm vụ (Có thể chỉnh sửa hoặc xóa):**")
                    
                    search_task_kw = st.text_input("🔍 Tìm kiếm nhiệm vụ (theo tên task, dự án hoặc nhân sự):", placeholder="Nhập từ khóa...")
                    df_tasks_display = df_all_tasks.copy()
                    if search_task_kw.strip():
                        mask = df_tasks_display.apply(lambda row: row.astype(str).str.contains(search_task_kw.strip(), case=False).any(), axis=1)
                        df_tasks_display = df_tasks_display[mask]

                    if df_tasks_display.empty:
                        st.warning("Không tìm thấy nhiệm vụ phù hợp.")
                    else:
                        task_select_label = df_tasks_display.apply(lambda r: f"[ID: {r['id']}] [{r['project']}] {r['task_name']} ({r['assignee']})", axis=1).tolist()
                        chosen_task_str = st.selectbox("Chọn đầu việc để chỉnh sửa/xóa:", task_select_label)
                        
                        chosen_task_id = int(chosen_task_str.split("]")[0].replace("[ID: ", ""))
                        task_row = df_all_tasks[df_all_tasks['id'] == chosen_task_id].iloc[0]

                        with st.form("edit_single_task_form"):
                            ed_task_name = st.text_input("Tên đầu việc", value=task_row['task_name'])
                            ed_status = st.selectbox("Trạng thái", ["Chưa bắt đầu", "Đang làm", "Hoàn thành"], index=["Chưa bắt đầu", "Đang làm", "Hoàn thành"].index(task_row['status']) if task_row['status'] in ["Chưa bắt đầu", "Đang làm", "Hoàn thành"] else 0)
                            ed_hours = st.number_input("Số giờ đã làm", value=float(task_row['hours_spent']), min_value=0.0, step=0.5)
                            
                            t_start_default = datetime.strptime(task_row['start_date'], "%Y-%m-%d").date() if task_row.get('start_date') else datetime.now().date()
                            t_end_default = datetime.strptime(task_row['end_date'], "%Y-%m-%d").date() if task_row.get('end_date') else datetime.now().date()

                            col_ts1, col_ts2 = st.columns(2)
                            with col_ts1:
                                ed_start_date = st.date_input("Ngày bắt đầu công việc", value=t_start_default)
                            with col_ts2:
                                ed_end_date = st.date_input("Ngày kết thúc dự kiến", value=t_end_default)

                            if st.form_submit_button("Cập nhật nhiệm vụ này"):
                                conn.table("tasks").update({
                                    "task_name": ed_task_name.strip(),
                                    "status": ed_status,
                                    "hours_spent": ed_hours,
                                    "start_date": str(ed_start_date),
                                    "end_date": str(ed_end_date),
                                    "date_updated": datetime.now().strftime("%Y-%m-%d")
                                }).eq("id", chosen_task_id).execute()
                                st.success("Đã cập nhật nhiệm vụ thành công!")
                                st.rerun()

                        st.markdown("---")
                        st.error("⚠️ **Xác nhận xóa nhiệm vụ:**")
                        confirm_delete_task = st.checkbox("Tôi chắc chắn muốn xóa nhiệm vụ này.")
                        if confirm_delete_task:
                            if st.button("🗑️ Xóa vĩnh viễn nhiệm vụ này"):
                                conn.table("tasks").delete().eq("id", chosen_task_id).execute()
                                st.success(f"Đã xóa nhiệm vụ ID: {chosen_task_id} thành công!")
                                st.rerun()

        except Exception as e:
            st.error(f"Lỗi quản lý dự án: {e}")

    # --- CHỨC NĂNG: GIAO VIỆC MỚI ---
    elif choice == t["menu_add_task"]:
        st.subheader("Giao nhiệm vụ cho Nhân viên")
        try:
            res_us = execute_query(conn.table("users").select("name").neq("role", "General Manager"), ttl=0)
            res_pj = execute_query(conn.table("projects").select("project_name").eq("status", "Đang triển khai"), ttl=0)

            staff_list = [u["name"] for u in res_us.data] if res_us.data else []
            project_list = [p["project_name"] for p in res_pj.data] if res_pj.data else []

            if not staff_list:
                st.warning("Chưa có nhân viên nào trên hệ thống. Vui lòng thêm nhân viên trước.")
            elif not project_list:
                st.warning("Chưa có dự án nào đang mở. Vui lòng vào mục 'Quản lý & Cập nhật Dự án' để thêm dự án trước.")
            else:
                with st.form("add_task_form"):
                    project_select = st.selectbox("Chọn Dự án:", project_list)
                    task_title = st.text_input("Tên đầu việc cần xử lý", placeholder="e.g. Foundation Design...")
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
                            dup_check = execute_query(
                                conn.table("tasks")
                                .select("*")
                                .eq("project", project_select)
                                .eq("task_name", task_title.strip())
                                .eq("assignee", assignee_select),
                                ttl=0
                            )
                            if dup_check.data:
                                st.error(f"⚠️ **Cảnh báo trùng lặp:** Nhân viên **{assignee_select}** đã được giao đầu việc **'{task_title.strip()}'** trong dự án **[{project_select}]** rồi!")
                            else:
                                conn.table("tasks").insert({
                                    "project": project_select,
                                    "task_name": task_title.strip(),
                                    "assignee": assignee_select,
                                    "status": "Chưa bắt đầu",
                                    "hours_spent": 0.0,
                                    "date_updated": datetime.now().strftime("%Y-%m-%d"),
                                    "start_date": str(task_start),
                                    "end_date": str(task_end),
                                    "created_by": st.session_state.name
                                }).execute()
                                st.success(f"Đã giao việc '{task_title}' cho {assignee_select} thuộc dự án [{project_select}]!")
                                st.rerun()
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")

    # --- CHỨC NĂNG: PHÂN TÍCH CHỒNG CHÉO ---
    elif choice == t["menu_overlap"]:
        st.subheader("Phân tích Tải công việc & Sự chồng chéo Dự án của Nhân sự")
        try:
            df_tasks = get_scoped_tasks_df()
            if not df_tasks.empty:
                df_tasks = df_tasks[df_tasks['status'] != "Hoàn thành"]

            if df_tasks.empty:
                st.info("Hiện không có công việc nào đang dở dang hoặc chưa bắt đầu thuộc quyền quản lý của bạn.")
            else:
                col_of1, col_of2 = st.columns(2)
                p_options_ol = [t["all"]] + sorted(df_tasks['project'].unique().tolist())
                s_options_ol = [t["all"]] + sorted(df_tasks['assignee'].unique().tolist())

                with col_of1:
                    sel_p_ol = st.selectbox(t["filter_project"], p_options_ol, key="ol_p")
                with col_of2:
                    sel_s_ol = st.selectbox(t["filter_staff"], s_options_ol, key="ol_s")

                df_tasks_filtered = df_tasks.copy()
                if sel_p_ol != t["all"]:
                    df_tasks_filtered = df_tasks_filtered[df_tasks_filtered['project'] == sel_p_ol]
                if sel_s_ol != t["all"]:
                    df_tasks_filtered = df_tasks_filtered[df_tasks_filtered['assignee'] == sel_s_ol]

                if df_tasks_filtered.empty:
                    st.warning("Không có dữ liệu phù hợp với bộ lọc.")
                else:
                    df_user_projects = df_tasks_filtered.groupby('assignee')['project'].nunique().reset_index()
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
                                staff_name = row['Nhân sự']
                                proj_count = row['Số lượng Dự án đang phụ trách']
                                st.error(f"🚨 **{staff_name}** đang tham gia **{proj_count} dự án** cùng lúc!")
                                user_pjs = df_tasks[df_tasks['assignee'] == staff_name]['project'].unique()
                                st.write(f"👉 Các dự án: *{', '.join(user_pjs)}*")
                        else:
                            st.success("✅ Hiện không có nhân sự nào bị phân bổ hơn 1 dự án đồng thời.")

                    st.markdown("---")
                    st.write("🔍 **Ma trận phân bổ Đầu việc theo Nhân sự & Dự án:**")
                    pivot_df = pd.pivot_table(
                        df_tasks_filtered, 
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
    elif choice == t["menu_time_log"]:
        st.subheader("Cập nhật báo cáo tiến độ công việc hàng ngày")
        try:
            df_display = get_scoped_tasks_df()

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
                    status_options_list = ["Chưa bắt đầu", "Đang làm", "Hoàn thành"]
                    current_st = df_display.iloc[task_index]['status']
                    idx = status_options_list.index(current_st) if current_st in status_options_list else 0
                    status_update = st.selectbox("Cập nhật trạng thái thực tế:", status_options_list, index=idx)
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

    # --- CHỨC NĂNG: ĐỔI MẬT KHẨU CÁ NHÂN ---
    elif choice == t["menu_change_pw"]:
        st.subheader("Đổi Mật khẩu Tài khoản")
        with st.form("change_password_form"):
            old_pw = st.text_input("Mật khẩu hiện tại", type="password")
            new_pw = st.text_input("Mật khẩu mới", type="password")
            confirm_pw = st.text_input("Xác nhận mật khẩu mới", type="password")
            
            submit_pw = st.form_submit_button("Xác nhận đổi mật khẩu")
            
            if submit_pw:
                if not old_pw or not new_pw or not confirm_pw:
                    st.error("Vui lòng điền đầy đủ thông tin!")
                elif new_pw != confirm_pw:
                    st.error("Mật khẩu mới và xác nhận mật khẩu không khớp!")
                else:
                    try:
                        res_user = execute_query(conn.table("users").select("*").eq("username", st.session_state.username), ttl=0)
                        if res_user.data:
                            current_db_pw = str(res_user.data[0]["password"])
                            if current_db_pw != old_pw:
                                st.error("Mật khẩu hiện tại không chính xác!")
                            else:
                                conn.table("users").update({"password": new_pw}).eq("username", st.session_state.username).execute()
                                st.success("Đổi mật khẩu thành công!")
                        else:
                            st.error("Không tìm thấy thông tin tài khoản.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- CHỨC NĂNG: QUẢN LÝ NHÂN SỰ ---
    elif choice == t["menu_user_mgmt"]:
        st.subheader("Quản lý nhân sự")
        try:
            res_users = execute_query(conn.table("users").select("username, name, role"), ttl=0)
            df_users = pd.DataFrame(res_users.data) if res_users.data else pd.DataFrame()

            if not df_users.empty:
                search_user_box = st.text_input("🔍 Tìm kiếm tài khoản nhân sự:", placeholder="Nhập tên hoặc username...")
                df_users_display = df_users.copy()
                if search_user_box.strip():
                    mask_u = df_users_display.apply(lambda row: row.astype(str).str.contains(search_user_box.strip(), case=False).any(), axis=1)
                    df_users_display = df_users_display[mask_u]
                st.dataframe(df_users_display, use_container_width=True)

            if not df_users.empty and is_super_admin:
                st.markdown("---")
                st.write("✏️ **Cập nhật / Sửa vai trò nhân sự (Chỉ General Manager):**")
                with st.form("update_user_role_form"):
                    selected_target_user = st.selectbox("Chọn tài khoản cần đổi vai trò:", df_users["username"].tolist())
                    
                    current_role_val = df_users[df_users["username"] == selected_target_user]["role"].values[0]
                    role_options_list = ["Nhân viên", "Associate/Senior", "General Manager"]
                    curr_idx = role_options_list.index(current_role_val) if current_role_val in role_options_list else 0
                    
                    new_assigned_role = st.selectbox("Chọn vai trò mới:", role_options_list, index=curr_idx)

                    if st.form_submit_button("Lưu thay đổi vai trò"):
                        conn.table("users").update({"role": new_assigned_role}).eq("username", selected_target_user).execute()
                        st.success(f"Đã cập nhật vai trò của tài khoản '{selected_target_user}' thành '{new_assigned_role}' thành công!")
                        st.rerun()

            st.markdown("---")
            st.write("➕ **Thêm tài khoản nhân sự mới:**")
            with st.form("add_user_form", clear_on_submit=True):
                new_username = st.text_input("Tài khoản (viết liền không dấu)")
                new_password = st.text_input("Mật khẩu", type="password")
                new_name = st.text_input("Họ và tên")
                new_role = st.selectbox("Vai trò", ["Nhân viên", "Associate/Senior"])

                if st.form_submit_button("Tạo tài khoản"):
                    clean_new_username = new_username.strip().lower()
                    if not clean_new_username or not new_password or not new_name.strip():
                        st.error("Vui lòng điền đầy đủ thông tin!")
                    elif not df_users.empty and clean_new_username in df_users["username"].str.lower().tolist():
                        st.error("Tài khoản này đã tồn tại!")
                    else:
                        # Kiểm tra trùng lặp tên đầy đủ nhân viên
                        check_name = execute_query(conn.table("users").select("*").ilike("name", new_name.strip()), ttl=0)
                        if check_name.data:
                            st.warning(f"⚠️ Lưu ý: Nhân sự có tên '{new_name.strip()}' đã tồn tại trên hệ thống!")
                        
                        conn.table("users").insert({
                            "username": clean_new_username,
                            "password": new_password,
                            "name": new_name.strip(),
                            "role": new_role
                        }).execute()
                        st.success(f"Đã tạo tài khoản '{clean_new_username}'!")
                        st.rerun()

            if is_super_admin:
                st.markdown("---")
                st.error("⚠️ **Xóa tài khoản (Chỉ General Manager):**")
                if not df_users.empty:
                    del_options = [u for u in df_users["username"].tolist() if u != st.session_state.username]
                    if del_options:
                        del_user = st.selectbox("Chọn tài khoản cần xóa", del_options)
                        confirm_del_user = st.checkbox("Tôi xác nhận muốn xóa tài khoản này.")
                        if confirm_del_user:
                            if st.button("Xóa tài khoản"):
                                conn.table("users").delete().eq("username", del_user).execute()
                                st.success(f"Đã xóa tài khoản '{del_user}'!")
                                st.rerun()
                    else:
                        st.info("Không có tài khoản nào khác để xóa.")
        except Exception as e:
            st.error(f"Lỗi quản lý nhân sự: {e}")
