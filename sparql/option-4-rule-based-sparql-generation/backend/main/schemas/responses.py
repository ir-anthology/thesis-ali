"""API response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ResultColumn(BaseModel):
    """Column definition matching the frontend contract."""

    key: str = Field(description="Column key (matches SPARQL variable name)")
    label: str = Field(description="Human-readable display label")
    type: Literal["text", "number", "badge", "link"] = Field(
        default="text", description="Column type"
    )
    sortable: bool = Field(default=False, description="Whether column is sortable")


class CellValue(BaseModel):
    """A cell value with an associated follow-up question."""

    value: str | int | float = Field(description="Cell value")
    question: str = Field(
        default="", description="Natural language question about this value"
    )


class ExplorationResponse(BaseModel):
    """Response returned to the frontend."""

    interpretation: str | None = Field(
        default=None, description="Backend interpretation of the query"
    )
    columns: list[ResultColumn] | None = Field(
        default=None, description="Column definitions"
    )
    rows: list[dict[str, CellValue]] | None = Field(
        default=None, description="Data rows"
    )
    observations: list[str] | None = Field(
        default=None, description="LLM-generated insights"
    )
    suggestions: list[str] | None = Field(
        default=None, description="Follow-up suggestions"
    )
    sparql_query: str | None = Field(default=None, description="SPARQL query used")
