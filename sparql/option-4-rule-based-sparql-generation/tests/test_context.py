"""Tests for the context builder and exploration context."""

import pytest
from backend.main.context.builder import ContextBuilder
from backend.main.schemas.requests import ChatRequest, HistoryTurn
from backend.main.schemas.context import ExplorationContext, QueryResult
from backend.main.schemas.llm import Interpretation
from backend.main.schemas.responses import ResultColumn, CellValue


@pytest.fixture
def builder():
    return ContextBuilder()


def test_build_initial_context(builder):
    request = ChatRequest(message="Who are the most prolific authors?", history=[])
    ctx = builder.build(request)

    assert ctx.user_message == "Who are the most prolific authors?"
    assert ctx.history == []
    assert ctx.dblp_schema is not None
    assert "DBLP" in ctx.dblp_schema
    assert ctx.interpretation is None
    assert ctx.sparql_query is None
    assert ctx.query_result is None


def test_build_context_with_history(builder):
    history = [
        HistoryTurn(role="user", content="Show me papers by Geoffrey Hinton"),
        HistoryTurn(
            role="assistant",
            content="Here are the papers",
            interpretation="Let me find papers by Geoffrey Hinton",
        ),
    ]
    request = ChatRequest(message="Only from 2023", history=history)
    ctx = builder.build(request)

    assert len(ctx.history) == 2
    assert ctx.history[0].role == "user"
    assert ctx.history[1].role == "assistant"


def test_context_enrichment():
    ctx = ExplorationContext(user_message="test")

    # C1
    interp = Interpretation(
        summary="test query",
        scope="in_scope",
        entities=["Geoffrey Hinton"],
    )
    ctx.set_interpretation(interp)
    assert ctx.interpretation is not None
    assert ctx.interpretation.scope == "in_scope"

    # C2
    ctx.set_sparql("SELECT ?x WHERE { ?x ?y ?z }")
    assert ctx.sparql_query is not None

    query_result = QueryResult(
        columns=["x"],
        rows=[{"x": "value1"}],
        row_count=1,
    )
    ctx.set_query_result(query_result)
    assert ctx.query_result.row_count == 1

    # C3
    columns = [ResultColumn(key="x", label="X")]
    rows = [{"x": CellValue(value="value1", question="Tell me about value1")}]
    ctx.set_result_table(columns, rows)
    assert len(ctx.result_columns) == 1
    assert len(ctx.result_rows) == 1

    ctx.set_observations(["Test observation"])
    assert len(ctx.observations) == 1

    # C4
    ctx.set_suggestions(["Follow-up question?"])
    assert len(ctx.suggestions) == 1


def test_context_schema():
    ctx = ExplorationContext(user_message="test")
    ctx.set_schema("test schema")
    assert ctx.dblp_schema == "test schema"
