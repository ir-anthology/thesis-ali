"""Step 6: Execute SPARQL queries against DBLP endpoint."""

import logging
import httpx
from .config import DBLP_SPARQL_ENDPOINT, MAX_RESULT_ROWS
from .models import QueryExecutionResult

logger = logging.getLogger(__name__)


class SPARQLExecutor:
    """Executes SPARQL queries against DBLP endpoint."""

    def __init__(self):
        self.endpoint = DBLP_SPARQL_ENDPOINT
        self.max_rows = MAX_RESULT_ROWS
        self.client = httpx.Client(timeout=30.0)

    def execute(self, sparql_query: str) -> QueryExecutionResult:
        """Execute SPARQL query against DBLP endpoint.

        Args:
            sparql_query: Valid SPARQL query string

        Returns:
            QueryExecutionResult with columns, rows, and status
        """
        logger.info("Executing SPARQL against DBLP endpoint: %s", self.endpoint)

        # Add LIMIT if not present
        query = sparql_query.strip()
        if "LIMIT" not in query.upper():
            query = f"{query.rstrip()}\nLIMIT {self.max_rows}"
            logger.info("Added LIMIT %d to query", self.max_rows)

        try:
            response = self.client.post(
                self.endpoint,
                content=query,
                headers={
                    "Content-Type": "application/sparql-query",
                    "Accept": "application/sparql-results+json",
                },
            )
            response.raise_for_status()

            data = response.json()
            result = self._parse_response(data)

            logger.info(
                "SPARQL execution successful: %d columns, %d rows",
                len(result.columns),
                result.row_count,
            )
            return result

        except httpx.HTTPStatusError as e:
            logger.error("SPARQL execution HTTP error: %s", str(e))
            return QueryExecutionResult(
                success=False,
                error=f"HTTP error: {e.response.status_code} - {e.response.text}",
            )
        except Exception as e:
            logger.error("SPARQL execution failed: %s", str(e))
            return QueryExecutionResult(
                success=False,
                error=f"Execution error: {str(e)}",
            )

    def _parse_response(self, data: dict) -> QueryExecutionResult:
        """Parse SPARQL JSON response.

        Args:
            data: JSON response from SPARQL endpoint

        Returns:
            QueryExecutionResult with parsed columns and rows
        """
        head = data.get("head", {})
        results = data.get("results", {})
        bindings = results.get("bindings", [])

        columns = head.get("vars", [])
        rows = []

        for binding in bindings:
            row = {}
            for col in columns:
                if col in binding:
                    row[col] = binding[col].get("value", "")
                else:
                    row[col] = ""
            rows.append(row)

        return QueryExecutionResult(
            success=True,
            columns=columns,
            rows=rows,
            row_count=len(rows),
        )

    def close(self):
        """Close HTTP client."""
        self.client.close()
