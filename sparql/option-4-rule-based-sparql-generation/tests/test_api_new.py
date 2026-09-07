"""Tests for the FastAPI API endpoints (new module structure)."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main.main import app
from backend.main.schemas.responses import ExplorationResponse, ResultColumn, CellValue


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
