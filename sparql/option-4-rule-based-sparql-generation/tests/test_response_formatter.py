"""Tests for response formatter."""

import pytest
from unittest.mock import Mock, patch
from src.response_formatter import ResponseFormatter
from src.models import (
    QueryExecutionResult,
    ColumnDef,
    CellValue,
    FormattedResponse,
)


@pytest.fixture
def formatter():
    return ResponseFormatter()


def test_format_empty_results(formatter):
    execution_result = QueryExecutionResult(
        success=True,
        columns=["pub", "title", "year"],
        rows=[],
        row_count=0,
    )

    result = formatter.format("Test query", execution_result, "Test intent")

    assert result.row_count == 0
    assert len(result.columns) == 3
    assert result.columns[0].key == "pub"
    assert result.columns[0].label == "Pub"
    assert result.rows == []
    assert "No results" in result.query_explanation


def test_format_with_results(formatter):
    execution_result = QueryExecutionResult(
        success=True,
        columns=["author", "title"],
        rows=[
            {"author": "Geoffrey Hinton", "title": "Paper 1"},
            {"author": "Yann LeCun", "title": "Paper 2"},
        ],
        row_count=2,
    )

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content='{"rows": [{"author": {"value": "Geoffrey Hinton", "question": "Tell me about Geoffrey Hinton"}, "title": {"value": "Paper 1", "question": "Tell me about Paper 1"}}, {"author": {"value": "Yann LeCun", "question": "Tell me about Yann LeCun"}, "title": {"value": "Paper 2", "question": "Tell me about Paper 2"}}]}'
            )
        )
    ]

    with patch.object(
        formatter.client.chat.completions, "create", return_value=mock_response
    ):
        result = formatter.format("Test query", execution_result, "Test intent")

    assert result.row_count == 2
    assert len(result.columns) == 2
    assert result.columns[0].key == "author"
    assert result.columns[0].label == "Author"
    assert result.rows[0]["author"].value == "Geoffrey Hinton"
    assert result.rows[0]["author"].question == "Tell me about Geoffrey Hinton"


def test_format_llm_failure(formatter):
    execution_result = QueryExecutionResult(
        success=True,
        columns=["author"],
        rows=[{"author": "Geoffrey Hinton"}],
        row_count=1,
    )

    with patch.object(
        formatter.client.chat.completions,
        "create",
        side_effect=Exception("API Error"),
    ):
        result = formatter.format("Test query", execution_result, "Test intent")

    assert result.row_count == 1
    assert result.rows[0]["author"].value == "Geoffrey Hinton"
    assert result.rows[0]["author"].question == ""


def test_column_label_generation(formatter):
    execution_result = QueryExecutionResult(
        success=True,
        columns=["pub_title", "year_of_publication"],
        rows=[{"pub_title": "Test", "year_of_publication": "2023"}],
        row_count=1,
    )

    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(
                content='{"rows": [{"pub_title": {"value": "Test", "question": "Tell me about Test"}, "year_of_publication": {"value": "2023", "question": "What year?"}}]}'
            )
        )
    ]

    with patch.object(
        formatter.client.chat.completions, "create", return_value=mock_response
    ):
        result = formatter.format("Test query", execution_result, "Test intent")

    assert result.columns[0].label == "Pub Title"
    assert result.columns[1].label == "Year Of Publication"
