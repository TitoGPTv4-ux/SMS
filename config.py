import os

DB_CONFIG = {
    "host": os.environ.get("MYSQLHOST") or os.environ.get("MYSQL_HOST") or "localhost",
    "port": int(os.environ.get("MYSQLPORT") or os.environ.get("MYSQL_PORT") or 3306),
    "user": os.environ.get("MYSQLUSER") or os.environ.get("MYSQL_USER") or "root",
    "password": os.environ.get("MYSQLPASSWORD") or os.environ.get("MYSQL_PASSWORD") or "",
    "database": os.environ.get("MYSQLDATABASE") or os.environ.get("MYSQL_DATABASE") or "railway",
}
