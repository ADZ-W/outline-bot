"""SQLite persistence layer for Outline servers."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from .models import Server


class ServerRepository:
    """Repository for `servers` table operations."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    api_url TEXT NOT NULL,
                    api_secret_encrypted TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def list_servers(self) -> list[Server]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, api_url, api_secret_encrypted, created_at FROM servers ORDER BY id"
            ).fetchall()
        return [self._row_to_server(row) for row in rows]

    def get_server(self, server_id: int) -> Server | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, api_url, api_secret_encrypted, created_at FROM servers WHERE id = ?",
                (server_id,),
            ).fetchone()
        return self._row_to_server(row) if row else None

    def create_server(self, name: str, api_url: str, api_secret_encrypted: str) -> int:
        created_at = datetime.utcnow().isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO servers(name, api_url, api_secret_encrypted, created_at) VALUES (?, ?, ?, ?)",
                (name, api_url, api_secret_encrypted, created_at),
            )
            return int(cur.lastrowid)

    def rename_server(self, server_id: int, new_name: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE servers SET name = ? WHERE id = ?", (new_name, server_id))

    def delete_server(self, server_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM servers WHERE id = ?", (server_id,))

    @staticmethod
    def _row_to_server(row: sqlite3.Row) -> Server:
        return Server(
            id=int(row["id"]),
            name=str(row["name"]),
            api_url=str(row["api_url"]),
            api_secret_encrypted=str(row["api_secret_encrypted"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )
