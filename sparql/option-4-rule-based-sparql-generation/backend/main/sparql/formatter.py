"""Result normalisation — converts raw QueryResult into frontend table format."""

from __future__ import annotations

from backend.main.schemas.context import QueryResult
from backend.main.schemas.responses import CellMetadata, ResultColumn, CellValue


_EXTERNAL_IDENTIFIER_CANDIDATES: dict[str, tuple[str, ...]] = {
    "orcid": ("author_name", "author", "creator_name", "creator"),
    "doi": (
        "title",
        "publication_title",
        "publication",
        "pub",
        "paper",
        "article",
    ),
    "issn": (
        "venue_name",
        "venue",
        "stream_name",
        "stream",
        "journal",
        "conference",
    ),
}


def _is_uri_column(column: str, query_result: QueryResult) -> bool:
    """Identify raw entity URI columns."""
    key = column.lower()
    if key in {"id", "uri"}:
        return True
    if key.endswith(("_id", "_uri")):
        return True

    values = [str(row.get(column, "")) for row in query_result.rows]
    non_empty = [value for value in values if value]
    return bool(non_empty) and all(value.startswith("https://dblp.org/") for value in non_empty)


def _entity_type(column: str) -> str:
    key = column.lower()
    if "author" in key or "creator" in key:
        return "author"
    if "venue" in key or "stream" in key or "journal" in key or "conference" in key:
        return "venue"
    if "pub" in key or "paper" in key or "article" in key:
        return "publication"
    return "entity"


def _metadata_source(column: str, columns: list[str]) -> str | None:
    """Find the metadata column associated with a display column."""
    candidates = [f"{column}_id", f"{column}_uri"]
    if column.endswith("_name"):
        prefix = column.removesuffix("_name")
        candidates.extend([f"{prefix}_id", f"{prefix}_uri"])
    if column in {"title", "name"}:
        candidates.extend(["pub_id", "publication_id", "pub_uri", "publication_uri"])
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _related_column(
    identifier_column: str,
    columns: list[ResultColumn],
) -> str | None:
    """Find the visible display column related to an external identifier."""
    candidates = _EXTERNAL_IDENTIFIER_CANDIDATES.get(identifier_column.lower())
    if candidates is None:
        return None

    visible_by_key = {
        column.key.lower(): column.key
        for column in columns
        if column.visible
    }
    for candidate in candidates:
        if candidate in visible_by_key:
            return visible_by_key[candidate]
    return None


def format_result_columns(query_result: QueryResult) -> list[ResultColumn]:
    """Create frontend column definitions from a QueryResult."""
    columns = [
        ResultColumn(
            key=col,
            label=col.replace("_", " ").title(),
            sortable=not _is_uri_column(col, query_result),
            visible=not _is_uri_column(col, query_result),
            external_link=col.lower() in {"orcid", "doi", "issn"},
        )
        for col in query_result.columns
    ]
    for column in columns:
        if column.external_link:
            column.related_column = _related_column(column.key, columns)
    return columns


def format_result_rows(
    query_result: QueryResult,
) -> list[dict[str, CellValue]]:
    """Create frontend rows (without questions) from a QueryResult.

    Questions are filled in later by the result-analysis service.
    """
    rows: list[dict[str, CellValue]] = []
    columns = format_result_columns(query_result)
    metadata_columns = {
        column.key: column
        for column in columns
        if not column.visible
    }
    for raw_row in query_result.rows:
        row: dict[str, CellValue] = {}
        for col in query_result.columns:
            value = str(raw_row.get(col, ""))
            metadata = None
            if col in metadata_columns and value.startswith("https://dblp.org/"):
                metadata = CellMetadata(
                    entity_id=value,
                    entity_type=_entity_type(col),
                )
            row[col] = CellValue(value=value, question="", metadata=metadata)

        for column in columns:
            if not column.visible:
                continue
            source = _metadata_source(column.key, query_result.columns)
            if source and source in row and row[source].metadata:
                row[column.key] = row[column.key].model_copy(
                    update={"metadata": row[source].metadata}
                )
        rows.append(row)
    return rows
