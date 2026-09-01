"""Pydantic models for rule-based SPARQL generation."""

from enum import Enum
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Intent categories for DBLP queries."""

    find_publications_by_author = "find_publications_by_author"
    find_publications_by_venue = "find_publications_by_venue"
    find_publications_by_author_and_venue = "find_publications_by_author_and_venue"
    find_publications_by_year = "find_publications_by_year"
    find_publications_by_type = "find_publications_by_type"
    find_authors_of_publication = "find_authors_of_publication"
    find_coauthors = "find_coauthors"
    find_author_metadata = "find_author_metadata"
    find_venue_info = "find_venue_info"
    count_publications = "count_publications"
    unknown = "unknown"


class EntityMention(BaseModel):
    """An entity mention extracted from user query."""

    text: str = Field(..., description="Original text mention")
    type_hint: str = Field(
        default="Unknown",
        description="Entity type hint: Person, Conference, Journal, Venue, Unknown",
    )


class IntentResult(BaseModel):
    """Result of intent classification."""

    intent: IntentType = Field(..., description="Classified intent")
    entities_mentioned: list[EntityMention] = Field(
        default_factory=list, description="Extracted entity mentions"
    )
    constraints: dict = Field(
        default_factory=dict,
        description="Extracted constraints (year, publication_type, etc.)",
    )
    needs_clarification: bool = Field(
        default=False, description="Whether clarification is needed"
    )
    clarification_question: str | None = Field(
        default=None, description="Clarification question if needed"
    )


class ResolvedEntity(BaseModel):
    """An entity resolved to a DBLP URI."""

    mention: str = Field(..., description="Original text mention")
    uri: str | None = Field(default=None, description="Resolved DBLP URI")
    label: str | None = Field(default=None, description="Human-readable label")
    type: str | None = Field(default=None, description="Entity type")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence score"
    )
    ambiguous: bool = Field(default=False, description="Whether multiple matches found")
    not_found: bool = Field(default=False, description="Whether entity was not found")
    candidates: list[dict] = Field(
        default_factory=list, description="Candidate matches if ambiguous"
    )


class EntityResolutionResult(BaseModel):
    """Result of entity resolution step."""

    resolved_entities: list[ResolvedEntity] = Field(
        default_factory=list, description="Resolved entities"
    )
    unresolved_mentions: list[str] = Field(
        default_factory=list, description="Mentions that could not be resolved"
    )


class LimitationResult(BaseModel):
    """Result of limitation detection."""

    has_limitation: bool = Field(
        default=False, description="Whether query has limitations"
    )
    limitation: str | None = Field(
        default=None, description="Limitation message if applicable"
    )


class ClarificationResult(BaseModel):
    """Result of clarification detection."""

    needs_clarification: bool = Field(
        default=False, description="Whether clarification is needed"
    )
    clarification: str | None = Field(
        default=None, description="Clarification question"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Suggested alternatives"
    )


class SPARQLResult(BaseModel):
    """Result of SPARQL generation."""

    sparql: str = Field(..., description="Generated SPARQL query")
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence score"
    )
    explanation: str = Field(
        default="", description="Explanation of the generated query"
    )


class ValidationResult(BaseModel):
    """Result of SPARQL validation."""

    valid: bool = Field(default=False, description="Whether query is valid")
    errors: list[str] = Field(default_factory=list, description="Validation errors")
    warnings: list[str] = Field(default_factory=list, description="Validation warnings")


class QueryResponse(BaseModel):
    """Final response for a natural language query."""

    intent: str = Field(..., description="Detected intent")
    clarification: str | None = Field(
        default=None, description="Clarification question if needed"
    )
    limitation: str | None = Field(
        default=None, description="Limitation message if applicable"
    )
    sparql_query: str | None = Field(default=None, description="Generated SPARQL query")
    suggestions: list[str] = Field(
        default_factory=list, description="Suggested alternatives or next steps"
    )
