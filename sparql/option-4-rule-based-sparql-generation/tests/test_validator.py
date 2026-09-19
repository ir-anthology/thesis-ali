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
}
LIMIT 1"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert len(result.errors) == 0


def test_known_class_with_a_is_not_treated_as_predicate(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub WHERE {
  ?pub a dblp:Publication .
}
LIMIT 1"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert result.errors == []


def test_known_class_with_rdf_type_is_not_treated_as_predicate(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?pub WHERE {
  ?pub rdf:type dblp:Publication .
}
LIMIT 1"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert result.errors == []


def test_class_name_in_predicate_position_is_rejected(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub WHERE {
  ?pub dblp:Publication ?value .
}"""
    result = validator.validate(sparql)
    assert result.valid is False
    assert "Unknown predicate: dblp:Publication" in result.errors


def test_jasist_query_with_known_classes_is_valid(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT DISTINCT ?publication_id ?title WHERE {
  ?publication_id a dblp:Publication ;
    dblp:title ?title ;
    dblp:publishedInStream ?venue_id .
  ?venue_id a dblp:Journal ;
    dblp:primaryStreamTitle ?venue_name .
  FILTER(CONTAINS(LCASE(STR(?venue_name)), "jasist"))
}
LIMIT 15"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert result.errors == []


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
}
LIMIT 1"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert any("SELECT *" in w for w in result.warnings)


def test_missing_limit_is_valid_for_non_aggregate_query(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?pub ?title WHERE {
  ?pub dblp:title ?title .
    }"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert result.errors == []


def test_missing_limit_is_valid_for_single_aggregate_query(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT (COUNT(DISTINCT ?pub) AS ?publications) WHERE {
  ?pub a dblp:Publication .
}"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert result.errors == []


def test_complete_result_query_without_limit_is_valid(validator):
    sparql = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT DISTINCT ?pub ?title WHERE {
  ?pub a dblp:Publication .
  ?pub dblp:title ?title .
}"""
    result = validator.validate(sparql)
    assert result.valid is True
    assert result.errors == []
