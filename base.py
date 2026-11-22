from aiogram import types

user_key = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="راهنما")]
    ],
    resize_keyboard=True
)

registration_key = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="ثبت نام"),
         types.KeyboardButton(text="عضویت در گروه")],
        [types.KeyboardButton(text="اقدام برای کوچ")],
        [types.KeyboardButton(text="راهنما")]
    ],
    resize_keyboard=True
)

manager_key = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="لیست کوچ ها")],
            [types.KeyboardButton(text="آمار ربات 📊"), types.KeyboardButton(text="ارسال پیام همگانی 📢")],
            [types.KeyboardButton(text="لیست کاربران 👥"), types.KeyboardButton(text="ارسال اطلاعات کوچی برای کوچ")]
        ],
        resize_keyboard=True
    )

def get_user_by_id(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (user_id,)
    )

    result = cu.fetchone()

    conn.close()
    return result

def get_admin_id():
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute("SELECT id FROM accounts WHERE admin = 1")
    result = cu.fetchone()

    conn.close()
    return result

def get_all_users():
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("SELECT * FROM accounts")
    result = cu.fetchall()

    db.close()
    return result


def get_user_count():
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("SELECT COUNT(*) FROM accounts")
    result = cu.fetchone()[0]

    db.close()
    return result

def insertinto_accounts(data: tuple):
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("""
        INSERT OR IGNORE INTO accounts
        (id, username, first_name, admin, coach)
        VALUES (?, ?, ?, ?, ?)
    """, data)

    db.commit()
    db.close()
    
def save_form_info(user_id: int, data: dict):
    import sqlite3

    with sqlite3.connect("case.db") as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT request_id FROM form_user_info WHERE user_id=? ORDER BY request_id DESC LIMIT 1",
            (user_id,)
        )
        result = cursor.fetchone()

        values = (
            data["full_name"], data["city"], data["skills"],
            data["active_fields"], data["contribution"],
            data["needed_help"], data["contact"], data["extra_info"]
        )

        if result:
            cursor.execute("""
                UPDATE form_user_info SET
                full_name=?, city=?, skills=?, active_fields=?,
                contribution=?, needed_help=?, contact=?, extra_info=?
                WHERE request_id=?
            """, (*values, result[0]))
        else:
            cursor.execute("""
                INSERT INTO form_user_info
                (user_id, full_name, city, skills, active_fields,
                 contribution, needed_help, contact, extra_info, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'not_requested')
            """, (user_id, *values))
            
def submit_coach_request(user_id: int):
    import sqlite3
    with sqlite3.connect("case.db") as db:
        cu = db.cursor()
        cu.execute("""
            SELECT request_id, status
            FROM form_user_info
            WHERE user_id = ?
            ORDER BY request_id DESC
            LIMIT 1
        """, (user_id,))
        result = cu.fetchone()
        if result is None:
            return "no_form"
        request_id, status = result
        if status == "pending":
            return "already_pending"
        if status == "assigned":
            return "already_assigned"
        if status == "completed":
            return "completed"
        if status != "not_requested":
            return "invalid_status"
        cu.execute("""
            UPDATE form_user_info
            SET status = 'pending'
            WHERE request_id = ?
        """, (request_id,))
        return "submitted"
    
def set_videos_completed(user_id: int):
    import sqlite3

    with sqlite3.connect("case.db") as db:
        db.execute("""
            UPDATE accounts
            SET videos_completed = 1
            WHERE id = ?
        """, (user_id,))

def has_completed_videos(user_id: int):
    import sqlite3

    with sqlite3.connect("case.db") as db:
        result = db.execute("""
            SELECT videos_completed
            FROM accounts
            WHERE id = ?
        """, (user_id,)).fetchone()

        return bool(result and result[0])
    
def inline_url_maker(list1, list2):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=name, url=callback)]
        for name, callback in zip(list1, list2)
    ])
    return keyboard

def inline_query_maker(list1, list2):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=name, callback_data=callback)]
        for name, callback in zip(list1, list2)
    ])
    return keyboard

def get_all_coaches():
    import sqlite3

    with sqlite3.connect("case.db") as db:
        return db.execute(
            "SELECT id, username, first_name FROM accounts WHERE coach = 1"
        ).fetchall()


def add_coach(user_id: int):
    import sqlite3

    with sqlite3.connect("case.db") as db:
        cursor = db.execute(
            "UPDATE accounts SET coach = 1 WHERE id = ?",
            (user_id,)
        )
        return cursor.rowcount > 0


def remove_coach(user_id: int):
    import sqlite3

    with sqlite3.connect("case.db") as db:
        cursor = db.execute(
            "UPDATE accounts SET coach = 0 WHERE id = ?",
            (user_id,)
        )
        return cursor.rowcount > 0
    
def get_non_coaches():
    import sqlite3

    with sqlite3.connect("case.db") as db:
        return db.execute("""
            SELECT id, username, first_name
            FROM accounts
            WHERE coach = 0 AND admin = 0
        """).fetchall()
        
def get_pending_requests():
    import sqlite3
    with sqlite3.connect("case.db") as db:
        return db.execute("""
            SELECT request_id, user_id, full_name, city
            FROM form_user_info
            WHERE status='pending'
            ORDER BY created_at ASC
        """).fetchall()

def get_form_request(request_id: int):
    import sqlite3
    with sqlite3.connect("case.db") as db:
        return db.execute("""
            SELECT * FROM form_user_info
            WHERE request_id=?
        """, (request_id,)).fetchone()

def assign_coach(request_id: int, coach_id: int):
    import sqlite3
    with sqlite3.connect("case.db") as db:
        coach = db.execute(
            "SELECT id FROM accounts WHERE id=? AND coach=1",
            (coach_id,)
        ).fetchone()

        if not coach:
            return False

        cursor = db.execute("""
            UPDATE form_user_info
            SET status='assigned', coach_id=?
            WHERE request_id=? AND status='pending'
        """, (coach_id, request_id))

        return cursor.rowcount > 0


FORM_FIELD_LABELS = [
    ("full_name", "نام و نام خانوادگی"),
    ("city", "شهر"),
    ("skills", "مهارت‌ها"),
    ("active_fields", "حوزه‌های فعالیت"),
    ("contribution", "میزان مشارکت"),
    ("needed_help", "کمک مورد نیاز"),
    ("contact", "راه ارتباطی"),
    ("extra_info", "توضیحات اضافه"),
]


def get_member_publish_data(user_id: int):
    import sqlite3

    column_names = [column for column, _ in FORM_FIELD_LABELS]

    with sqlite3.connect("case.db") as db:
        row = db.execute(f"""
            SELECT {", ".join(column_names)}
            FROM form_user_info
            WHERE user_id = ?
            ORDER BY request_id DESC
            LIMIT 1
        """, (user_id,)).fetchone()

    if row is None:
        return None

    data = dict(zip(column_names, row))

    fields = [
        (label, data[column])
        for column, label in FORM_FIELD_LABELS
        if data[column] is not None and str(data[column]).strip() != ""
    ]

    return {"fields": fields, "name": data["full_name"], "contact": data["contact"]}


def has_form(user_id: int):
    import sqlite3

    with sqlite3.connect("case.db") as db:
        return db.execute(
            "SELECT 1 FROM form_user_info WHERE user_id = ? LIMIT 1",
            (user_id,)
        ).fetchone() is not None
