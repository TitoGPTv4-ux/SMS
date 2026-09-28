from database import execute_query
import pandas as pd


def add_course(code, name, credits):
    return execute_query(
        "INSERT INTO courses (course_code, course_name, credits) VALUES (%s,%s,%s)",
        (code, name, credits)
    )


def update_course(course_id, code, name, credits):
    return execute_query(
        "UPDATE courses SET course_code=%s, course_name=%s, credits=%s WHERE id=%s",
        (code, name, credits, course_id)
    )


def delete_course(course_id):
    return execute_query("DELETE FROM courses WHERE id=%s", (course_id,))


def get_courses():
    data = execute_query("SELECT * FROM courses ORDER BY course_name", fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def get_course_by_id(course_id):
    return execute_query("SELECT * FROM courses WHERE id=%s", (course_id,), fetchone=True)


def add_programme(code, name, duration_years):
    return execute_query(
        "INSERT INTO programmes (programme_code, programme_name, duration_years) VALUES (%s,%s,%s)",
        (code, name, duration_years)
    )


def update_programme(programme_id, code, name, duration_years):
    return execute_query(
        "UPDATE programmes SET programme_code=%s, programme_name=%s, duration_years=%s WHERE id=%s",
        (code, name, duration_years, programme_id)
    )


def delete_programme(programme_id):
    return execute_query("DELETE FROM programmes WHERE id=%s", (programme_id,))


def get_programmes():
    data = execute_query("SELECT * FROM programmes ORDER BY programme_name", fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def get_programme_by_id(programme_id):
    return execute_query("SELECT * FROM programmes WHERE id=%s", (programme_id,), fetchone=True)


def add_student(reg_no, full_name, email, phone, programme_id, course_id, year_of_study, user_id=None):
    return execute_query(
        "INSERT INTO students (reg_no, full_name, email, phone, programme_id, course_id, year_of_study, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (reg_no, full_name, email, phone, programme_id, course_id, year_of_study, user_id)
    )


def update_student(student_id, reg_no, full_name, email, phone, programme_id, course_id, year_of_study):
    return execute_query(
        "UPDATE students SET reg_no=%s, full_name=%s, email=%s, phone=%s, programme_id=%s, course_id=%s, year_of_study=%s WHERE id=%s",
        (reg_no, full_name, email, phone, programme_id, course_id, year_of_study, student_id)
    )


def delete_student(student_id):
    return execute_query("DELETE FROM students WHERE id=%s", (student_id,))


def get_students(course_id=None):
    query = """
        SELECT s.*, c.course_name, p.programme_name FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        LEFT JOIN programmes p ON s.programme_id = p.id
    """
    params = ()
    if course_id:
        query += " WHERE s.course_id=%s"
        params = (course_id,)
    query += " ORDER BY s.full_name"
    data = execute_query(query, params, fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def get_student_by_id(student_id):
    return execute_query("SELECT * FROM students WHERE id=%s", (student_id,), fetchone=True)


def get_student_by_user(user_id):
    return execute_query("""
        SELECT s.*, c.course_name, p.programme_name FROM students s
        LEFT JOIN courses c ON s.course_id = c.id
        LEFT JOIN programmes p ON s.programme_id = p.id
        WHERE s.user_id=%s
    """, (user_id,), fetchone=True)


def add_teacher(full_name, email, phone, user_id=None):
    return execute_query(
        "INSERT INTO teachers (full_name, email, phone, user_id) VALUES (%s,%s,%s,%s)",
        (full_name, email, phone, user_id)
    )


def update_teacher(teacher_id, full_name, email, phone):
    return execute_query(
        "UPDATE teachers SET full_name=%s, email=%s, phone=%s WHERE id=%s",
        (full_name, email, phone, teacher_id)
    )


def delete_teacher(teacher_id):
    return execute_query("DELETE FROM teachers WHERE id=%s", (teacher_id,))


def get_teachers():
    data = execute_query("SELECT * FROM teachers ORDER BY full_name", fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def get_teacher_by_user(user_id):
    return execute_query("SELECT * FROM teachers WHERE user_id=%s", (user_id,), fetchone=True)


def assign_teacher_course(teacher_id, course_id):
    existing = execute_query(
        "SELECT id FROM teacher_courses WHERE teacher_id=%s AND course_id=%s",
        (teacher_id, course_id), fetchone=True
    )
    if existing:
        return None
    return execute_query(
        "INSERT INTO teacher_courses (teacher_id, course_id) VALUES (%s,%s)",
        (teacher_id, course_id)
    )


def remove_teacher_course(teacher_id, course_id):
    return execute_query(
        "DELETE FROM teacher_courses WHERE teacher_id=%s AND course_id=%s",
        (teacher_id, course_id)
    )


def get_teacher_courses(teacher_id):
    data = execute_query("""
        SELECT c.* FROM courses c
        JOIN teacher_courses tc ON c.id = tc.course_id
        WHERE tc.teacher_id=%s
        ORDER BY c.course_name
    """, (teacher_id,), fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def add_mark(student_id, course_id, exam_name, score, max_score, exam_date, recorded_by):
    return execute_query(
        "INSERT INTO marks (student_id, course_id, exam_name, score, max_score, exam_date, recorded_by) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (student_id, course_id, exam_name, score, max_score, exam_date, recorded_by)
    )


def update_mark(mark_id, score, max_score, exam_name, exam_date):
    return execute_query(
        "UPDATE marks SET score=%s, max_score=%s, exam_name=%s, exam_date=%s WHERE id=%s",
        (score, max_score, exam_name, exam_date, mark_id)
    )


def delete_mark(mark_id):
    return execute_query("DELETE FROM marks WHERE id=%s", (mark_id,))


def get_marks(student_id=None, course_id=None):
    query = """
        SELECT m.*, s.full_name AS student_name, s.reg_no, c.course_name
        FROM marks m
        JOIN students s ON m.student_id = s.id
        JOIN courses c ON m.course_id = c.id
    """
    conditions = []
    params = []
    if student_id:
        conditions.append("m.student_id=%s")
        params.append(student_id)
    if course_id:
        conditions.append("m.course_id=%s")
        params.append(course_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY m.exam_date DESC"
    data = execute_query(query, tuple(params), fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def mark_attendance(student_id, course_id, attendance_date, status, recorded_by):
    existing = execute_query(
        "SELECT id FROM attendance WHERE student_id=%s AND course_id=%s AND attendance_date=%s",
        (student_id, course_id, attendance_date), fetchone=True
    )
    if existing:
        return execute_query(
            "UPDATE attendance SET status=%s, recorded_by=%s WHERE id=%s",
            (status, recorded_by, existing["id"])
        )
    return execute_query(
        "INSERT INTO attendance (student_id, course_id, attendance_date, status, recorded_by) VALUES (%s,%s,%s,%s,%s)",
        (student_id, course_id, attendance_date, status, recorded_by)
    )


def get_attendance(student_id=None, course_id=None):
    query = """
        SELECT a.*, s.full_name AS student_name, s.reg_no, c.course_name
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
    """
    conditions = []
    params = []
    if student_id:
        conditions.append("a.student_id=%s")
        params.append(student_id)
    if course_id:
        conditions.append("a.course_id=%s")
        params.append(course_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY a.attendance_date DESC"
    data = execute_query(query, tuple(params), fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def get_attendance_summary(student_id):
    data = execute_query("""
        SELECT c.course_name,
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present_count,
            SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) AS absent_count,
            COUNT(*) AS total_count
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id=%s
        GROUP BY c.course_name
    """, (student_id,), fetch=True)
    return pd.DataFrame(data) if data else pd.DataFrame()


def get_dashboard_stats():
    students_count = execute_query("SELECT COUNT(*) AS c FROM students", fetchone=True)
    courses_count = execute_query("SELECT COUNT(*) AS c FROM courses", fetchone=True)
    teachers_count = execute_query("SELECT COUNT(*) AS c FROM teachers", fetchone=True)
    marks_count = execute_query("SELECT COUNT(*) AS c FROM marks", fetchone=True)
    return {
        "students": students_count["c"] if students_count else 0,
        "courses": courses_count["c"] if courses_count else 0,
        "teachers": teachers_count["c"] if teachers_count else 0,
        "marks": marks_count["c"] if marks_count else 0
    }