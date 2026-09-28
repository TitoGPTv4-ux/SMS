import os
import streamlit as st


def _get(key, default):
    try:
        if "mysql" in st.secrets and key in st.secrets["mysql"]:
            return st.secrets["mysql"][key]
    except Exception:
        pass
    return os.getenv("DB_" + key.upper(), default)


DB_CONFIG = {
    "host": _get("host", "localhost"),
    "user": _get("user", "root"),
    "password": _get("password", ""),
    "database": _get("database", "SMS"),
    "port": int(_get("port", 3306))
}

APP_NAME = "SMS"