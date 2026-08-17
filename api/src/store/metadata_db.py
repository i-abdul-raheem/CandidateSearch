import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetadataStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS roles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    department TEXT NOT NULL DEFAULT '',
                    location TEXT NOT NULL DEFAULT '',
                    work_mode TEXT NOT NULL DEFAULT '',
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recent_searches (
                    id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    result_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_roles_updated ON roles(updated_at DESC);
                CREATE INDEX IF NOT EXISTS idx_searches_created ON recent_searches(created_at DESC);
            """)

    def list_roles(self) -> list[dict]:
        with self._connect() as db:
            return [dict(row) for row in db.execute("SELECT * FROM roles ORDER BY updated_at DESC")]

    def create_role(self, data: dict) -> dict:
        role_id, now = uuid.uuid4().hex, _now()
        role = {"id": role_id, **data, "created_at": now, "updated_at": now}
        with self._connect() as db:
            db.execute(
                "INSERT INTO roles VALUES (:id,:title,:department,:location,:work_mode,:description,:status,:created_at,:updated_at)",
                role,
            )
        return role

    def update_role(self, role_id: str, data: dict) -> dict | None:
        current = self.get_role(role_id)
        if current is None:
            return None
        updated = {**current, **data, "updated_at": _now()}
        with self._connect() as db:
            db.execute("""
                UPDATE roles SET title=:title, department=:department, location=:location,
                work_mode=:work_mode, description=:description, status=:status,
                updated_at=:updated_at WHERE id=:id
            """, updated)
        return updated

    def get_role(self, role_id: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM roles WHERE id = ?", (role_id,)).fetchone()
        return dict(row) if row else None

    def delete_role(self, role_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        return cursor.rowcount > 0

    def record_search(self, query: str, result_count: int) -> dict:
        item = {"id": uuid.uuid4().hex, "query": query, "result_count": result_count, "created_at": _now()}
        with self._connect() as db:
            db.execute("INSERT INTO recent_searches VALUES (:id,:query,:result_count,:created_at)", item)
            db.execute("""
                DELETE FROM recent_searches WHERE id NOT IN (
                    SELECT id FROM recent_searches ORDER BY created_at DESC LIMIT 100
                )
            """)
        return item

    def list_searches(self, limit: int = 20) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM recent_searches ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in rows]

    def delete_search(self, search_id: str) -> bool:
        with self._connect() as db:
            cursor = db.execute("DELETE FROM recent_searches WHERE id = ?", (search_id,))
        return cursor.rowcount > 0

    def clear_searches(self) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM recent_searches")
