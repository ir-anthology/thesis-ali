"""Privacy-aware conversation analytics backed by SQLite.

Analytics failures are intentionally isolated from request handling.  The
store contains only pseudonymous session identifiers and application data;
request metadata such as IP addresses and authorization headers is never
accepted by this module.
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from backend.main.config import ANALYTICS_DB_PATH, ANALYTICS_RETENTION_DAYS

logger = logging.getLogger(__name__)

_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
INACTIVITY_TIMEOUT = timedelta(minutes=30)


@dataclass(frozen=True)
class AnalyticsEvent:
    session_id: str
    started_at: datetime
    finished_at: datetime
    message: str
    history: list[dict[str, Any]]
    response: dict[str, Any]
    outcome: str
    result_rows: int | None
    error_category: str | None = None


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def validate_session_id(value: str | None) -> str | None:
    if not value or not _UUID_RE.fullmatch(value):
        return None
    try:
        UUID(value)
    except ValueError:
        return None
    return value.lower()


class AnalyticsRepository:
    """Small SQLite repository for anonymous conversation events."""

    def __init__(self, db_path: Path | str = ANALYTICS_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        self._initialize()
        self.cleanup()

    def _connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_path, timeout=30)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    first_activity_at TEXT NOT NULL,
                    last_activity_at TEXT NOT NULL,
                    request_count INTEGER NOT NULL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS conversation_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    history_json TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    result_rows INTEGER,
                    error_category TEXT,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                );

                CREATE INDEX IF NOT EXISTS idx_events_session
                    ON conversation_events(session_id);
                CREATE INDEX IF NOT EXISTS idx_events_started
                    ON conversation_events(started_at);
                """
            )

    def record(self, event: AnalyticsEvent) -> None:
        started = event.started_at.isoformat()
        finished = event.finished_at.isoformat()
        latency_ms = max(0, round((event.finished_at - event.started_at).total_seconds() * 1000))
        with self._lock:
            with self._connect() as connection:
                existing = connection.execute(
                    "SELECT first_activity_at FROM sessions WHERE session_id = ?",
                    (event.session_id,),
                ).fetchone()
                if existing is None:
                    connection.execute(
                        "INSERT INTO sessions(session_id, first_activity_at, last_activity_at, request_count) VALUES (?, ?, ?, 1)",
                        (event.session_id, started, finished),
                    )
                else:
                    first = min(existing["first_activity_at"], started)
                    connection.execute(
                        "UPDATE sessions SET first_activity_at = ?, last_activity_at = ?, request_count = request_count + 1 WHERE session_id = ?",
                        (first, finished, event.session_id),
                    )
                connection.execute(
                    """INSERT INTO conversation_events(
                        session_id, started_at, finished_at, latency_ms, message,
                        history_json, response_json, outcome, result_rows, error_category
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        event.session_id,
                        started,
                        finished,
                        latency_ms,
                        event.message,
                        json.dumps(event.history, ensure_ascii=False),
                        json.dumps(event.response, ensure_ascii=False),
                        event.outcome,
                        event.result_rows,
                        event.error_category,
                    ),
                )

    def cleanup(self, now: datetime | None = None) -> int:
        if ANALYTICS_RETENTION_DAYS is None:
            return 0
        cutoff = (now or utc_now()) - timedelta(days=ANALYTICS_RETENTION_DAYS)
        with self._lock:
            with self._connect() as connection:
                cursor = connection.execute(
                    "DELETE FROM conversation_events WHERE started_at < ?",
                    (cutoff.isoformat(),),
                )
                connection.execute(
                    "DELETE FROM sessions WHERE session_id NOT IN (SELECT DISTINCT session_id FROM conversation_events)"
                )
                return cursor.rowcount


def safe_record(repository: AnalyticsRepository, event: AnalyticsEvent) -> None:
    """Persist an event without allowing analytics to affect the API."""
    try:
        repository.record(event)
    except Exception:
        logger.exception("Analytics persistence failed")
