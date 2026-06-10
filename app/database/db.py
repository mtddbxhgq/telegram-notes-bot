import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from cryptography.fernet import Fernet

from config import FERNET_KEY


LOCAL_TIMEZONE = ZoneInfo("Europe/Kyiv")
MAX_NOTES_PER_USER = 100


@dataclass
class Note:
    note_id: int
    text: str
    created_at: str


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.cipher = Fernet(FERNET_KEY.encode())

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _encrypt_text(self, text: str) -> str:
        return self.cipher.encrypt(text.encode("utf-8")).decode("utf-8")

    def _decrypt_text(self, encrypted_text: str) -> str:
        return self.cipher.decrypt(encrypted_text.encode("utf-8")).decode("utf-8")

    def init_db(self) -> None:
        with self._connect() as conn:
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

    def get_notes_count(self, user_id: int) -> int:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) AS notes_count
                FROM notes
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        return int(row["notes_count"])

    def _get_next_note_id(self, conn: sqlite3.Connection, user_id: int) -> int:
        row = conn.execute(
            """
            SELECT MAX(note_id) AS max_note_id
            FROM notes
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

        max_note_id = row["max_note_id"]

        if max_note_id is None:
            return 1

        return int(max_note_id) + 1

    def add_note(self, user_id: int, text: str) -> int:
        created_at = datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        encrypted_text = self._encrypt_text(text)

        with self._connect() as conn:
            note_id = self._get_next_note_id(conn, user_id)

            conn.execute(
                """
                INSERT INTO notes (user_id, note_id, text, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, note_id, encrypted_text, created_at),
            )
            conn.commit()

        return note_id

    def get_notes(self, user_id: int) -> List[Note]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT note_id, text, created_at
                FROM notes
                WHERE user_id = ?
                ORDER BY note_id ASC
                """,
                (user_id,),
            ).fetchall()

        notes = []

        for row in rows:
            decrypted_text = self._decrypt_text(row["text"])

            notes.append(
                Note(
                    note_id=row["note_id"],
                    text=decrypted_text,
                    created_at=row["created_at"],
                )
            )

        return notes

    def delete_note(self, user_id: int, note_id: int) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                DELETE FROM notes
                WHERE user_id = ? AND note_id = ?
                """,
                (user_id, note_id),
            )
            conn.commit()
            return cursor.rowcount > 0