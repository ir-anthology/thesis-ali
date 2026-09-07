"""Tests for the SPARQL validator (new module structure)."""

import pytest
from backend.main.sparql.validator import SPARQLValidator


@pytest.fixture
def validator():
    return SPARQLValidator()


def test_valid_query(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?title WHERE {
  ?pub dblp:authoredBy <https://dblp.org/pid/10/3248> .
  ?pub dblp:title ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert len(result.errors) == 0


def test_empty_query(validator):
    result = validator.validate("")
    assert result.valid is False
    assert "empty" in result.errors[0].lower()


def test_missing_select(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
?pub ?title WHERE {
  ?pub dblp:title ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is False
    assert any("SELECT" in e for e in result.errors)


def test_missing_braces(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?title"""
    result = validator.validate(sparql)
    assert result.valid is False
    assert any("braces" in e.lower() for e in result.errors)


def test_unbalanced_braces(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?title WHERE {
  ?pub dblp:title ?title ."""
    result = validator.validate(sparql)
    assert result.valid is False
    assert any("unbalanced" in e.lower() for e in result.errors)


def test_missing_prefix(validator):
    sparql = """SELECT ?pub ?title WHERE {
  ?pub dblp:title ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is False
    assert any("prefix" in e.lower() for e in result.errors)


def test_unknown_predicate(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?title WHERE {
  ?pub dblp:unknownPredicate ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is False
    assert any("unknown" in e.lower() for e in result.errors)


def test_unknown_class(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub WHERE {
  ?pub a dblp:UnknownClass .
}"""
    result = validator.validate(sparql)
    assert result.valid is False
    assert any("unknown" in e.lower() for e in result.errors)


def test_select_star_warning(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT * WHERE {
  ?pub dblp:title ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert any("SELECT *" in w for w in result.warnings)


def test_missing_limit_warning(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?title WHERE {
  ?pub dblp:title ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert any("limit" in w.lower() for w in result.warnings)
