import sqlite3
from config import DATABASE_PATH


def init_db() -> None:
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                note_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, note_id)
            )
        """)
        conn.commit()

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()