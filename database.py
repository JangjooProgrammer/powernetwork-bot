import sqlite3
from base import insertinto_accounts
from config import ADMIN_ID, ADMIN_USERNAME

conn = sqlite3.connect("case.db")
cu = conn.cursor()

cu.execute ("""
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY,
        username VARCHAR(55),
        first_name VARCHAR(55),
        admin INTEGER,
        coach INTEGER
    )
""")

cu.execute("""
    CREATE TABLE IF NOT EXISTS form_user_info (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        full_name TEXT NOT NULL,
        city TEXT NOT NULL,
        skills TEXT NOT NULL,
        active_fields TEXT NOT NULL,
        contribution TEXT NOT NULL,
        needed_help TEXT NOT NULL,
        contact TEXT NOT NULL,
        extra_info TEXT,
        status TEXT DEFAULT 'pending',
        coach_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

cu.execute("PRAGMA table_info(accounts)")
columns = [column[1] for column in cu.fetchall()]

if "videos_completed" not in columns:
    cu.execute("""
        ALTER TABLE accounts
        ADD COLUMN videos_completed INTEGER DEFAULT 0
    """)

conn.commit()
conn.close()

insertinto_accounts((ADMIN_ID, ADMIN_USERNAME, "Admin", 1, 0))