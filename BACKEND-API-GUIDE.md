# Backend API Guide: Frontend Consumption Contract

**Application:** Adaptive Conversational Knowledge Graph Explorer
**Frontend:** `frontend/adaptive/` (SvelteKit + Tailwind CSS)
**Backend:** `backend/main/` (FastAPI + Python)
**Date:** August 2026

---

## 1. Overview

This guide defines the API contract between the Scholarly Explorer frontend and backend. The frontend is a conversation-driven adaptive UI that renders structured exploration results from a scholarly knowledge graph. The backend must return **semantic exploration state** — not raw SPARQL or text — so the frontend can dynamically render the appropriate visualization.

### Architecture

```
User Input (natural language)
       ↓
   Frontend (SvelteKit)
       ↓  POST /api/exploration
   Backend (FastAPI)
       ↓
   LLM (intent parsing + observation generation)
       ↓
   SPARQL Query Builder
       ↓
   Knowledge Graph (triplestore)
       ↓
   Result Formatter
       ↓
   ExplorationResponse (JSON)
       ↓
   Frontend renders adaptive UI
```

### Key Principles

1. **Frontend does NOT construct SPARQL** — the backend handles all query generation
2. **Response is semantic** — columns, rows, observations, suggestions (not raw data)
3. **Conversation is stateful** — backend receives context from previous turns
4. **LLM generates insights** — observations and follow-up questions come from the backend

---

## 2. Base URL & Conventions

| Property | Value |
|----------|-------|
| Base URL | `http://localhost:8000` |
| Content Type | `application/json` |
| CORS | Allow all origins (`*`) |
| Auth | None (MVP) |

### Error Format

All errors follow:

```json
{
  "status": "error",
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "Something went wrong while processing your query."
  }
}
```

---

## 3. Endpoints

### 3.1 POST `/api/exploration`

The primary endpoint for all exploration queries. The frontend sends a user message along with conversation context, and the backend returns a structured exploration response.

**Request:**

```json
{
  "message": "Who are the most prolific authors?",
  "conversation_id": "conv-abc-123",
  "context": {
    "filters": [],
    "target_facet": null,
    "sorting": null
  }
}
```

**Response:**

```json
{
  "status": "answerable",
  "conversation_id": "conv-abc-123",
  "exploration": {
    "target_facet": "author",
    "filters": [],
    "sort": {
      "field": "publications",
      "direction": "desc"
    }
  },
  "result": {
    "type": "facet_table",
    "title": "Most Prolific Authors in Exploratory Search",
    "columns": [
      { "key": "author", "label": "Author", "type": "text", "sortable": true },
      { "key": "publications", "label": "Publications", "type": "number", "sortable": true },
      { "key": "venues", "label": "Venues", "type": "number", "sortable": true },
      { "key": "years", "label": "Years", "type": "text" }
    ],
    "rows": [
      { "author": "Marti A. Hearst", "publications": 42, "venues": 12, "years": "1995–2024" },
      { "author": "Ryen W. White", "publications": 38, "venues": 10, "years": "2003–2024" }
    ]
  },
  "interpretation": {
    "observations": [
      {
        "id": "obs-1",
        "text": "Marti A. Hearst leads with 42 publications spanning nearly three decades.",
        "source": "llm"
      }
    ],
    "suggestions": [
      { "id": "sug-1", "text": "Only consider the last five years" },
      { "id": "sug-2", "text": "Which venues do these authors publish in?" },
      { "id": "sug-3", "text": "Show me how this changed over time" }
    ]
  },
  "sparql_query": "PREFIX schema: <http://schema.org/>\nPREFIX dcterms: <http://purl.org/dc/terms/>\n\nSELECT ?author\n       (COUNT(?pub) AS ?publications)\n       (COUNT(DISTINCT ?venue) AS ?venues)\nWHERE {\n  ?pub a schema:ScholarlyArticle ;\n       dcterms:creator ?author ;\n       schema:isPartOf ?venue .\n}\nGROUP BY ?author\nORDER BY DESC(?publications)\nLIMIT 5"
}
```

### 3.2 GET `/api/health`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## 4. Request Schema

### ChatRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User's natural language query |
| `conversation_id` | string | Yes | Unique ID for this conversation session |
| `context` | object | No | Current exploration context from previous turns |
| `context.filters` | Filter[] | No | Active filters from previous turns |
| `context.target_facet` | string | No | Current exploration dimension (author/venue/year/publication) |
| `context.sorting` | SortState | No | Current sort state |

### Filter

| Field | Type | Values |
|-------|------|--------|
| `facet` | string | `"author"`, `"venue"`, `"year"`, `"publication"` |
| `value` | string | Filter value (e.g., `"2020-2025"`, `"SIGIR"`) |
| `label` | string | Display label (e.g., `"2020–2025"`, `"SIGIR"`) |

### SortState

| Field | Type | Values |
|-------|------|--------|
| `field` | string | Column key to sort by |
| `direction` | string | `"asc"` or `"desc"` |

---

## 5. Response Schema

### ExplorationResponse

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"answerable"`, `"unsupported"`, or `"error"` |
| `conversation_id` | string | Same ID from request |
| `exploration` | object | Updated exploration context |
| `exploration.target_facet` | string\|null | Primary dimension for results |
| `exploration.filters` | Filter[] | Active filters (may differ from request) |
| `exploration.sort` | SortState\|null | Recommended sort order |
| `result` | ResultState | The structured result data |
| `interpretation` | InterpretationState | LLM-generated insights |
| `sparql_query` | string\|null | The SPARQL query used (only when `status === "answerable"`) |

### ResultState

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Visualization type (see Section 6) |
| `title` | string | Human-readable title for the result |
| `columns` | ResultColumn[] | Column definitions for tabular data |
| `rows` | ResultRow[] | Data rows |

### ResultColumn

| Field | Type | Description |
|-------|------|-------------|
| `key` | string | Unique identifier for this column |
| `label` | string | Display label |
| `type` | string | `"text"`, `"number"`, `"badge"`, or `"link"` |
| `sortable` | boolean | Whether users can sort by this column |

### ResultRow

A JSON object where keys match column `key` values. Values are strings or numbers.

```json
{
  "author": "Marti A. Hearst",
  "publications": 42,
  "venues": 12,
  "years": "1995–2024"
}
```

### InterpretationState

| Field | Type | Description |
|-------|------|-------------|
| `observations` | Observation[] | LLM-generated insights about the data |
| `suggestions` | FollowUpQuestion[] | Recommended follow-up queries |

### Observation

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `text` | string | The observation text |
| `source` | string | Always `"llm"` |

### FollowUpQuestion

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier |
| `text` | string | The suggested question |

---

## 6. Result Types

The frontend supports 5 visualization types. The backend determines which type is most appropriate for the query.

### 6.1 `facet_table`

Tabular data with sortable columns. Used for most queries.

```json
{
  "type": "facet_table",
  "title": "Most Prolific Authors in Exploratory Search",
  "columns": [
    { "key": "author", "label": "Author", "type": "text", "sortable": true },
    { "key": "publications", "label": "Publications", "type": "number", "sortable": true }
  ],
  "rows": [
    { "author": "Marti A. Hearst", "publications": 42 },
    { "author": "Ryen W. White", "publications": 38 }
  ]
}
```

**Use when:** Query asks for authors, venues, years, publications, or any faceted data.

### 6.2 `entity_list`

List of entities with metadata. Similar to facet_table but for individual entities.

```json
{
  "type": "entity_list",
  "title": "Publications by Marti A. Hearst",
  "columns": [
    { "key": "title", "label": "Title", "type": "text" },
    { "key": "venue", "label": "Venue", "type": "badge" },
    { "key": "year", "label": "Year", "type": "number" }
  ],
  "rows": [
    { "title": "User Interfaces and Support for Exploratory Search", "venue": "SIGIR", "year": 2023 },
    { "title": "Faceted Search for Digital Libraries", "venue": "JASIST", "year": 2021 }
  ]
}
```

**Use when:** Query asks for specific publications or entity details.

### 6.3 `comparison`

Side-by-side comparison of two or more entities.

```json
{
  "type": "comparison",
  "title": "SIGIR vs CHIIR",
  "columns": [
    { "key": "metric", "label": "Metric", "type": "text" },
    { "key": "SIGIR", "label": "SIGIR", "type": "text" },
    { "key": "CHIIR", "label": "CHIIR", "type": "text" }
  ],
  "rows": [
    { "metric": "Total Publications", "SIGIR": "18", "CHIIR": "9" },
    { "metric": "Authors", "SIGIR": "5", "CHIIR": "4" }
  ]
}
```

**Use when:** Query asks to compare two venues, authors, or years.

### 6.4 `timeline`

Temporal visualization with time on one axis and values as bars.

```json
{
  "type": "timeline",
  "title": "Publication Activity Over Time",
  "columns": [
    { "key": "year", "label": "Year", "type": "text" },
    { "key": "SIGIR", "label": "SIGIR", "type": "number" },
    { "key": "CHIIR", "label": "CHIIR", "type": "number" }
  ],
  "rows": [
    { "year": "2020", "SIGIR": 12, "CHIIR": 3 },
    { "year": "2021", "SIGIR": 14, "CHIIR": 4 }
  ]
}
```

**Use when:** Query asks about trends over time, changes, or temporal patterns.

### 6.5 `summary`

Text-based summary with no tabular data. Used for explanatory queries.

```json
{
  "type": "summary",
  "title": "Why SIGIR Is Prominent",
  "columns": [],
  "rows": []
}
```

**Use when:** Query asks "why", "explain", or requires textual analysis rather than data.

---

## 7. Query Scenarios

These are the 7 recognized query types. The backend should handle similar natural language variations.

### 7.1 Prolific Authors

**Input:** `"Who are the most prolific authors?"`
**Target Facet:** `author`
**Result Type:** `facet_table`
**Columns:** author, publications, venues, years

### 7.2 Filtered Results

**Input:** `"Only consider the last five years"`
**Target Facet:** `author`
**Filters:** `[{ facet: "year", value: "2020-2025", label: "2020–2025" }]`
**Result Type:** `facet_table`

### 7.3 Venue Pivot

**Input:** `"Which venues do they publish in?"`
**Target Facet:** `venue`
**Result Type:** `facet_table`
**Columns:** venue, publications, authors, years

### 7.4 Timeline

**Input:** `"Show me how this changed over time"`
**Target Facet:** `year`
**Result Type:** `timeline`
**Columns:** year, [venue1], [venue2], ...

### 7.5 Comparison

**Input:** `"Compare SIGIR and CHIIR"`
**Target Facet:** `venue`
**Result Type:** `comparison`
**Columns:** metric, [entity1], [entity2]

### 7.6 Explanation

**Input:** `"Why is SIGIR prominent?"`
**Target Facet:** `venue`
**Result Type:** `summary`
**Observations:** Multiple LLM-generated insights

### 7.7 Unsupported

**Input:** Any unrecognized query
**Status:** `unsupported`
**Suggestions:** Alternative queries the user can try

---

## 8. Conversation Context

The backend must maintain conversation state across requests. The frontend sends the current context with each request.

### Context Flow

```
Request 1: "Who are the most prolific authors?"
  → Context: { filters: [], target_facet: null, sorting: null }
  → Response: { target_facet: "author", sort: { field: "publications", direction: "desc" } }

Request 2: "Only consider the last five years"
  → Context: { filters: [], target_facet: "author", sorting: { field: "publications", direction: "desc" } }
  → Response: { filters: [{ facet: "year", value: "2020-2025" }], ... }

Request 3: "Which venues do they publish in?"
  → Context: { filters: [{ facet: "year", value: "2020-2025" }], target_facet: "author" }
  → Response: { target_facet: "venue", filters: [{ facet: "year", value: "2020-2025" }] }
```

### Key Rules

1. **Filters persist** — If the user applied a filter in a previous turn, it carries forward unless explicitly removed
2. **Target facet changes** — The backend determines the new target facet based on the query
3. **Sorting updates** — The backend recommends a sort order based on the result type
4. **Context is advisory** — The backend may ignore or modify context if the query requires it

---

## 9. LLM Integration

The backend must use an LLM for two purposes:

### 9.1 Intent Parsing

Parse the user's natural language query into:
- Target facet (author, venue, year, publication)
- Filters to apply
- Sort order
- Result type (facet_table, comparison, timeline, summary)

### 9.2 Observation Generation

After retrieving data from the knowledge graph, the LLM should generate:
- **Observations** — Key insights about the data (1-3 per response)
- **Suggestions** — Follow-up questions the user might ask (2-3 per response)

### 9.3 Unsupported Handling

When the LLM cannot map the query to a valid exploration:
- Set `status: "unsupported"`
- Provide observations explaining the limitation
- Provide suggestions for alternative queries

---

## 10. Migration Guide

### Current Backend State

The current `backend/main/` has:

```python
# schemas.py
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    type: str  # "sparql", "table", or "error"
    content: str  # Raw text
```

```python
# main.py
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    # Returns raw SPARQL or table text
```

### Migration Steps

1. **Update `schemas.py`** — Replace `ChatResponse` with `ExplorationResponse` (see Section 5)
2. **Add conversation management** — Store conversation state per `conversation_id`
3. **Integrate LLM for intent parsing** — Replace hardcoded SPARQL generation with LLM-based intent extraction
4. **Add observation generation** — Use LLM to generate insights from query results
5. **Add suggestion generation** — Use LLM to generate follow-up questions
6. **Update route** — Change `POST /chat` to `POST /api/exploration`

### New schemas.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Facet(str, Enum):
    author = "author"
    venue = "venue"
    year = "year"
    publication = "publication"

class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"

class Filter(BaseModel):
    facet: Facet
    value: str
    label: str

class SortState(BaseModel):
    field: str
    direction: SortDirection

class ResultColumn(BaseModel):
    key: str
    label: str
    type: str  # "text", "number", "badge", "link"
    sortable: bool = False

class ResultState(BaseModel):
    type: str  # "facet_table", "entity_list", "comparison", "timeline", "summary"
    title: str
    columns: list[ResultColumn]
    rows: list[dict]

class Observation(BaseModel):
    id: str
    text: str
    source: str = "llm"

class FollowUpQuestion(BaseModel):
    id: str
    text: str

class InterpretationState(BaseModel):
    observations: list[Observation]
    suggestions: list[FollowUpQuestion]

class ExplorationContext(BaseModel):
    target_facet: Optional[Facet] = None
    filters: list[Filter] = []
    sort: Optional[SortState] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    context: Optional[ExplorationContext] = None

class ExplorationResponse(BaseModel):
    status: str  # "answerable", "unsupported", "error"
    conversation_id: str
    exploration: ExplorationContext
    result: ResultState
    interpretation: InterpretationState
    sparql_query: Optional[str] = None  # Only when status == "answerable"
```

---

## 11. TypeScript Types Reference

The frontend defines these types in `src/lib/types/exploration.ts`. The backend should return JSON that matches these shapes.

```typescript
type Facet = 'author' | 'venue' | 'year' | 'publication';
type ResultType = 'facet_table' | 'entity_list' | 'comparison' | 'timeline' | 'summary';
type SortDirection = 'asc' | 'desc';
type ResponseStatus = 'answerable' | 'unsupported' | 'error';

interface Filter {
  facet: Facet;
  value: string;
  label: string;
}

interface SortState {
  field: string;
  direction: SortDirection;
}

interface ResultColumn {
  key: string;
  label: string;
  type: 'text' | 'number' | 'badge' | 'link';
  sortable?: boolean;
}

interface ResultRow {
  [key: string]: string | number;
}

interface ResultState {
  type: ResultType;
  columns: ResultColumn[];
  rows: ResultRow[];
  title?: string;
}

interface Observation {
  id: string;
  text: string;
  source: 'llm';
}

interface FollowUpQuestion {
  id: string;
  text: string;
}

interface InterpretationState {
  observations: Observation[];
  suggestions: FollowUpQuestion[];
}

interface ExplorationResponse {
  status: ResponseStatus;
  conversation_id: string;
  exploration: {
    targetFacet: Facet | null;
    filters: Filter[];
    sort: SortState | null;
  };
  result: ResultState;
  interpretation: InterpretationState;
  sparql_query?: string;
}
```

---

## 12. Testing the API

### cURL Examples

**Health check:**
```bash
curl http://localhost:8000/api/health
```

**Send a query:**
```bash
curl -X POST http://localhost:8000/api/exploration \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Who are the most prolific authors?",
    "conversation_id": "test-123",
    "context": {
      "filters": [],
      "target_facet": null,
      "sorting": null
    }
  }'
```

**Follow-up query:**
```bash
curl -X POST http://localhost:8000/api/exploration \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Only consider the last five years",
    "conversation_id": "test-123",
    "context": {
      "filters": [],
      "target_facet": "author",
      "sorting": { "field": "publications", "direction": "desc" }
    }
  }'
```

### Validation Checklist

- [ ] Response has `status` field
- [ ] Response has `exploration` context
- [ ] Response has `result` with `type`, `title`, `columns`, `rows`
- [ ] Response has `interpretation` with `observations` and `suggestions`
- [ ] Column `key` values match row object keys
- [ ] Sortable columns have `sortable: true`
- [ ] Observations have `source: "llm"`
- [ ] Unsupported queries return `status: "unsupported"` with suggestions
