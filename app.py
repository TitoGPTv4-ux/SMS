import os
print("DEBUG env:", {k: bool(os.environ.get(k)) for k in ["MYSQL_URL", "MYSQLHOST", "MYSQLPORT", "MYSQLUSER", "MYSQLPASSWORD", "MYSQLDATABASE"]}, flush=True)
from config import DB_CONFIG
print("DEBUG DB_CONFIG:", DB_CONFIG["host"], DB_CONFIG["port"], DB_CONFIG["database"], flush=True)
import streamlit as st
import pandas as pd
import base64
import os
from datetime import date
from database import init_database
from auth import authenticate, create_user, get_all_users, delete_user
from styles import apply_styles, page_header, metric_box
from report import build_student_report
import crud

st.set_page_config(page_title="Student Management System", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
apply_styles()


def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def show_centered_logo(width):
    logo_b64 = get_logo_base64()
    st.markdown(
        f'<div style="text-align:center;">'
        f'<img src="data:image/png;base64,{logo_b64}" width="{width}">'
        f'</div>',
        unsafe_allow_html=True,
    )

if "user" not in st.session_state:
    st.session_state.user = None

if "db_initialized" not in st.session_state:
    init_database()
    st.session_state.db_initialized = True


def _login_form(key, allowed_roles, wrong_portal_msg):
    with st.form(f"{key}_login_form"):
        username = st.text_input("Username", key=f"{key}_username")
        password = st.text_input("Password", type="password", key=f"{key}_password")
        submitted = st.form_submit_button("Login", use_container_width=True)
    if submitted:
        username = (username or "").strip()
        if not username or not password:
            st.warning("Enter both username and password")
            return
        user = authenticate(username, password)
        if not user:
            st.error("Invalid username or password")
        elif user["role"] not in allowed_roles:
            st.error(wrong_portal_msg)
        else:
            st.session_state.user = user
            st.rerun()


def login_page():
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            show_centered_logo(220)
            st.markdown('<div class="sms-subtitle">Sign in to continue</div>', unsafe_allow_html=True)
            student_tab, staff_tab = st.tabs(["Student Login", "Staff Login"])
            with student_tab:
                _login_form(
                    "student",
                    ("student",),
                    "This account is not a student account. Please use the Staff Login tab.",
                )
            with staff_tab:
                _login_form(
                    "staff",
                    ("admin", "teacher"),
                    "This is a student account. Please use the Student Login tab.",
                )


def logout():
    st.session_state.user = None
    st.rerun()


def admin_dashboard():
    page_header("Admin Dashboard", "Overview of the entire system")
    stats = crud.get_dashboard_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_box(stats["students"], "Students")
    with col2:
        metric_box(stats["courses"], "Courses")
    with col3:
        metric_box(stats["teachers"], "Teachers")
    with col4:
        metric_box(stats["marks"], "Marks Recorded")


def admin_manage_programmes():
    page_header("Programme Management", "Add, edit or remove academic programmes")
    tab1, tab2 = st.tabs(["Programme List", "Add Programme"])

    with tab1:
        programmes_df = crud.get_programmes()
        st.dataframe(programmes_df, use_container_width=True)
        if not programmes_df.empty:
            selected_id = st.selectbox(
                "Select a programme to edit/delete", programmes_df["id"].tolist(),
                format_func=lambda x: programmes_df[programmes_df["id"] == x]["programme_name"].values[0]
            )
            programme = crud.get_programme_by_id(selected_id)
            with st.form("edit_programme_form"):
                code = st.text_input("Programme Code", value=programme["programme_code"])
                name = st.text_input("Programme Name", value=programme["programme_name"])
                duration = st.number_input("Duration (Years)", min_value=1, max_value=8, value=programme["duration_years"])
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Save Changes", use_container_width=True):
                        crud.update_programme(selected_id, code, name, duration)
                        st.success("Programme updated")
                        st.rerun()
                with col_b:
                    if st.form_submit_button("Delete Programme", use_container_width=True):
                        crud.delete_programme(selected_id)
                        st.success("Programme deleted")
                        st.rerun()

    with tab2:
        with st.form("add_programme_form", clear_on_submit=True):
            code = st.text_input("Programme Code")
            name = st.text_input("Programme Name")
            duration = st.number_input("Duration (Years)", min_value=1, max_value=8, value=3)
            if st.form_submit_button("Add Programme", use_container_width=True):
                new_id = crud.add_programme(code, name, duration)
                if new_id:
                    st.success("Programme added")
                    st.rerun()


def admin_manage_students():
    page_header("Student Management", "Add, edit or remove student records")
    courses_df = crud.get_courses()
    course_options = dict(zip(courses_df["course_name"], courses_df["id"])) if not courses_df.empty else {}
    programmes_df = crud.get_programmes()
    programme_options = dict(zip(programmes_df["programme_name"], programmes_df["id"])) if not programmes_df.empty else {}

    tab1, tab2 = st.tabs(["Student List", "Add Student"])

    with tab1:
        students_df = crud.get_students()
        st.dataframe(students_df, use_container_width=True)
        if not students_df.empty:
            selected_id = st.selectbox(
                "Select a student to edit/delete", students_df["id"].tolist(),
                format_func=lambda x: students_df[students_df["id"] == x]["full_name"].values[0]
            )
            student = crud.get_student_by_id(selected_id)
            with st.form("edit_student_form"):
                reg_no = st.text_input("Reg No", value=student["reg_no"])
                full_name = st.text_input("Full Name", value=student["full_name"])
                email = st.text_input("Email", value=student["email"] or "")
                phone = st.text_input("Phone", value=student["phone"] or "")
                year_of_study = st.number_input("Year of Study", min_value=1, max_value=6, value=student["year_of_study"])
                programme_name = st.selectbox("Programme", list(programme_options.keys()) if programme_options else ["No programme available"])
                course_name = st.selectbox("Course", list(course_options.keys()) if course_options else ["No course available"])
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Save Changes", use_container_width=True):
                        cid = course_options.get(course_name)
                        pid = programme_options.get(programme_name)
                        crud.update_student(selected_id, reg_no, full_name, email, phone, pid, cid, year_of_study)
                        st.success("Student record updated")
                        st.rerun()
                with col_b:
                    if st.form_submit_button("Delete Student", use_container_width=True):
                        crud.delete_student(selected_id)
                        st.success("Student deleted")
                        st.rerun()

    with tab2:
        with st.form("add_student_form", clear_on_submit=True):
            reg_no = st.text_input("Reg No")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            year_of_study = st.number_input("Year of Study", min_value=1, max_value=6, value=1)
            programme_name = st.selectbox("Programme", list(programme_options.keys()) if programme_options else ["No programme available"])
            course_name = st.selectbox("Course", list(course_options.keys()) if course_options else ["No course available"])
            create_login = st.checkbox("Create a login account for this student")
            username = st.text_input("Username (if creating an account)")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Add Student", use_container_width=True):
                cid = course_options.get(course_name)
                pid = programme_options.get(programme_name)
                user_id = None
                if create_login and username and pwd:
                    user_id = create_user(username, pwd, "student", full_name, email)
                new_id = crud.add_student(reg_no, full_name, email, phone, pid, cid, year_of_study, user_id)
                if new_id:
                    st.success("Student added")
                    st.rerun()


def admin_manage_courses():
    page_header("Course Management", "Add, edit or remove courses")
    tab1, tab2 = st.tabs(["Course List", "Add Course"])

    with tab1:
        courses_df = crud.get_courses()
        st.dataframe(courses_df, use_container_width=True)
        if not courses_df.empty:
            selected_id = st.selectbox(
                "Select a course to edit/delete", courses_df["id"].tolist(),
                format_func=lambda x: courses_df[courses_df["id"] == x]["course_name"].values[0]
            )
            course = crud.get_course_by_id(selected_id)
            with st.form("edit_course_form"):
                code = st.text_input("Course Code", value=course["course_code"])
                name = st.text_input("Course Name", value=course["course_name"])
                credits = st.number_input("Credits", min_value=1, max_value=10, value=course["credits"])
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Save Changes", use_container_width=True):
                        crud.update_course(selected_id, code, name, credits)
                        st.success("Course updated")
                        st.rerun()
                with col_b:
                    if st.form_submit_button("Delete Course", use_container_width=True):
                        crud.delete_course(selected_id)
                        st.success("Course deleted")
                        st.rerun()

    with tab2:
        with st.form("add_course_form", clear_on_submit=True):
            code = st.text_input("Course Code")
            name = st.text_input("Course Name")
            credits = st.number_input("Credits", min_value=1, max_value=10, value=3)
            if st.form_submit_button("Add Course", use_container_width=True):
                new_id = crud.add_course(code, name, credits)
                if new_id:
                    st.success("Course added")
                    st.rerun()


def admin_manage_teachers():
    page_header("Teacher Management", "Add teachers and assign them to courses")
    tab1, tab2, tab3 = st.tabs(["Teacher List", "Add Teacher", "Assign Course"])

    with tab1:
        teachers_df = crud.get_teachers()
        st.dataframe(teachers_df, use_container_width=True)
        if not teachers_df.empty:
            selected_id = st.selectbox(
                "Select a teacher to delete", teachers_df["id"].tolist(),
                format_func=lambda x: teachers_df[teachers_df["id"] == x]["full_name"].values[0]
            )
            if st.button("Delete Teacher"):
                crud.delete_teacher(selected_id)
                st.success("Teacher deleted")
                st.rerun()

    with tab2:
        with st.form("add_teacher_form", clear_on_submit=True):
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            username = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.form_submit_button("Add Teacher", use_container_width=True):
                user_id = None
                if username and pwd:
                    user_id = create_user(username, pwd, "teacher", full_name, email)
                new_id = crud.add_teacher(full_name, email, phone, user_id)
                if new_id:
                    st.success("Teacher added")
                    st.rerun()

    with tab3:
        teachers_df = crud.get_teachers()
        courses_df = crud.get_courses()
        if not teachers_df.empty and not courses_df.empty:
            teacher_id = st.selectbox(
                "Teacher", teachers_df["id"].tolist(),
                format_func=lambda x: teachers_df[teachers_df["id"] == x]["full_name"].values[0]
            )
            course_id = st.selectbox(
                "Course", courses_df["id"].tolist(),
                format_func=lambda x: courses_df[courses_df["id"] == x]["course_name"].values[0]
            )
            if st.button("Assign Course to Teacher"):
                result = crud.assign_teacher_course(teacher_id, course_id)
                if result:
                    st.success("Course assigned")
                else:
                    st.warning("Already assigned")
            st.markdown("---")
            assigned = crud.get_teacher_courses(teacher_id)
            st.write("This teacher's courses:")
            st.dataframe(assigned, use_container_width=True)
        else:
            st.info("Make sure there are teachers and courses first")


def record_marks_page(teacher_id):
    page_header("Record Marks", "Enter or edit student marks")
    courses_df = crud.get_courses() if teacher_id is None else crud.get_teacher_courses(teacher_id)
    if courses_df.empty:
        st.info("No courses available")
        return
    course_id = st.selectbox(
        "Select Course", courses_df["id"].tolist(),
        format_func=lambda x: courses_df[courses_df["id"] == x]["course_name"].values[0]
    )
    students_df = crud.get_students(course_id)
    if students_df.empty:
        st.info("No students in this course")
        return
    with st.form("marks_form", clear_on_submit=True):
        student_id = st.selectbox(
            "Student", students_df["id"].tolist(),
            format_func=lambda x: students_df[students_df["id"] == x]["full_name"].values[0]
        )
        exam_name = st.text_input("Exam Name", value="CAT 1")
        score = st.number_input("Score", min_value=0.0, max_value=1000.0, value=0.0)
        max_score = st.number_input("Max Score", min_value=1.0, max_value=1000.0, value=100.0)
        exam_date = st.date_input("Date", value=date.today())
        if st.form_submit_button("Save Mark", use_container_width=True):
            recorded_by = st.session_state.user["id"]
            crud.add_mark(student_id, course_id, exam_name, score, max_score, exam_date, recorded_by)
            st.success("Mark saved")
            st.rerun()
    st.markdown("---")
    marks_df = crud.get_marks(course_id=course_id)
    st.dataframe(marks_df, use_container_width=True)
    if not marks_df.empty:
        mark_id = st.selectbox("Select a record to delete", marks_df["id"].tolist())
        if st.button("Delete Mark Record"):
            crud.delete_mark(mark_id)
            st.success("Record deleted")
            st.rerun()


def attendance_page(teacher_id):
    page_header("Attendance", "Record student attendance")
    courses_df = crud.get_courses() if teacher_id is None else crud.get_teacher_courses(teacher_id)
    if courses_df.empty:
        st.info("No courses available")
        return
    course_id = st.selectbox(
        "Select Course", courses_df["id"].tolist(),
        format_func=lambda x: courses_df[courses_df["id"] == x]["course_name"].values[0], key="att_course"
    )
    students_df = crud.get_students(course_id)
    if students_df.empty:
        st.info("No students in this course")
        return
    attendance_date = st.date_input("Attendance Date", value=date.today())
    st.markdown("### Set Status for Each Student")
    with st.form("attendance_form"):
        statuses = {}
        for _, row in students_df.iterrows():
            statuses[row["id"]] = st.radio(row["full_name"], ["Present", "Absent"], horizontal=True, key=f"att_{row['id']}")
        if st.form_submit_button("Save Attendance", use_container_width=True):
            recorded_by = st.session_state.user["id"]
            for sid, status in statuses.items():
                crud.mark_attendance(sid, course_id, attendance_date, status, recorded_by)
            st.success("Attendance saved")
            st.rerun()
    st.markdown("---")
    att_df = crud.get_attendance(course_id=course_id)
    st.dataframe(att_df, use_container_width=True)


def teacher_dashboard(teacher):
    page_header(f"Welcome, {teacher['full_name']}", "Teacher Dashboard")
    courses_df = crud.get_teacher_courses(teacher["id"])
    col1, col2 = st.columns(2)
    with col1:
        metric_box(len(courses_df), "Courses You Teach")
    with col2:
        total_students = 0
        for cid in courses_df["id"].tolist() if not courses_df.empty else []:
            total_students += len(crud.get_students(cid))
        metric_box(total_students, "Total Students")
    st.markdown("### Your Courses")
    st.dataframe(courses_df, use_container_width=True)


def teacher_students_page(teacher_id):
    page_header("My Students", "List of students in your courses")
    courses_df = crud.get_teacher_courses(teacher_id)
    if courses_df.empty:
        st.info("You have not been assigned any courses yet")
        return
    course_id = st.selectbox(
        "Select Course", courses_df["id"].tolist(),
        format_func=lambda x: courses_df[courses_df["id"] == x]["course_name"].values[0]
    )
    students_df = crud.get_students(course_id)
    st.dataframe(students_df, use_container_width=True)


def student_dashboard(student):
    programme_label = student.get("programme_name") or "No programme assigned"
    page_header(f"Welcome, {student['full_name']}", f"Programme: {programme_label}")
    marks_df = crud.get_marks(student_id=student["id"])
    att_summary = crud.get_attendance_summary(student["id"])
    col1, col2 = st.columns(2)
    with col1:
        metric_box(len(marks_df), "Exams Taken")
    with col2:
        if not att_summary.empty:
            total_present = att_summary["present_count"].sum()
            total_all = att_summary["total_count"].sum()
            pct = round((total_present / total_all) * 100, 1) if total_all else 0
        else:
            pct = 0
        metric_box(f"{pct}%", "Average Attendance")


def student_results_page(student):
    page_header("My Results", "Your marks for each exam")
    marks_df = crud.get_marks(student_id=student["id"])
    if marks_df.empty:
        st.info("No marks recorded yet")
        return
    marks_df["percentage"] = (marks_df["score"].astype(float) / marks_df["max_score"].astype(float) * 100).round(2)
    st.dataframe(marks_df[["course_name", "exam_name", "score", "max_score", "percentage", "exam_date"]], use_container_width=True)
    avg = marks_df["percentage"].mean()
    metric_box(f"{round(avg, 1)}%", "Overall Average")


def student_attendance_page(student):
    page_header("My Attendance", "Summary of your attendance")
    att_summary = crud.get_attendance_summary(student["id"])
    if att_summary.empty:
        st.info("No attendance recorded yet")
        return
    st.dataframe(att_summary, use_container_width=True)
    att_df = crud.get_attendance(student_id=student["id"])
    st.markdown("### Full History")
    st.dataframe(att_df[["course_name", "attendance_date", "status"]], use_container_width=True)


def student_report_page(student):
    page_header("My Report", "Download your full academic report")
    marks_df = crud.get_marks(student_id=student["id"])
    att_summary = crud.get_attendance_summary(student["id"])

    pdf_bytes = build_student_report(student, marks_df, att_summary)
    st.download_button(
        label="📥 Download Report (PDF)",
        data=pdf_bytes,
        file_name=f"report_{student['reg_no'].replace('/', '-')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    if marks_df.empty:
        st.info("No marks recorded yet, so the report will only contain your personal information.")
    else:
        st.markdown("### Preview")
        marks_df["percentage"] = (marks_df["score"].astype(float) / marks_df["max_score"].astype(float) * 100).round(2)
        st.dataframe(
            marks_df[["course_name", "exam_name", "score", "max_score", "percentage", "exam_date"]],
            use_container_width=True,
        )


def admin_manage_users():
    page_header("User Management", "View and manage system accounts")
    users = get_all_users()
    users_df = pd.DataFrame(users) if users else pd.DataFrame()
    st.dataframe(users_df, use_container_width=True)
    if not users_df.empty:
        user_id = st.selectbox(
            "Select a user to delete", users_df["id"].tolist(),
            format_func=lambda x: users_df[users_df["id"] == x]["username"].values[0]
        )
        if st.button("Delete User"):
            delete_user(user_id)
            st.success("User deleted")
            st.rerun()


def sidebar_nav(role):
    st.sidebar.markdown(f"### 👤 {st.session_state.user['full_name']}")
    st.sidebar.markdown(f'<span class="badge-role">{role.upper()}</span>', unsafe_allow_html=True)
    st.sidebar.markdown("---")
    if role == "admin":
        choice = st.sidebar.radio("Menu", ["Dashboard", "Students", "Programmes", "Courses", "Teachers", "Marks", "Attendance", "Users"])
    elif role == "teacher":
        choice = st.sidebar.radio("Menu", ["Dashboard", "My Students", "Marks", "Attendance"])
    else:
        choice = st.sidebar.radio("Menu", ["Dashboard", "Results", "Attendance", "Report"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        logout()
    return choice


def main():
    if st.session_state.user is None:
        login_page()
        return

    role = st.session_state.user["role"]
    choice = sidebar_nav(role)

    if role == "admin":
        if choice == "Dashboard":
            admin_dashboard()
        elif choice == "Students":
            admin_manage_students()
        elif choice == "Programmes":
            admin_manage_programmes()
        elif choice == "Courses":
            admin_manage_courses()
        elif choice == "Teachers":
            admin_manage_teachers()
        elif choice == "Marks":
            record_marks_page(None)
        elif choice == "Attendance":
            attendance_page(None)
        elif choice == "Users":
            admin_manage_users()

    elif role == "teacher":
        teacher = crud.get_teacher_by_user(st.session_state.user["id"])
        if not teacher:
            st.error("This account is not linked to a teacher record")
            return
        if choice == "Dashboard":
            teacher_dashboard(teacher)
        elif choice == "My Students":
            teacher_students_page(teacher["id"])
        elif choice == "Marks":
            record_marks_page(teacher["id"])
        elif choice == "Attendance":
            attendance_page(teacher["id"])

    elif role == "student":
        student = crud.get_student_by_user(st.session_state.user["id"])
        if not student:
            st.error("This account is not linked to a student record")
            return
        if choice == "Dashboard":
            student_dashboard(student)
        elif choice == "Results":
            student_results_page(student)
        elif choice == "Attendance":
            student_attendance_page(student)
        elif choice == "Report":
            student_report_page(student)


if __name__ == "__main__":
    main()