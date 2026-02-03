import sqlite3
from typing import Optional
from .models import UserInDB

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT,
            hashed_password TEXT,
            full_name TEXT,
            disabled INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Initialize on module load
init_db()

def get_user(username: str) -> Optional[UserInDB]:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # allow login by username OR email
    cursor.execute("SELECT username, email, hashed_password, full_name, disabled FROM users WHERE username = ? OR email = ?", (username, username))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UserInDB(
            username=row[0],
            email=row[1],
            hashed_password=row[2],
            full_name=row[3],
            disabled=bool(row[4]) if row[4] else False
        )
    return None

def create_user(user: UserInDB):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password, full_name, disabled) VALUES (?, ?, ?, ?, ?)",
            (user.username, user.email, user.hashed_password, user.full_name, 0)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"User {user.username} already exists.")
    finally:
        conn.close()
    return user
