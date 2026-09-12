"""GET /api/statistics — aggregated DBLP statistics endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter

from backend.main.schemas.responses import StatisticsResponse, ResultColumn, CellValue
from backend.main.sparql.client import SPARQLClient, SPARQLError

logger = logging.getLogger(__name__)

router = APIRouter()

_sparql_client = SPARQLClient()

STATISTICS_SPARQL = """\
PREFIX dblp: <https://dblp.org/rdf/schema#>

SELECT
  (COUNT(DISTINCT ?authorName) AS ?Authors)
  (COUNT(DISTINCT ?pub)        AS ?Publications)
  (COUNT(DISTINCT ?venueTitle) AS ?Venues)
  (COUNT(DISTINCT ?year)       AS ?Years)
WHERE {
  ?pub a dblp:Publication .
  OPTIONAL { ?pub dblp:authoredBy ?authorName . }
  OPTIONAL { ?pub dblp:title ?pubTitle . }
  OPTIONAL { ?pub dblp:publishedIn ?venueTitle . }
  OPTIONAL { ?pub dblp:yearOfPublication ?year . }
}
"""

COLUMNS = [
    ResultColumn(key="author", label="Author", type="number", sortable=True),
    ResultColumn(key="publications", label="Publications", type="number", sortable=True),
    ResultColumn(key="venue", label="Venue", type="number", sortable=True),
    ResultColumn(key="year", label="Year", type="number", sortable=True),
]


def _build_response(raw_row: dict[str, object]) -> StatisticsResponse:
    """Map SPARQL result variables to the frontend column/row contract."""
    row: dict[str, CellValue] = {
        "author": CellValue(
            value=int(raw_row.get("Authors", 0)),
            question="List top 10 Authors based on Publications count.",
        ),
        "publications": CellValue(
            value=int(raw_row.get("Publications", 0)),
            question="List top 10 Publications published in 2025.",
        ),
        "venue": CellValue(
            value=int(raw_row.get("Venues", 0)),
            question="List top 10 venues based on Publications count.",
        ),
        "year": CellValue(
            value=int(raw_row.get("Years", 0)),
            question="List top 10 Year based on Publications count.",
        ),
    }
    return StatisticsResponse(columns=COLUMNS, rows=[row])


@router.get("/api/statistics", response_model=StatisticsResponse)
async def statistics() -> StatisticsResponse:
    """Return aggregated DBLP statistics (authors, publications, venues, years)."""
    logger.info("Received statistics request")

    try:
        result = _sparql_client.execute(STATISTICS_SPARQL)
        if result.rows:
            return _build_response(result.rows[0])
        return StatisticsResponse(columns=COLUMNS, rows=[])
    except SPARQLError:
        logger.exception("SPARQL execution failed for statistics")
        return StatisticsResponse(columns=COLUMNS, rows=[])
    except Exception:
        logger.exception("Unexpected error in statistics endpoint")
        return StatisticsResponse(columns=COLUMNS, rows=[])
