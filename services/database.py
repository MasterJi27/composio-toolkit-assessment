"""SQLite persistence for research results."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Optional

from services.config import settings
from services.models import AppRecord


class ResearchDB:
    """Thin SQLite wrapper for checkpoint and recovery."""

    def __init__(self, db_path: Optional[Path] = None):
        self.path = db_path or settings.db_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.path))
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self):
        self.connect().execute("""
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY,
                app TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT DEFAULT '',
                auth TEXT DEFAULT '',
                access TEXT DEFAULT '',
                api TEXT DEFAULT '',
                mcp TEXT DEFAULT '',
                verdict TEXT DEFAULT '',
                evidence TEXT DEFAULT '',
                evidence_grade TEXT DEFAULT '',
                confidence TEXT DEFAULT 'LOW',
                needs_review INTEGER DEFAULT 1,
                composio_supported INTEGER DEFAULT 0,
                composio_tools INTEGER DEFAULT 0,
                composio_managed_auth INTEGER DEFAULT 0,
                composio_demand_rank INTEGER,
                first_pass_auth TEXT DEFAULT '',
                first_pass_access TEXT DEFAULT '',
                first_pass_api TEXT DEFAULT '',
                first_pass_verdict TEXT DEFAULT '',
                source_note TEXT DEFAULT '',
                created_at TEXT DEFAULT ''
            )
        """)
        # Migration: add columns if missing on existing tables
        try:
            cur = self.connect().execute("PRAGMA table_info(apps)")
            cols = {row[1] for row in cur.fetchall()}
            if "composio_managed_auth" not in cols:
                self.connect().execute("ALTER TABLE apps ADD COLUMN composio_managed_auth INTEGER DEFAULT 0")
                self.connect().commit()
            if "evidence_grade" not in cols:
                self.connect().execute("ALTER TABLE apps ADD COLUMN evidence_grade TEXT DEFAULT ''")
                self.connect().commit()
        except sqlite3.Error:
            pass
        self.connect().commit()

    def upsert(self, record: AppRecord):
        self.connect().execute("""
            INSERT OR REPLACE INTO apps VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        """, (
            record.id, record.app, record.category, record.description,
            record.auth, record.access, record.api, record.mcp,
            record.verdict, record.evidence, record.evidence_grade, record.confidence,
            1 if record.needs_review else 0,
            1 if record.composio_supported else 0,
            record.composio_tools,
            1 if record.composio_managed_auth else 0,
            record.composio_demand_rank,
            record.first_pass_auth, record.first_pass_access,
            record.first_pass_api, record.first_pass_verdict,
            record.source_note, record.created_at,
        ))
        self.connect().commit()

    def get(self, app_id: int) -> Optional[AppRecord]:
        cur = self.connect().execute("SELECT * FROM apps WHERE id = ?", (app_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return AppRecord(**dict(row))

    def get_by_name(self, name: str) -> Optional[AppRecord]:
        cur = self.connect().execute("SELECT * FROM apps WHERE app = ?", (name,))
        row = cur.fetchone()
        if row is None:
            return None
        return AppRecord(**dict(row))

    def all(self) -> list[AppRecord]:
        cur = self.connect().execute("SELECT * FROM apps ORDER BY id")
        return [AppRecord(**dict(row)) for row in cur.fetchall()]

    def count(self) -> int:
        cur = self.connect().execute("SELECT COUNT(*) FROM apps")
        return cur.fetchone()[0]

    def needs_review_count(self) -> int:
        cur = self.connect().execute("SELECT COUNT(*) FROM apps WHERE needs_review = 1")
        return cur.fetchone()[0]

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


db = ResearchDB()
