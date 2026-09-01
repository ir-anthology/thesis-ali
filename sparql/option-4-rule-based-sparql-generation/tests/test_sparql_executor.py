"""Tests for SPARQL executor."""

import pytest
from unittest.mock import Mock, patch
from src.sparql_executor import SPARQLExecutor
from src.models import QueryExecutionResult


@pytest.fixture
def executor():
    return SPARQLExecutor()


def test_parse_response(executor):
    data = {
        "head": {"vars": ["pub", "title", "year"]},
        "results": {
            "bindings": [
                {
                    "pub": {"type": "uri", "value": "https://dblp.org/rec/1"},
                    "title": {"type": "literal", "value": "Paper 1"},
                    "year": {"type": "literal", "value": "2023"},
                },
                {
                    "pub": {"type": "uri", "value": "https://dblp.org/rec/2"},
                    "title": {"type": "literal", "value": "Paper 2"},
                    "year": {"type": "literal", "value": "2022"},
                },
            ]
        },
    }

    result = executor._parse_response(data)

    assert result.success is True
    assert result.columns == ["pub", "title", "year"]
    assert result.row_count == 2
    assert result.rows[0]["pub"] == "https://dblp.org/rec/1"
    assert result.rows[0]["title"] == "Paper 1"
    assert result.rows[0]["year"] == "2023"


def test_parse_response_empty(executor):
    data = {
        "head": {"vars": ["pub", "title"]},
        "results": {"bindings": []},
    }

    result = executor._parse_response(data)

    assert result.success is True
    assert result.columns == ["pub", "title"]
    assert result.row_count == 0
    assert result.rows == []


def test_parse_response_missing_column(executor):
    data = {
        "head": {"vars": ["pub", "title", "year"]},
        "results": {
            "bindings": [
                {
                    "pub": {"type": "uri", "value": "https://dblp.org/rec/1"},
                    "title": {"type": "literal", "value": "Paper 1"},
                    # year is missing
                }
            ]
        },
    }

    result = executor._parse_response(data)

    assert result.success is True
    assert result.rows[0]["year"] == ""


def test_execute_http_error(executor):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status = Mock(
        side_effect=Exception("HTTP 400: Bad Request")
    )

    with patch.object(executor.client, "post", return_value=mock_response):
        result = executor.execute("SELECT ?x WHERE { ?x ?y ?z }")

    assert result.success is False
    assert result.error is not None


def test_execute_success(executor):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "head": {"vars": ["x"]},
        "results": {"bindings": [{"x": {"type": "literal", "value": "test"}}]},
    }
    mock_response.raise_for_status = Mock()

    with patch.object(executor.client, "post", return_value=mock_response):
        result = executor.execute("SELECT ?x WHERE { ?x ?y ?z }")

    assert result.success is True
    assert result.columns == ["x"]
    assert result.row_count == 1
