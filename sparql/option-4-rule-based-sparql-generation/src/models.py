"""Pydantic models for rule-based SPARQL generation."""

from pydantic import BaseModel, Field


class EntityMention(BaseModel):
    """An entity mention extracted from user query."""

    text: str = Field(..., description="Original text mention")
    type_hint: str = Field(
        default="Unknown",
        description="Entity type hint: Person, Conference, Journal, Venue, Unknown",
    )


class Constraints(BaseModel):
    """Extracted constraints from the query."""

    year: str | None = Field(default=None, description="Year filter (e.g., '2023')")
    publication_type: str | None = Field(
        default=None, description="Publication type (Article, Inproceedings, etc.)"
    )


class IntentResult(BaseModel):
    """Result of intent classification with limitation detection."""

    intent: str = Field(
        ...,
        description="Natural language rephrasing in 3rd person. "
        "Start with 'The user is asking for...' or 'The user wants to know...'",
    )
    entities_mentioned: list[EntityMention] = Field(
        default_factory=list, description="Extracted entity mentions"
    )
    constraints: Constraints = Field(
        default_factory=Constraints,
        description="Extracted constraints (year, publication_type, etc.)",
    )
    has_limitation: bool = Field(
        default=False,
        description="True if query requires features not available in DBLP",
    )
    limitation: str | None = Field(
        default=None, description="Explanation of limitation if has_limitation is true"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="1-3 follow-up suggestions when has_limitation is true",
    )


class Candidate(BaseModel):
    """A candidate entity match."""

    uri: str = Field(default="", description="DBLP URI")
    label: str = Field(default="", description="Human-readable label")


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
    candidates: list[Candidate] = Field(
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


class ClarificationResult(BaseModel):
    """Result of clarification detection."""

    needs_clarification: bool = Field(
        default=False, description="Whether clarification is needed"
    )
    clarification: str | None = Field(
        default=None, description="Clarification question"
    )
    suggestions: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="1-3 complete query suggestions that resolve the ambiguity",
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
    suggestions: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="1-3 follow-up query suggestions",
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
