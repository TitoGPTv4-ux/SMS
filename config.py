import os
import streamlit as st

RAILWAY_NAMES = {
    "host": "MYSQLHOST",
    "user": "MYSQLUSER",
    "password": "MYSQLPASSWORD",
    "database": "MYSQLDATABASE",
    "port": "MYSQLPORT"
}


def _get(key, default):
    try:
        if "mysql" in st.secrets and key in st.secrets["mysql"]:
            return st.secrets["mysql"][key]
    except Exception:
        pass
    value = os.getenv("DB_" + key.upper())
    if value:
        return value
    value = os.getenv(RAILWAY_NAMES[key])
    if value:
        return value
    return default


DB_CONFIG = {
    "host": _get("host", "localhost"),
    "user": _get("user", "root"),
    "password": _get("password", ""),
    "database": _get("database", "student_management_system"),
    "port": int(_get("port", 3306))
}

APP_NAME = "Student Management System"