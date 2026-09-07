"""API request models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from .responses import CellValue, ResultColumn


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
