"""Internal exploration context — accumulates data through the pipeline.

This is separate from the API response model.  Each pipeline stage receives the
full context and adds its own output.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from .requests import HistoryTurn
from .responses import ResultColumn, CellValue
from .llm import Interpretation


class QueryResult(BaseModel):
    """Raw result from SPARQL execution."""

    columns: list[str] = Field(
        default_factory=list, description="Column variable names"
    )
    rows: list[dict[str, object]] = Field(
        default_factory=list, description="Raw result rows"
    )
    row_count: int = Field(default=0, description="Number of rows returned")


class ExplorationContext(BaseModel):
    """Accumulates all derived data for a single exploration request.

    The pipeline enriches this context at every stage.
    """

    # C0 — inputs
    user_message: str
    history: list[HistoryTurn] = Field(default_factory=list)

    # DBLP schema (set once)
    dblp_schema: str | None = None

    # C1 — interpretation
    interpretation: Interpretation | None = None

    # C2 — SPARQL
    sparql_query: str | None = None
    query_result: QueryResult | None = None

    # C3 — result analysis
    result_columns: list[ResultColumn] = Field(default_factory=list)
    result_rows: list[dict[str, CellValue]] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)

    # C4 — suggestions
    suggestions: list[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Enrichment helpers
    # ------------------------------------------------------------------

    def set_schema(self, schema: str) -> None:
        self.dblp_schema = schema

    def set_interpretation(self, interpretation: Interpretation) -> None:
        self.interpretation = interpretation

    def set_sparql(self, query: str) -> None:
        self.sparql_query = query

    def set_query_result(self, result: QueryResult) -> None:
        self.query_result = result

    def set_result_table(
        self,
        columns: list[ResultColumn],
        rows: list[dict[str, CellValue]],
    ) -> None:
        self.result_columns = columns
        self.result_rows = rows

    def set_observations(self, observations: list[str]) -> None:
        self.observations = observations

    def set_suggestions(self, suggestions: list[str]) -> None:
        self.suggestions = suggestions
