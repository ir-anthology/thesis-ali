"""LLM structured-output models.

These are the *internal* models used for LLM calls.  They are distinct from the
API response models so that each LLM stage can evolve independently.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Interpretation(BaseModel):
    """Stage 1 output — query interpretation and scope decision."""

    summary: str = Field(description="Brief summary of what the user is asking")

    scope: Literal["in_scope", "out_of_scope", "ambiguous"] = Field(
        description="Whether the request is answerable via DBLP"
    )

    entities: list[str] = Field(
        default_factory=list,
        description="Entity names mentioned (authors, venues, etc.)",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Extracted constraints (year, publication type, etc.)",
    )
    requested_information: list[str] = Field(
        default_factory=list,
        description="What information the user wants",
    )

    possible_scopes: list[str] = Field(
        default_factory=list,
        description="Possible interpretations (only for ambiguous scope)",
    )
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Questions to ask the user (only for ambiguous scope)",
    )

    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made during interpretation",
    )


class SPARQLGeneration(BaseModel):
    """Stage 2 output — a generated SPARQL query."""

    query: str = Field(description="The generated SPARQL query")


class ResultQuestions(BaseModel):
    """Stage 3 output — questions for meaningful cells."""

    questions: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of column_key -> question for meaningful cells",
    )


class Observations(BaseModel):
    """Stage 3 output — data-grounded observations."""

    observations: list[str] = Field(
        default_factory=list,
        description="1-3 observations derived from the data",
    )


class Suggestions(BaseModel):
    """Stage 4 output — follow-up questions / suggestions."""

    suggestions: list[str] = Field(
        default_factory=list,
        description="2-3 follow-up questions answerable via DBLP",
    )
