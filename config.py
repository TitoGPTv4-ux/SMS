import os
from urllib.parse import urlparse
import streamlit as st

RAILWAY_NAMES = {
    "host": "MYSQLHOST",
    "user": "MYSQLUSER",
    "password": "MYSQLPASSWORD",
    "database": "MYSQLDATABASE",
    "port": "MYSQLPORT"
}


def _from_url(key):
    url = os.getenv("MYSQL_URL") or os.getenv("DATABASE_URL")
    if not url:
        return None
    parsed = urlparse(url)
    values = {
        "host": parsed.hostname,
        "port": parsed.port,
        "user": parsed.username,
        "password": parsed.password,
        "database": parsed.path.lstrip("/")
    }
    return values.get(key)


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
    value = _from_url(key)
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
