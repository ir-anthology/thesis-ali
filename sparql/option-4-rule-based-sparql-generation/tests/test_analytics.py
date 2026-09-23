from datetime import timedelta
from pathlib import Path
import shutil
import json
import sqlite3
import uuid

import pytest

from backend.main.analytics import (
    AnalyticsEvent,
    AnalyticsRepository,
    utc_now,
    validate_session_id,
)


SESSION_ID = "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def analytics_path() -> Path:
    directory = Path.cwd() / f".analytics-test-{uuid.uuid4().hex}"
    directory.mkdir()
    try:
        yield directory / "analytics.sqlite3"
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def test_repository_creates_and_persists_conversation_event(analytics_path: Path):
    repository = AnalyticsRepository(analytics_path)
    started = utc_now()
    repository.record(
        AnalyticsEvent(
            session_id=SESSION_ID,
            started_at=started,
            finished_at=started + timedelta(milliseconds=25),
            message="Who are the most prolific authors?",
            history=[{"role": "user", "content": "Hello"}],
            response={"interpretation": "Let me check."},
            outcome="success",
            result_rows=3,
            interaction={
                "type": "cell_click",
                "from_turn_id": "turn-123",
                "details": {"column": "author", "value": "Alice"},
            },
        )
    )

    with sqlite3.connect(analytics_path) as connection:
        event = connection.execute(
            "SELECT session_id, message, history_json, response_json, outcome, result_rows, latency_ms, interaction_json FROM conversation_events"
        ).fetchone()
        session = connection.execute(
            "SELECT request_count FROM sessions WHERE session_id = ?", (SESSION_ID,)
        ).fetchone()

    assert event[0] == SESSION_ID
    assert event[1] == "Who are the most prolific authors?"
    assert '"role": "user"' in event[2]
    assert '"interpretation": "Let me check."' in event[3]
    assert event[4:7] == ("success", 3, 25)
    assert json.loads(event[7]) == {
        "type": "cell_click",
        "from_turn_id": "turn-123",
        "details": {"column": "author", "value": "Alice"},
    }
    assert session == (1,)


def test_session_ids_are_uuid_only():
    assert validate_session_id(SESSION_ID) == SESSION_ID
    assert validate_session_id("not-a-session") is None
    assert validate_session_id("127.0.0.1") is None
    assert validate_session_id(None) is None


def test_cleanup_removes_expired_events_and_orphan_sessions(analytics_path: Path, monkeypatch):
    monkeypatch.setattr("backend.main.analytics.ANALYTICS_RETENTION_DAYS", 30)
    repository = AnalyticsRepository(analytics_path)
    old = utc_now() - timedelta(days=31)
    repository.record(
        AnalyticsEvent(SESSION_ID, old, old, "old", [], {}, "success", 0)
    )

    assert repository.cleanup() == 1

    import sqlite3

    with sqlite3.connect(analytics_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM conversation_events").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 0
