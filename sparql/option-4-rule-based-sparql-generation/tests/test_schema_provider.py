"""Tests for the schema provider."""

import pytest
from backend.main.schema.provider import DBLPSchemaProvider


@pytest.fixture
def schema():
    return DBLPSchemaProvider()


def test_get_schema_contains_classes(schema):
    s = schema.get_schema()
    assert "Article" in s
    assert "Inproceedings" in s
    assert "Creator" in s


def test_get_schema_contains_predicates(schema):
    s = schema.get_schema()
    assert "authoredBy" in s
    assert "creatorName" in s
    assert "title" in s


def test_get_prefixes(schema):
    prefixes = schema.get_prefixes()
    assert "PREFIX dblp:" in prefixes
    assert "PREFIX rdf:" in prefixes
    assert "PREFIX xsd:" in prefixes


def test_get_classes(schema):
    classes = schema.get_classes()
    assert "Article" in classes
    assert "Person" in classes
    assert len(classes) > 10


def test_get_predicates(schema):
    predicates = schema.get_predicates()
    assert "authoredBy" in predicates
    assert "creatorName" in predicates
    assert len(predicates) > 50


def test_limitation_keywords(schema):
    assert "citation" in schema.LIMITATION_KEYWORDS
    assert "abstract" in schema.LIMITATION_KEYWORDS
    assert "h-index" in schema.LIMITATION_KEYWORDS
