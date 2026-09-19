"""API response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ResultColumn(BaseModel):
    """Column definition matching the frontend contract."""

    key: str = Field(description="Column key (matches SPARQL variable name)")
    label: str = Field(description="Human-readable display label")
    type: Literal["text", "number", "badge", "link"] = Field(
        default="text", description="Column type"
    )
    sortable: bool = Field(default=False, description="Whether column is sortable")
    visible: bool = Field(default=True, description="Whether the column is visible")
    external_link: bool = Field(
        default=False,
        description="Whether the value can represent an external link",
    )
    related_column: str | None = Field(
        default=None,
        description="Related entity/display column key",
    )


class CellMetadata(BaseModel):
    """Optional entity metadata attached to a displayed cell."""

    model_config = ConfigDict(extra="allow")

    entity_id: str | None = None
    entity_type: Literal["author", "venue", "publication", "entity"] | None = None


class CellValue(BaseModel):
    """A cell value with an associated follow-up question."""

    value: str | int | float = Field(description="Cell value")
    question: str = Field(
        default="", description="Natural language question about this value"
    )
    metadata: CellMetadata | None = Field(
        default=None, description="Hidden entity metadata for drill-down"
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


class StatisticsResponse(BaseModel):
    """Response for the /api/statistics endpoint."""

    columns: list[ResultColumn] = Field(description="Column definitions")
    rows: list[dict[str, CellValue]] = Field(description="Data rows")


class CellQuestionResponse(BaseModel):
    """Response containing one lazily generated cell follow-up question."""

    question: str = Field(description="Generated follow-up question")
