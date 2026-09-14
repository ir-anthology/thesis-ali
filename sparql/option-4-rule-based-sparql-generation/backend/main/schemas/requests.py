"""API request models."""

from __future__ import annotations

from typing import Literal

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
