import os
from urllib.parse import urlparse

APP_NAME = "Student Management System"


def _build_db_config():
    url = os.environ.get("MYSQL_URL") or os.environ.get("MYSQL_PUBLIC_URL")
    if url:
        p = urlparse(url)
        return {
            "host": p.hostname,
            "port": p.port or 3306,
            "user": p.username,
            "password": p.password or "",
            "database": (p.path or "/railway").lstrip("/") or "railway",
        }
    return {
        "host": os.environ.get("MYSQLHOST") or os.environ.get("MYSQL_HOST") or "localhost",
        "port": int(os.environ.get("MYSQLPORT") or os.environ.get("MYSQL_PORT") or 3306),
        "user": os.environ.get("MYSQLUSER") or os.environ.get("MYSQL_USER") or "root",
        "password": os.environ.get("MYSQLPASSWORD") or os.environ.get("MYSQL_PASSWORD") or "",
        "database": os.environ.get("MYSQLDATABASE") or os.environ.get("MYSQL_DATABASE") or "railway",
    }


DB_CONFIG = _build_db_config()