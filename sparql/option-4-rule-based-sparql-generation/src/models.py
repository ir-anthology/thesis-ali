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


class QueryInterpretation(BaseModel):
    """Unified result of query interpretation.

    Categorizes user queries into one of three outcomes:
    - clear: Query is answerable, proceed with SPARQL generation
    - ambiguous: Query needs clarification, return options
    - out_of_scope: Query cannot be answered via DBLP
    """

    outcome: str = Field(
        ...,
        description="One of: 'clear', 'ambiguous', 'out_of_scope'",
    )
    intent: str = Field(
        ...,
        description="First-person intent for 'clear' outcome (e.g., 'Let me find papers by Geoffrey Hinton'). "
        "Descriptive summary for 'ambiguous' and 'out_of_scope' outcomes.",
    )
    entities_mentioned: list[EntityMention] = Field(
        default_factory=list, description="Extracted entity mentions"
    )
    constraints: Constraints = Field(
        default_factory=Constraints,
        description="Extracted constraints (year, publication_type, etc.)",
    )
    clarification: str | None = Field(
        default=None,
        description="Clarification question (only for 'ambiguous' outcome)",
    )
    options: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="2-3 specific clickable options for the user (only for 'ambiguous' outcome)",
    )
    limitation: str | None = Field(
        default=None,
        description="Explanation of limitation (only for 'out_of_scope' outcome)",
    )
    suggestions: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="1-3 DBLP query suggestions (for 'ambiguous' and 'out_of_scope' outcomes)",
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


class QueryExecutionResult(BaseModel):
    """Result of executing SPARQL against DBLP endpoint."""

    success: bool = Field(description="Whether execution succeeded")
    columns: list[str] = Field(
        default_factory=list, description="Column names from SPARQL result"
    )
    rows: list[dict[str, str]] = Field(
        default_factory=list, description="Raw rows from SPARQL result"
    )
    row_count: int = Field(default=0, description="Number of rows returned")
    error: str | None = Field(
        default=None, description="Error message if execution failed"
    )


class ColumnDef(BaseModel):
    """Column definition for formatted response."""

    key: str = Field(description="Column key (SPARQL variable name)")
    label: str = Field(description="Human-readable column label")
    type: str = Field(default="text", description="Column type: text, number, uri")
    sortable: bool = Field(default=True, description="Whether column is sortable")


class CellValue(BaseModel):
    """A cell value with associated question."""

    value: str | int | float = Field(description="Cell value")
    question: str = Field(description="Natural language question about this value")


class FormattedResponse(BaseModel):
    """Formatted response with columns, rows, and questions."""

    columns: list[ColumnDef] = Field(description="Column definitions")
    rows: list[dict[str, CellValue]] = Field(
        description="Rows with cell values and questions"
    )
    row_count: int = Field(description="Number of rows")
    query_explanation: str = Field(
        default="", description="Explanation of what the query returns"
    )


# Frontend-compatible models


class ResultColumn(BaseModel):
    """Column definition matching frontend contract."""

    key: str = Field(description="Column key")
    label: str = Field(description="Display label")
    type: str = Field(
        default="text",
        description="Column type: text, number, badge, link",
    )
    sortable: bool = Field(default=False, description="Whether column is sortable")


class HistoryTurn(BaseModel):
    """Conversation history turn."""

    role: str = Field(description="Role: user or assistant")
    content: str = Field(description="Message content")
    interpretation: str | None = Field(
        default=None, description="Backend's interpretation of the query"
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


class ExplorationResponse(BaseModel):
    """Frontend response schema."""

    interpretation: str | None = Field(
        default=None, description="Backend's interpretation of the query"
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


class QueryResponse(BaseModel):
    """Internal response for pipeline (backward compatibility)."""

    interpretation: str | None = Field(
        default=None, description="Backend's interpretation of the query"
    )
    sparql_query: str | None = Field(default=None, description="Generated SPARQL query")
    suggestions: list[str] = Field(
        default_factory=list, description="Suggested alternatives or next steps"
    )
    columns: list[ColumnDef] = Field(
        default_factory=list, description="Column definitions for table display"
    )
    rows: list[dict[str, CellValue]] = Field(
        default_factory=list, description="Rows with cell values and questions"
    )
    row_count: int = Field(default=0, description="Number of rows returned")
    error: str | None = Field(default=None, description="Execution error if any")
