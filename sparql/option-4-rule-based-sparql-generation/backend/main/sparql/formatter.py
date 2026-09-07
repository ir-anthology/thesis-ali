"""Result normalisation — converts raw QueryResult into frontend table format."""

from __future__ import annotations

from backend.main.schemas.context import QueryResult
from backend.main.schemas.responses import ResultColumn, CellValue


def format_result_columns(query_result: QueryResult) -> list[ResultColumn]:
    """Create frontend column definitions from a QueryResult."""
    return [
        ResultColumn(key=col, label=col.replace("_", " ").title())
        for col in query_result.columns
    ]


def format_result_rows(
    query_result: QueryResult,
) -> list[dict[str, CellValue]]:
    """Create frontend rows (without questions) from a QueryResult.

    Questions are filled in later by the result-analysis service.
    """
    rows: list[dict[str, CellValue]] = []
    for raw_row in query_result.rows:
        row: dict[str, CellValue] = {}
        for col in query_result.columns:
            value = str(raw_row.get(col, ""))
            row[col] = CellValue(value=value, question="")
        rows.append(row)
    return rows
