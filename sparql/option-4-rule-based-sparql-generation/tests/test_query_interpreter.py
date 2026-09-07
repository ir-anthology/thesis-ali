"""Tests for query interpreter."""

import pytest
from unittest.mock import Mock, patch
from src.models import QueryInterpretation, EntityMention, Constraints
from src.query_interpreter import QueryInterpreter


@pytest.fixture
def interpreter():
    return QueryInterpreter()


def test_clear_outcome(interpreter):
    mock_result = QueryInterpretation(
        outcome="clear",
        intent="Let me find the papers by Geoffrey Hinton",
        entities_mentioned=[EntityMention(text="Geoffrey Hinton", type_hint="Person")],
        constraints=Constraints(),
    )

    with patch.object(
        interpreter.client.responses,
        "parse",
        return_value=Mock(output_parsed=mock_result),
    ):
        result = interpreter.interpret("Which papers did Geoffrey Hinton author?")

    assert result.outcome == "clear"
    assert "Geoffrey Hinton" in result.intent
    assert len(result.entities_mentioned) == 1
    assert result.entities_mentioned[0].text == "Geoffrey Hinton"


def test_ambiguous_outcome(interpreter):
    mock_result = QueryInterpretation(
        outcome="ambiguous",
        intent="The user is asking for publications by an author named Smith",
        entities_mentioned=[EntityMention(text="Smith", type_hint="Person")],
        constraints=Constraints(),
        clarification="There are multiple authors named Smith in DBLP. Which one did you mean?",
        options=[
            "Show me papers by John Smith",
            "Show me papers by Mike Smith",
            "Show me papers by Sarah Smith",
        ],
    )

    with patch.object(
        interpreter.client.responses,
        "parse",
        return_value=Mock(output_parsed=mock_result),
    ):
        result = interpreter.interpret("papers by Smith")

    assert result.outcome == "ambiguous"
    assert result.clarification is not None
    assert len(result.options) == 3


def test_out_of_scope_outcome(interpreter):
    mock_result = QueryInterpretation(
        outcome="out_of_scope",
        intent="The user is asking about citation counts",
        entities_mentioned=[],
        constraints=Constraints(),
        limitation="DBLP does not track citation counts. Consider using Semantic Scholar or Google Scholar.",
        suggestions=[
            "How many publications does this author have?",
            "Show me papers by this author",
        ],
    )

    with patch.object(
        interpreter.client.responses,
        "parse",
        return_value=Mock(output_parsed=mock_result),
    ):
        result = interpreter.interpret("How many citations does this paper have?")

    assert result.outcome == "out_of_scope"
    assert result.limitation is not None
    assert len(result.suggestions) == 2


def test_llm_returns_none(interpreter):
    with patch.object(
        interpreter.client.responses, "parse", return_value=Mock(output_parsed=None)
    ):
        result = interpreter.interpret("test query")

    assert result.outcome == "out_of_scope"
    assert result.limitation is not None
    assert len(result.suggestions) > 0


def test_llm_error(interpreter):
    with patch.object(
        interpreter.client.responses, "parse", side_effect=Exception("API Error")
    ):
        result = interpreter.interpret("test query")

    assert result.outcome == "out_of_scope"
    assert result.limitation is not None
    assert len(result.suggestions) > 0


def test_with_history(interpreter):
    from src.models import HistoryTurn

    history = [
        HistoryTurn(role="user", content="Which papers did Geoffrey Hinton author?"),
        HistoryTurn(
            role="assistant", content="Let me find the papers by Geoffrey Hinton"
        ),
    ]

    mock_result = QueryInterpretation(
        outcome="clear",
        intent="Let me find papers from 2023 by Geoffrey Hinton",
        entities_mentioned=[EntityMention(text="Geoffrey Hinton", type_hint="Person")],
        constraints=Constraints(year="2023"),
    )

    with patch.object(
        interpreter.client.responses,
        "parse",
        return_value=Mock(output_parsed=mock_result),
    ):
        result = interpreter.interpret("Only from 2023", history)

    assert result.outcome == "clear"
    assert result.constraints.year == "2023"


def test_outcome_values(interpreter):
    """Test that outcome is one of the valid values."""
    for outcome in ["clear", "ambiguous", "out_of_scope"]:
        mock_result = QueryInterpretation(
            outcome=outcome,
            intent="Test intent",
            entities_mentioned=[],
            constraints=Constraints(),
        )

        with patch.object(
            interpreter.client.responses,
            "parse",
            return_value=Mock(output_parsed=mock_result),
        ):
            result = interpreter.interpret("test query")

        assert result.outcome == outcome
