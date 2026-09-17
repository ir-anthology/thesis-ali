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
    assert columns[0].visible is True
    assert columns[0].external_link is False
    assert columns[0].related_column is None
    assert columns[1].visible is True
    assert columns[1].external_link is False
    assert columns[1].related_column is None


def test_format_metadata_columns_and_cell_metadata():
    qr = QueryResult(
        columns=["author_id", "author_name", "publications"],
        rows=[
            {
                "author_id": "https://dblp.org/pid/10/3248",
                "author_name": "Geoffrey Hinton",
                "publications": "42",
            }
        ],
        row_count=1,
    )

    columns = format_result_columns(qr)
    rows = format_result_rows(qr)

    assert {column.key for column in columns if not column.visible} == {"author_id"}
    assert columns[0].external_link is False
    assert rows[0]["author_id"].metadata.entity_id == "https://dblp.org/pid/10/3248"
    assert rows[0]["author_name"].metadata.entity_type == "author"


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


def test_external_identifier_columns_are_visible_links():
    qr = QueryResult(
        columns=["ORCID", "doi", "Issn", "homepage"],
        rows=[
            {
                "ORCID": "https://orcid.org/0000-0001-2345-6789",
                "doi": "10.1000/example",
                "Issn": "1234-5678",
                "homepage": "https://example.org",
            }
        ],
        row_count=1,
    )

    columns = {column.key: column for column in format_result_columns(qr)}

    assert columns["ORCID"].visible is True
    assert columns["ORCID"].external_link is True
    assert columns["ORCID"].related_column is None
    assert columns["doi"].visible is True
    assert columns["doi"].external_link is True
    assert columns["doi"].related_column is None
    assert columns["Issn"].external_link is True
    assert columns["Issn"].related_column is None
    assert columns["homepage"].external_link is False


def test_external_identifiers_map_to_display_columns():
    qr = QueryResult(
        columns=[
            "author_name",
            "author",
            "title",
            "venue_name",
            "orcid",
            "doi",
            "issn",
        ],
        rows=[],
        row_count=0,
    )

    columns = {column.key: column for column in format_result_columns(qr)}

    assert columns["orcid"].related_column == "author_name"
    assert columns["doi"].related_column == "title"
    assert columns["issn"].related_column == "venue_name"


def test_external_identifier_mapping_falls_back_to_generic_entity_column():
    qr = QueryResult(
        columns=["author", "publication", "venue", "orcid", "doi", "issn"],
        rows=[],
        row_count=0,
    )

    columns = {column.key: column for column in format_result_columns(qr)}

    assert columns["orcid"].related_column == "author"
    assert columns["doi"].related_column == "publication"
    assert columns["issn"].related_column == "venue"


def test_unmatched_external_identifier_has_no_related_column():
    qr = QueryResult(columns=["orcid", "count"], rows=[], row_count=0)

    columns = {column.key: column for column in format_result_columns(qr)}

    assert columns["orcid"].related_column is None
    assert columns["count"].related_column is None


def test_result_column_does_not_serialize_role():
    column = format_result_columns(QueryResult(columns=["author"], rows=[], row_count=0))[0]
    assert "role" not in column.model_dump()
    assert "related_column" in column.model_dump()
