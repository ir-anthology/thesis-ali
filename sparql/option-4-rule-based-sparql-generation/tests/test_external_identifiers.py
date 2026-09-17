from unittest.mock import Mock

import pytest

from backend.main.schemas.context import ExplorationContext, QueryResult
from backend.main.schemas.llm import Interpretation, SPARQLGeneration
from backend.main.services.exploration import ExplorationService
from backend.main.sparql.external_identifiers import extend_with_external_identifier
from backend.main.sparql.validator import SPARQLValidator


def test_author_grouping_adds_optional_orcid():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?author_name (COUNT(?publication) AS ?count)
WHERE {
  ?publication dblp:authoredBy ?author .
  ?author dblp:primaryCreatorName ?author_name .
}
GROUP BY ?author_name
"""

    extended = extend_with_external_identifier(query)

    assert "?orcid" in extended.split("WHERE", 1)[0]
    assert "OPTIONAL { ?author dblp:orcid ?orcid . }" in extended
    assert "GROUP BY ?author_name ?orcid" in extended


def test_publication_grouping_adds_optional_doi():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?title (COUNT(?author) AS ?count)
WHERE {
  ?publication a dblp:Publication .
  ?publication dblp:title ?title .
}
GROUP BY ?title
"""

    extended = extend_with_external_identifier(query)

    assert "?doi" in extended.split("WHERE", 1)[0]
    assert "OPTIONAL { ?publication dblp:doi ?doi . }" in extended
    assert "GROUP BY ?title ?doi" in extended


def test_venue_grouping_adds_optional_issn():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?venue_name (COUNT(?publication) AS ?count)
WHERE {
  ?publication dblp:publishedInStream ?venue .
  ?venue dblp:primaryStreamTitle ?venue_name .
}
GROUP BY ?venue_name
"""

    extended = extend_with_external_identifier(query)

    assert "?issn" in extended.split("WHERE", 1)[0]
    assert "OPTIONAL { ?venue dblp:issn ?issn . }" in extended
    assert "GROUP BY ?venue_name ?issn" in extended


def test_grouping_extension_preserves_order_by_boundary():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?venue_name (COUNT(DISTINCT ?publication) AS ?publication_count)
WHERE {
  ?publication dblp:publishedInStream ?venue .
  ?venue dblp:primaryStreamTitle ?venue_name .
}
GROUP BY ?venue_name
ORDER BY DESC(?publication_count)
LIMIT 10
"""

    extended = extend_with_external_identifier(query)

    assert "GROUP BY ?venue_name ?issn\nORDER BY" in extended
    assert "?issnORDER" not in extended


def test_year_grouping_is_unchanged():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?year (COUNT(?publication) AS ?count)
WHERE { ?publication dblp:yearOfPublication ?year . }
GROUP BY ?year
"""

    assert extend_with_external_identifier(query) == query


def test_query_without_group_by_is_unchanged():
    query = "SELECT ?author WHERE { ?author ?predicate ?value . }"
    assert extend_with_external_identifier(query) == query


def test_existing_identifier_is_not_duplicated_and_other_groups_are_preserved():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?author_name ?year ?orcid (COUNT(?publication) AS ?count)
WHERE {
  ?publication dblp:authoredBy ?author .
  ?author dblp:primaryCreatorName ?author_name .
  OPTIONAL { ?author dblp:orcid ?orcid . }
  ?publication dblp:yearOfPublication ?year .
}
GROUP BY ?author_name ?year ?orcid
"""

    extended = extend_with_external_identifier(query)

    assert extended.count("dblp:orcid") == 1
    assert "GROUP BY ?author_name ?year ?orcid" in extended


def test_unrecognized_grouping_fails_safe():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?topic (COUNT(?publication) AS ?count)
WHERE { ?publication dblp:title ?topic . }
GROUP BY ?topic
"""

    unsupported = query.replace("?publication dblp:title ?topic", "?publication ?predicate ?topic")
    assert extend_with_external_identifier(unsupported) == unsupported


def test_extended_query_passes_validator():
    query = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?author_name (COUNT(?publication) AS ?count)
WHERE {
  ?publication dblp:authoredBy ?author .
  ?author dblp:primaryCreatorName ?author_name .
}
GROUP BY ?author_name
"""

    validation = SPARQLValidator().validate(extend_with_external_identifier(query))
    assert validation.valid, validation.errors


@pytest.mark.asyncio
async def test_exploration_validates_and_executes_extended_query():
    original = """PREFIX dblp: <https://dblp.org/rdf/schema#>
SELECT ?author_name (COUNT(?publication) AS ?count)
WHERE {
  ?publication dblp:authoredBy ?author .
  ?author dblp:primaryCreatorName ?author_name .
}
GROUP BY ?author_name
"""
    extended = extend_with_external_identifier(original)

    service = object.__new__(ExplorationService)
    service._sparql_generation = Mock(
        run=Mock(return_value=SPARQLGeneration(query=original))
    )
    service._sparql_validator = Mock()
    service._sparql_validator.validate.return_value = Mock(valid=True, errors=[])
    service._sparql_client = Mock()
    service._sparql_client.execute.return_value = QueryResult(
        columns=["author_name", "orcid", "count"], rows=[], row_count=0
    )
    service._result_analysis = Mock()
    service._suggestions = Mock()
    service._suggestions.run.return_value = []

    context = ExplorationContext(
        user_message="Who are the most prolific authors?",
        interpretation=Interpretation(scope="in_scope", message="Find authors"),
    )

    response = await service._handle_in_scope(context)

    service._sparql_validator.validate.assert_called_once_with(extended)
    service._sparql_client.execute.assert_called_once_with(extended)
    assert response.sparql_query == extended
