"""Tests for the SPARQL result formatter."""

import pytest
from backend.main.sparql.formatter import format_result_columns, format_result_rows
from backend.main.schemas.context import QueryResult


def test_format_result_columns():
    qr = QueryResult(columns=["author", "pub_count"], rows=[], row_count=0)
    columns = format_result_columns(qr)

    assert len(columns) == 2
    assert columns[0].key == "author"
    assert columns[0].label == "Author"
    assert columns[1].key == "pub_count"
    assert columns[1].label == "Pub Count"


def test_format_result_rows():
    qr = QueryResult(
        columns=["author", "count"],
        rows=[
            {"author": "Geoffrey Hinton", "count": "42"},
            {"author": "Yann LeCun", "count": "35"},
        ],
        row_count=2,
    )
    rows = format_result_rows(qr)

    assert len(rows) == 2
    assert rows[0]["author"].value == "Geoffrey Hinton"
    assert rows[0]["author"].question == ""
    assert rows[0]["count"].value == "42"
    assert rows[1]["author"].value == "Yann LeCun"


def test_format_result_rows_empty():
    qr = QueryResult(columns=["x"], rows=[], row_count=0)
    rows = format_result_rows(qr)
    assert rows == []


def test_format_result_rows_missing_value():
    qr = QueryResult(
        columns=["a", "b"],
        rows=[{"a": "val1"}],
        row_count=1,
    )
    rows = format_result_rows(qr)
    assert rows[0]["a"].value == "val1"
    assert rows[0]["b"].value == ""
