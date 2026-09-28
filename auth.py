import bcrypt
from database import execute_query


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def authenticate(username, password):
    user = execute_query("SELECT * FROM users WHERE username=%s", (username,), fetchone=True)
    if user and verify_password(password, user["password"]):
        return user
    return None


def create_user(username, password, role, full_name, email=None, linked_id=None):
    existing = execute_query("SELECT id FROM users WHERE username=%s", (username,), fetchone=True)
    if existing:
        return None
    hashed = hash_password(password)
    return execute_query(
        "INSERT INTO users (username, password, role, full_name, email, linked_id) VALUES (%s,%s,%s,%s,%s,%s)",
        (username, hashed, role, full_name, email, linked_id)
    )


def change_password(user_id, new_password):
    hashed = hash_password(new_password)
    return execute_query("UPDATE users SET password=%s WHERE id=%s", (hashed, user_id))


def get_all_users(role=None):
    if role:
        return execute_query(
            "SELECT id, username, role, full_name, email FROM users WHERE role=%s", (role,), fetch=True
        )
    return execute_query("SELECT id, username, role, full_name, email FROM users", fetch=True)


def delete_user(user_id):
    return execute_query("DELETE FROM users WHERE id=%s", (user_id,))