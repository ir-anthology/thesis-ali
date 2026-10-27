"""SUS API contract, durable storage, and correlation with session metrics."""

import json
import sqlite3
from dataclasses import replace
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from backend.main.analytics import (
    AnalyticsEvent,
    AnalyticsRepository,
    FeedbackEvent,
    SUSSubmission,
    utc_now,
)
from backend.main.main import app

SESSION_ID = "123e4567-e89b-12d3-a456-426614174000"
ANSWERS = [4, 2, 4, 1, 5, 2, 4, 1, 4, 2]
PAYLOAD = {"questionnaire": "SUS", "version": "brooke-1996", "answers": ANSWERS}


@pytest.fixture
def repository(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.main.analytics.ANALYTICS_RETENTION_DAYS", None)
    repository = AnalyticsRepository(tmp_path / "analytics.sqlite3")
    monkeypatch.setattr("backend.main.api.sus._analytics", repository)
    return repository


@pytest.fixture
def client(repository):
    with TestClient(app) as client:
        yield client


@pytest.mark.parametrize("analytics_enabled", [None, "false"])
def test_submission_is_committed_with_session_and_server_metadata(
    client, repository, analytics_enabled
):
    headers = {"X-Session-Id": SESSION_ID.upper()}
    if analytics_enabled is not None:
        headers["X-Analytics-Enabled"] = analytics_enabled
    started_at = utc_now()

    response = client.post("/api/sus", json=PAYLOAD, headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert set(data) == {"status", "submission_id"}
    assert data["status"] == "accepted"
    assert UUID(data["submission_id"]).version == 4
    reopened = AnalyticsRepository(repository.db_path)
    with sqlite3.connect(reopened.db_path) as connection:
        row = connection.execute(
            "SELECT * FROM sus_submissions WHERE submission_id = ?",
            (data["submission_id"],),
        ).fetchone()
        assert connection.execute("SELECT COUNT(*) FROM sessions").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM conversation_events").fetchone() == (0,)
    assert row[:3] == (data["submission_id"], "SUS", "brooke-1996")
    assert json.loads(row[3]) == ANSWERS
    assert row[4:6] == (82.5, SESSION_ID)
    submitted_at = datetime.fromisoformat(row[6])
    assert submitted_at.utcoffset() == timedelta(0)
    assert started_at <= submitted_at <= utc_now()


@pytest.mark.parametrize(
    ("answers", "score"),
    [
        ([1, 5] * 5, 0.0),
        ([5, 1] * 5, 100.0),
        ([3] * 10, 50.0),
        (ANSWERS, 82.5),
    ],
)
def test_score_and_answers_are_preserved(client, repository, answers, score):
    response = client.post("/api/sus", json={**PAYLOAD, "answers": answers})

    assert response.status_code == 201
    with sqlite3.connect(repository.db_path) as connection:
        raw_answers, stored_score, session_id = connection.execute(
            "SELECT answers_json, sus_score, session_id FROM sus_submissions"
        ).fetchone()
    assert json.loads(raw_answers) == answers
    assert stored_score == score
    assert session_id is None


@pytest.mark.parametrize(
    "payload",
    [
        {},
        [],
        {"version": "brooke-1996", "answers": ANSWERS},
        {"questionnaire": "SUS", "answers": ANSWERS},
        {"questionnaire": "SUS", "version": "brooke-1996"},
        {**PAYLOAD, "questionnaire": "sus"},
        {**PAYLOAD, "version": "other"},
        {**PAYLOAD, "answers": ANSWERS[:9]},
        {**PAYLOAD, "answers": ANSWERS + [3]},
        {**PAYLOAD, "answers": None},
        {**PAYLOAD, "answers": "3333333333"},
        {**PAYLOAD, "answers": [0] + ANSWERS[1:]},
        {**PAYLOAD, "answers": [6] + ANSWERS[1:]},
        {**PAYLOAD, "answers": [True] + ANSWERS[1:]},
        {**PAYLOAD, "answers": [False] + ANSWERS[1:]},
        {**PAYLOAD, "answers": [4.0] + ANSWERS[1:]},
        {**PAYLOAD, "answers": [4.5] + ANSWERS[1:]},
        {**PAYLOAD, "answers": ["4"] + ANSWERS[1:]},
        {**PAYLOAD, "answers": [None] + ANSWERS[1:]},
        {**PAYLOAD, "history": []},
        {**PAYLOAD, "name": "participant"},
        {**PAYLOAD, "sus_score": 100},
    ],
)
def test_invalid_questionnaires_return_400_without_writing(client, repository, payload):
    response = client.post("/api/sus", json=payload)

    assert response.status_code == 400
    with sqlite3.connect(repository.db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sus_submissions").fetchone() == (0,)


@pytest.mark.parametrize("body", ["", "{invalid json", "null"])
def test_malformed_or_missing_json_returns_400(client, body):
    response = client.post(
        "/api/sus", content=body, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 400


@pytest.mark.parametrize("session_id", ["", "temporary-session-id", "127.0.0.1"])
def test_invalid_supplied_session_returns_400(client, repository, session_id):
    response = client.post(
        "/api/sus", json=PAYLOAD, headers={"X-Session-Id": session_id}
    )

    assert response.status_code == 400
    with sqlite3.connect(repository.db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sus_submissions").fetchone() == (0,)


def test_repeated_submissions_have_distinct_ids(client, repository):
    responses = [
        client.post("/api/sus", json=PAYLOAD, headers={"X-Session-Id": SESSION_ID})
        for _ in range(2)
    ]

    assert all(response.status_code == 201 for response in responses)
    assert responses[0].json()["submission_id"] != responses[1].json()["submission_id"]
    with sqlite3.connect(repository.db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sus_submissions").fetchone() == (2,)


def test_storage_failure_returns_500_and_retry_can_succeed(client, repository):
    with sqlite3.connect(repository.db_path) as connection:
        connection.execute(
            """CREATE TRIGGER reject_sus BEFORE INSERT ON sus_submissions
               BEGIN SELECT RAISE(ABORT, 'simulated storage failure'); END"""
        )

    response = client.post("/api/sus", json=PAYLOAD)

    assert response.status_code == 500
    assert "simulated storage failure" not in response.text
    with sqlite3.connect(repository.db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM sus_submissions").fetchone() == (0,)
        connection.execute("DROP TRIGGER reject_sus")
    assert client.post("/api/sus", json=PAYLOAD).status_code == 201


def _record_existing_metrics(repository):
    now = utc_now()
    event = AnalyticsEvent(
        session_id=SESSION_ID,
        started_at=now,
        finished_at=now,
        message="Show authors",
        history=[],
        response={},
        outcome="success",
        result_rows=1,
    )
    repository.record(event)
    repository.record(event)
    repository.record_feedback(FeedbackEvent(SESSION_ID, "answer-1", "positive", now))


def test_sus_joins_existing_metrics_without_incrementing_conversation_count(
    client, repository
):
    _record_existing_metrics(repository)

    assert client.post(
        "/api/sus", json=PAYLOAD, headers={"X-Session-Id": SESSION_ID.upper()}
    ).status_code == 201

    with sqlite3.connect(repository.db_path) as connection:
        row = connection.execute(
            """SELECT sus.sus_score, conversations.total, feedback.total,
                      sessions.request_count
               FROM sus_submissions AS sus
               JOIN sessions USING (session_id)
               JOIN (SELECT session_id, COUNT(*) AS total FROM conversation_events
                     GROUP BY session_id) AS conversations USING (session_id)
               JOIN (SELECT session_id, COUNT(*) AS total FROM answer_feedback
                     GROUP BY session_id) AS feedback USING (session_id)"""
        ).fetchone()
    assert row == (82.5, 2, 1, 2)


def test_existing_database_gains_sus_table_without_changing_metrics(repository):
    _record_existing_metrics(repository)
    with sqlite3.connect(repository.db_path) as connection:
        connection.execute("DROP TABLE sus_submissions")

    AnalyticsRepository(repository.db_path)

    with sqlite3.connect(repository.db_path) as connection:
        assert connection.execute("SELECT request_count FROM sessions").fetchone() == (2,)
        assert connection.execute("SELECT COUNT(*) FROM conversation_events").fetchone() == (2,)
        assert connection.execute("SELECT COUNT(*) FROM answer_feedback").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM sus_submissions").fetchone() == (0,)
        columns = {
            row[1] for row in connection.execute("PRAGMA table_info(sus_submissions)")
        }
    assert columns == {
        "submission_id", "questionnaire", "version", "answers_json",
        "sus_score", "session_id", "submitted_at",
    }


@pytest.mark.parametrize("retention_days", [None, 30])
def test_sus_retention_matches_analytics_policy(repository, monkeypatch, retention_days):
    monkeypatch.setattr("backend.main.analytics.ANALYTICS_RETENTION_DAYS", retention_days)
    now = utc_now()
    recent = SUSSubmission(
        submission_id=str(uuid4()),
        questionnaire="SUS",
        version="brooke-1996",
        answers=ANSWERS,
        sus_score=82.5,
        session_id=None,
        submitted_at=now,
    )
    old = replace(recent, submission_id=str(uuid4()), submitted_at=now - timedelta(days=31))
    repository.record_sus(recent)
    repository.record_sus(old)

    assert repository.cleanup(now=now) == 0

    with sqlite3.connect(repository.db_path) as connection:
        ids = {row[0] for row in connection.execute("SELECT submission_id FROM sus_submissions")}
    assert ids == ({recent.submission_id, old.submission_id} if retention_days is None else {recent.submission_id})


def test_cors_allows_session_header(client):
    response = client.options(
        "/api/sus",
        headers={
            "Origin": "https://demo.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-session-id",
        },
    )

    assert response.status_code == 200
    assert "x-session-id" in response.headers["access-control-allow-headers"].lower()


def test_sus_validation_status_is_local_and_documented(client):
    assert client.post("/api/feedback", json={}).status_code == 422
    operation = client.get("/openapi.json").json()["paths"]["/api/sus"]["post"]
    assert {"201", "400", "500"} <= operation["responses"].keys()
    assert "422" not in operation["responses"]
