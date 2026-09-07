"""SPARQL execution client — communicates with the DBLP/QLever endpoint.

This module knows nothing about LLMs or prompting.
"""

from __future__ import annotations

import logging

import httpx

from backend.main.config import DBLP_SPARQL_ENDPOINT, MAX_RESULT_ROWS
from backend.main.schemas.context import QueryResult

logger = logging.getLogger(__name__)


class SPARQLClient:
    """Executes SPARQL queries against the DBLP endpoint."""

    def __init__(self) -> None:
        self.endpoint = DBLP_SPARQL_ENDPOINT
        self.max_rows = MAX_RESULT_ROWS
        self._client = httpx.Client(timeout=30.0)

    def execute(self, sparql_query: str) -> QueryResult:
        """Execute a validated SPARQL query.

        Args:
            sparql_query: The SPARQL query string.

        Returns:
            QueryResult with columns, rows, and row_count.

        Raises:
            SPARQLError: If execution fails.
        """
        logger.info("Executing SPARQL against %s", self.endpoint)

        query = sparql_query.strip()
        if "LIMIT" not in query.upper():
            query = f"{query.rstrip()}\nLIMIT {self.max_rows}"
            logger.info("Added LIMIT %d to query", self.max_rows)

        try:
            response = self._client.post(
                self.endpoint,
                content=query,
                headers={
                    "Content-Type": "application/sparql-query",
                    "Accept": "application/sparql-results+json",
                },
            )
            response.raise_for_status()

            data = response.json()
            return self._parse_response(data)

        except httpx.HTTPStatusError as exc:
            logger.error("SPARQL HTTP error: %s", exc)
            raise SPARQLError(
                f"HTTP error: {exc.response.status_code} — {exc.response.text}"
            ) from exc
        except SPARQLError:
            raise
        except Exception as exc:
            logger.error("SPARQL execution failed: %s", exc)
            raise SPARQLError(f"Execution error: {exc}") from exc

    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(data: dict) -> QueryResult:
        head = data.get("head", {})
        results = data.get("results", {})
        bindings: list[dict] = results.get("bindings", [])

        columns: list[str] = head.get("vars", [])
        rows: list[dict[str, object]] = []

        for binding in bindings:
            row: dict[str, object] = {}
            for col in columns:
                if col in binding:
                    row[col] = binding[col].get("value", "")
                else:
                    row[col] = ""
            rows.append(row)

        return QueryResult(columns=columns, rows=rows, row_count=len(rows))

    def close(self) -> None:
        self._client.close()


class SPARQLError(Exception):
    """Raised when SPARQL execution fails."""
