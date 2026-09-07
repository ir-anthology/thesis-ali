"""LLM structured-output models.

These are the *internal* models used for LLM calls.  They are distinct from the
API response models so that each LLM stage can evolve independently.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Interpretation(BaseModel):
    """Stage 1 output — query interpretation and scope decision."""

    scope: Literal["in_scope", "out_of_scope", "ambiguous"] = Field(
        description="Whether the request is answerable via DBLP"
    )

    message: str = Field(
        description="User-friendly message describing the interpretation"
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
