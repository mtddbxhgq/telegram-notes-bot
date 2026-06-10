import sqlite3
from dataclasses import dataclass
from typing import List


@dataclass
class Note:
    id: int
    text: str
    created_at: str


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_note(self, user_id: int, text: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO notes (user_id, text) VALUES (?, ?)",
                (user_id, text),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_notes(self, user_id: int) -> List[Note]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, text, created_at
                FROM notes
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()

        return [
            Note(
                id=row["id"],
                text=row["text"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def delete_note(self, user_id: int, note_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM notes WHERE id = ? AND user_id = ?",
                (note_id, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0