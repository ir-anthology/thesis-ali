"""API request models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from .responses import CellValue, ResultColumn


class EntityInteraction(BaseModel):
    """Entity selected from a frontend result cell."""

    entity_id: str = Field(description="Absolute DBLP entity IRI")
    entity_type: Literal["author", "venue", "publication", "entity"] | None = Field(
        default=None, description="Optional DBLP entity type"
    )

    @field_validator("entity_id")
    @classmethod
    def validate_entity_id(cls, value: str) -> str:
        if not value.startswith("https://dblp.org/") or any(
            character.isspace() for character in value
        ):
            raise ValueError("entity_id must be an absolute DBLP IRI")
        return value


class AnalyticsInteraction(BaseModel):
    """Meaningful frontend action that led to an exploration request."""

    type: Literal[
        "typed",
        "suggestion_click",
        "cell_click",
        "edit",
        "retry",
    ]
    from_turn_id: str | None = None
    details: dict[str, Any] | None = None


class FeedbackRequest(BaseModel):
    """Anonymous feedback for one rendered assistant answer."""

    answer_turn_id: str = Field(min_length=1)
    feedback: Literal["positive", "negative"]


class HistoryTurn(BaseModel):
    """A single turn in the conversation history sent by the frontend."""

    role: Literal["user", "assistant"] = Field(description="Role: user or assistant")
    content: str = Field(description="Message content")

    interpretation: str | None = Field(
        default=None, description="Backend interpretation of the query"
    )
    columns: list[ResultColumn] | None = Field(
        default=None, description="Column definitions"
    )
    rows: list[dict[str, CellValue]] | None = Field(
        default=None, description="Data rows"
    )
    observations: list[str] | None = Field(default=None, description="LLM insights")
    suggestions: list[str] | None = Field(
        default=None, description="Follow-up suggestions"
    )
    sparql_query: str | None = Field(default=None, description="SPARQL query used")


class ChatRequest(BaseModel):
    """Frontend request schema."""

    message: str = Field(description="User's natural language query")
    history: list[HistoryTurn] = Field(
        default_factory=list, description="Conversation history"
    )
    interaction: EntityInteraction | None = Field(
        default=None, description="Optional entity selected from a result cell"
    )
    analytics_interaction: AnalyticsInteraction | None = Field(
        default=None, description="Optional meaningful frontend action metadata"
    )


class CellQuestionRequest(BaseModel):
    """Prompt data for generating one follow-up question on demand."""

    column: str = Field(description="Selected result column key")
    value: str | int | float = Field(description="Selected cell value")
    row: dict[str, str | int | float] = Field(
        description="All values from the selected result row"
    )
    metadata: dict[str, dict[str, str | int | float | bool | None]] | None = Field(
        default=None,
        description="Non-question metadata associated with result cells",
    )
    interpretation: str | None = Field(
        default=None,
        description="Interpretation displayed above the result table",
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value):
        if value is None:
            return value
        for cell_metadata in value.values():
            entity_id = cell_metadata.get("entity_id")
            if entity_id is not None and (
                not isinstance(entity_id, str)
                or not entity_id.startswith("https://dblp.org/")
                or any(character.isspace() for character in entity_id)
            ):
                raise ValueError("metadata entity_id must be an absolute DBLP IRI")
        return value
