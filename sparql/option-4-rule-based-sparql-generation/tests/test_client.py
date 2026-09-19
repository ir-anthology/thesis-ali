"""Tests for exact SPARQL query execution."""

from unittest.mock import Mock

from backend.main.sparql.client import SPARQLClient


def _client_with_response() -> tuple[SPARQLClient, Mock]:
    client = SPARQLClient()
    response = Mock()
    response.json.return_value = {
        "head": {"vars": ["value"]},
        "results": {"bindings": [{"value": {"value": "result"}}]},
    }
    client._client.post = Mock(return_value=response)
    return client, response


def test_query_with_llm_limit_is_sent_unchanged():
    client, response = _client_with_response()
    query = "SELECT ?value WHERE { ?s ?p ?value } LIMIT 10"

    client.execute(query)

    response.raise_for_status.assert_called_once_with()
    client._client.post.assert_called_once()
    assert client._client.post.call_args.kwargs["content"] == query


def test_larger_llm_limit_is_not_reduced():
    client, _ = _client_with_response()
    query = "SELECT ?value WHERE { ?s ?p ?value } LIMIT 100"

    client.execute(query)

    assert client._client.post.call_args.kwargs["content"] == query


def test_query_without_limit_is_not_modified_by_client():
    client, _ = _client_with_response()
    query = "SELECT (COUNT(?s) AS ?count) WHERE { ?s ?p ?o }"

    client.execute(query)

    assert client._client.post.call_args.kwargs["content"] == query
