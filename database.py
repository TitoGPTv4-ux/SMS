import os
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import streamlit as st


def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None


def execute_query(query, params=None, fetch=False, fetchone=False):
    conn = get_connection()
    if conn is None:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        if fetchone:
            return cursor.fetchone()
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        st.error(f"Query failed: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def _column_exists(cursor, table, column):
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
    """, (DB_CONFIG["database"], table, column))
    return cursor.fetchone()[0] > 0


def _foreign_key_exists(cursor, table, column):
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        AND REFERENCED_TABLE_NAME IS NOT NULL
    """, (DB_CONFIG["database"], table, column))
    return cursor.fetchone()[0] > 0


def migrate_schema(conn):
    cursor = conn.cursor()

    required_columns = [
        ("students", "programme_id", "INT NULL", "programmes"),
        ("students", "course_id", "INT NULL", "courses"),
        ("students", "user_id", "INT NULL", "users"),
        ("teachers", "user_id", "INT NULL", "users"),
    ]

    for table, column, coltype, ref_table in required_columns:
        try:
            if not _column_exists(cursor, table, column):
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
                conn.commit()
            if not _foreign_key_exists(cursor, table, column):
                cursor.execute(
                    f"ALTER TABLE {table} ADD FOREIGN KEY ({column}) "
                    f"REFERENCES {ref_table}(id) ON DELETE SET NULL"
                )
                conn.commit()
        except Error:
            conn.rollback()

    cursor.close()


def init_database():
    try:
        server_conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        server_cursor = server_conn.cursor()
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}`")
        server_conn.commit()
        server_cursor.close()
        server_conn.close()
    except Error:
        pass

    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            linked_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(20) UNIQUE NOT NULL,
            course_name VARCHAR(150) NOT NULL,
            credits INT DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS programmes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            programme_code VARCHAR(20) UNIQUE NOT NULL,
            programme_name VARCHAR(150) NOT NULL,
            duration_years INT DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            reg_no VARCHAR(30) UNIQUE NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            programme_id INT,
            course_id INT,
            year_of_study INT DEFAULT 1,
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (programme_id) REFERENCES programmes(id) ON DELETE SET NULL,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            phone VARCHAR(20),
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id INT NOT NULL,
            course_id INT NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            exam_name VARCHAR(100) NOT NULL,
            score DECIMAL(6,2) NOT NULL,
            max_score DECIMAL(6,2) NOT NULL DEFAULT 100,
            exam_date DATE,
            recorded_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            attendance_date DATE NOT NULL,
            status VARCHAR(20) NOT NULL,
            recorded_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_attendance (student_id, course_id, attendance_date)
        )
    """)

    conn.commit()
    cursor.close()

    migrate_schema(conn)

    from auth import hash_password
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", ("admin",))
    existing = cursor.fetchone()
    cursor.close()
    if not existing:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password, role, full_name, email) VALUES (%s,%s,%s,%s,%s)",
            ("admin", hash_password("1306"), "admin", "System Administrator", "admin@sms.local")
        )
        conn.commit()
        cursor.close()

    conn.close()