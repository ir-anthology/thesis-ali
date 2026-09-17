"""Tests for the FastAPI API endpoints (new module structure)."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main.main import app
from backend.main.schemas.responses import ExplorationResponse, ResultColumn, CellValue
from backend.main.schemas.requests import ChatRequest


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


def test_exploration_endpoint_success(client):
    mock_response = ExplorationResponse(
        interpretation="Let me find the papers by Geoffrey Hinton",
        columns=[
            ResultColumn(key="pub", label="Pub", type="text"),
            ResultColumn(key="title", label="Title", type="text"),
        ],
        rows=[
            {
                "pub": CellValue(
                    value="https://dblp.org/rec/1",
                    question="Tell me about this publication",
                ),
                "title": CellValue(value="Paper 1", question="Tell me about Paper 1"),
            }
        ],
        observations=["Geoffrey Hinton has published many papers."],
        suggestions=["Show me Geoffrey Hinton's publications from 2023"],
        sparql_query="PREFIX dblp: ...",
    )

    with patch(
        "backend.main.api.exploration._service.explore",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        response = client.post(
            "/api/exploration",
            json={"message": "Which papers did Geoffrey Hinton author?", "history": []},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["interpretation"] == "Let me find the papers by Geoffrey Hinton"
    assert len(data["columns"]) == 2
    assert len(data["rows"]) == 1
    assert len(data["observations"]) == 1
    assert len(data["suggestions"]) == 1


def test_exploration_endpoint_out_of_scope(client):
    mock_response = ExplorationResponse(
        interpretation="DBLP does not track citation counts.",
        suggestions=["Show me Geoffrey Hinton's publications"],
    )

    with patch(
        "backend.main.api.exploration._service.explore",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        response = client.post(
            "/api/exploration",
            json={"message": "How many citations does this paper have?", "history": []},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["interpretation"] == "DBLP does not track citation counts."
    assert data["columns"] is None
    assert data["rows"] is None


def test_exploration_endpoint_ambiguous(client):
    mock_response = ExplorationResponse(
        interpretation="There are multiple authors named Smith. Which one did you mean?",
        suggestions=[
            "Show me papers by John Smith",
            "Show me papers by Mike Smith",
        ],
    )

    with patch(
        "backend.main.api.exploration._service.explore",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        response = client.post(
            "/api/exploration",
            json={"message": "papers by Smith", "history": []},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["interpretation"] is not None
    assert "Smith" in data["interpretation"]
    assert data["suggestions"] == [
        "Show me papers by John Smith",
        "Show me papers by Mike Smith",
    ]


def test_exploration_endpoint_error(client):
    with patch(
        "backend.main.api.exploration._service.explore",
        new_callable=AsyncMock,
        side_effect=Exception("API Error"),
    ):
        response = client.post(
            "/api/exploration",
            json={"message": "test query", "history": []},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["interpretation"] is not None
    assert "error occurred" in data["interpretation"].lower()


def test_exploration_endpoint_with_history(client):
    mock_response = ExplorationResponse(
        interpretation="Let me find papers by Geoffrey Hinton from 2023",
        columns=[
            ResultColumn(key="title", label="Title", type="text"),
        ],
        rows=[
            {
                "title": CellValue(value="Paper 1", question="Tell me about Paper 1"),
            }
        ],
        suggestions=["Show me publications from 2022"],
        sparql_query="PREFIX dblp: ...",
    )

    history = [
        {"role": "user", "content": "Which papers did Geoffrey Hinton author?"},
        {
            "role": "assistant",
            "content": "Let me find the papers by Geoffrey Hinton",
            "interpretation": "Let me find the papers by Geoffrey Hinton",
        },
    ]

    with patch(
        "backend.main.api.exploration._service.explore",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        response = client.post(
            "/api/exploration",
            json={"message": "Only from 2023", "history": history},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["interpretation"] == "Let me find papers by Geoffrey Hinton from 2023"


def test_exploration_stream_endpoint_emits_ordered_events(client):
    async def fake_stream(_request):
        yield {"event": "interpretation", "data": {"text": "Understanding"}}
        yield {"event": "sparql", "data": {"query": "SELECT * WHERE {}"}}
        yield {"event": "result", "data": {"columns": [], "rows": []}}
        yield {"event": "suggestions", "data": {"items": ["Try again"]}}
        yield {"event": "complete", "data": {}}

    with patch(
        "backend.main.api.exploration._service.explore_stream",
        side_effect=fake_stream,
    ):
        response = client.post(
            "/api/exploration/stream",
            json={"message": "test query", "history": []},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    event_names = [
        line.removeprefix("event: ")
        for line in body.splitlines()
        if line.startswith("event:")
    ]
    assert event_names == [
        "interpretation",
        "sparql",
        "result",
        "suggestions",
        "complete",
    ]


def test_exploration_stream_endpoint_reports_pipeline_errors(client):
    async def failing_stream(_request):
        yield {"event": "interpretation", "data": {"text": "Understanding"}}
        raise RuntimeError("pipeline failed")

    with patch(
        "backend.main.api.exploration._service.explore_stream",
        side_effect=failing_stream,
    ):
        response = client.post(
            "/api/exploration/stream",
            json={"message": "test query", "history": []},
        )

    assert response.status_code == 200
    assert "event: error" in response.text
    assert "pipeline failed" not in response.text


def test_chat_request_accepts_direct_entity_interaction():
    request = ChatRequest(
        message="Show this author's publications",
        interaction={
            "entity_id": "https://dblp.org/pid/10/3248",
            "entity_type": "author",
        },
    )

    assert request.interaction is not None
    assert request.interaction.entity_id.endswith("10/3248")


def test_chat_request_rejects_non_dblp_entity_id():
    with pytest.raises(ValueError):
        ChatRequest(
            message="Show this entity",
            interaction={"entity_id": "https://example.com/entity"},
        )
