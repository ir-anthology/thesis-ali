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
  "history": []
}
```

**Follow-up Request (with conversation history):**

```json
{
  "message": "Only consider the last five years",
  "history": [
    {
      "role": "user",
      "content": "Who are the most prolific authors?"
    },
    {
      "role": "assistant",
      "content": "Here are the results:",
      "result": {
        "type": "facet_table",
        "title": "Most Prolific Authors in Exploratory Search",
        "columns": [...],
        "rows": [...]
      },
      "observations": [...],
      "suggestions": [...],
      "sparql_query": "PREFIX ...",
      "status": "answerable"
    }
  ]
}
```

**Response:**

```json
{
  "intent": "User is asking for the most prolific authors based on publication count.",
  "columns": [
    { "key": "author", "label": "Author", "type": "text", "sortable": true },
    { "key": "publications", "label": "Publications", "type": "number", "sortable": true },
    { "key": "venues", "label": "Venues", "type": "number", "sortable": true },
    { "key": "years", "label": "Years", "type": "text" }
  ],
  "rows": [
    { "author": "Marti A. Hearst", "publications": 42, "venues": 12, "years": "1995–2024" },
    { "author": "Ryen W. White", "publications": 38, "venues": 10, "years": "2003–2024" }
  ],
  "observations": ["Marti A. Hearst leads with 42 publications spanning nearly three decades."],
  "suggestions": ["Only consider the last five years", "Which venues do these authors publish in?", "Show me how this changed over time"],
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
| `history` | HistoryTurn[] | Yes | Previous conversation turns (empty array for first message) |

### HistoryTurn

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | Yes | `"user"` or `"assistant"` |
| `content` | string | Yes | The message text |
| `intent` | string | No | Backend's understanding of user intent (assistant turns only) |
| `clarification` | string | No | Backend asks user for more info (assistant turns only) |
| `limitation` | string | No | Query cannot be answered with available data (assistant turns only) |
| `columns` | ResultColumn[] | No | Column definitions (assistant turns only) |
| `rows` | ResultRow[] | No | Data rows (assistant turns only) |
| `observations` | string[] | No | LLM-generated insights (assistant turns only) |
| `suggestions` | string[] | No | Follow-up suggestions (assistant turns only) |
| `sparql_query` | string | No | The SPARQL query used (assistant turns only) |

---

## 5. Response Schema

### ExplorationResponse

| Field | Type | Description |
|-------|------|-------------|
| `intent` | string | Backend's understanding of user intent (optional) |
| `clarification` | string | Backend asks user for more info (optional) |
| `limitation` | string | Query cannot be answered with available data (optional) |
| `columns` | ResultColumn[] | Column definitions for tabular data (optional) |
| `rows` | ResultRow[] | Data rows (optional) |
| `observations` | string[] | LLM-generated insights (optional) |
| `suggestions` | string[] | Recommended follow-up queries (optional) |
| `sparql_query` | string | The SPARQL query used (optional) |

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

---

## 6. Response Structure

The response is a flat object with optional fields. The UI renders only what's present.

### Answerable Query (with table data)

```json
{
  "intent": "User is asking for the most prolific authors based on publication count.",
  "columns": [...],
  "rows": [...],
  "observations": ["..."],
  "suggestions": ["..."],
  "sparql_query": "PREFIX ..."
}
```

### Unsupported Query (no table data)

```json
{
  "intent": "User is asking about a topic that cannot be answered with available data.",
  "limitation": "I don't have data on this topic.",
  "suggestions": ["Try asking about authors", "Ask about venues"]
}
```

### Clarification Needed

```json
{
  "intent": "User is asking about authors or venues.",
  "clarification": "Did you mean authors or venues?",
  "suggestions": ["Show me authors", "Show me venues"]
}
```

### Key Rules

1. **`intent`** — Backend's understanding of user intent. Rendered first if present.
2. **`limitation`** — Query cannot be answered. Rendered second if present.
3. **`clarification`** — Backend asks for more info. Rendered third if present.
4. **`columns` + `rows`** — Present together for tabular data. Absent for unsupported queries.
5. **`observations`** — Optional. LLM-generated insights about the data.
6. **`suggestions`** — Optional. Follow-up questions the user might ask.
7. **`sparql_query`** — Optional. The SPARQL query used to retrieve data.
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
**Result Type:** `facet_table`
**Columns:** author, publications, venues, years

### 7.2 Filtered Results

**Input:** `"Only consider the last five years"`
**Result Type:** `facet_table`

### 7.3 Venue Pivot

**Input:** `"Which venues do they publish in?"`
**Result Type:** `facet_table`
**Columns:** venue, publications, authors, years

### 7.4 Timeline

**Input:** `"Show me how this changed over time"`
**Result Type:** `timeline`
**Columns:** year, [venue1], [venue2], ...

### 7.5 Comparison

**Input:** `"Compare SIGIR and CHIIR"`
**Result Type:** `comparison`
**Columns:** metric, [entity1], [entity2]

### 7.6 Explanation

**Input:** `"Why is SIGIR prominent?"`
**Result Type:** `summary`
**Observations:** Multiple LLM-generated insights

### 7.7 Unsupported

**Input:** Any unrecognized query
**Status:** `unsupported`
**Suggestions:** Alternative queries the user can try

---

## 8. Conversation Context

The backend is **stateless**. The frontend sends the full conversation history with each request.

### Context Flow

```
Request 1: { message: "Who are the most prolific authors?", history: [] }
  → Response: { result: facet_table with authors }

Request 2: { message: "Only consider the last five years", history: [
    { role: "user", content: "Who are the most prolific authors?" },
    { role: "assistant", content: "...", result: {...}, status: "answerable" }
  ]}
  → Response: { result: facet_table with filtered authors }

Request 3: { message: "Which venues do they publish in?", history: [
    { role: "user", content: "Who are the most prolific authors?" },
    { role: "assistant", content: "...", result: {...}, status: "answerable" },
    { role: "user", content: "Only consider the last five years" },
    { role: "assistant", content: "...", result: {...}, status: "answerable" }
  ]}
  → Response: { result: facet_table with venues }
```

### Key Rules

1. **Backend is stateless** — No session storage needed. Each request contains all required context.
2. **History is advisory** — The backend may ignore or modify context if the query requires it.
3. **First message has empty history** — `history: []` for the initial request.

---

## 9. LLM Integration

The backend must use an LLM for two purposes:

### 9.1 Intent Parsing

Parse the user's natural language query into:
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
2. **Integrate LLM for intent parsing** — Replace hardcoded SPARQL generation with LLM-based intent extraction
3. **Add observation generation** — Use LLM to generate insights from query results
4. **Add suggestion generation** — Use LLM to generate follow-up questions
5. **Update route** — Change `POST /chat` to `POST /api/exploration`

### New schemas.py

```python
from pydantic import BaseModel, Field
from typing import Optional

class ResultColumn(BaseModel):
    key: str
    label: str
    type: str  # "text", "number", "badge", "link"
    sortable: bool = False

class HistoryTurn(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    intent: Optional[str] = None
    clarification: Optional[str] = None
    limitation: Optional[str] = None
    columns: Optional[list[ResultColumn]] = None
    rows: Optional[list[dict]] = None
    observations: Optional[list[str]] = None
    suggestions: Optional[list[str]] = None
    sparql_query: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: list[HistoryTurn] = []

class ExplorationResponse(BaseModel):
    intent: Optional[str] = None
    clarification: Optional[str] = None
    limitation: Optional[str] = None
    columns: Optional[list[ResultColumn]] = None
    rows: Optional[list[dict]] = None
    observations: Optional[list[str]] = None
    suggestions: Optional[list[str]] = None
    sparql_query: Optional[str] = None
```

---

## 11. TypeScript Types Reference

The frontend defines these types in `src/lib/types/exploration.ts`. The backend should return JSON that matches these shapes.

```typescript
interface ResultColumn {
  key: string;
  label: string;
  type: 'text' | 'number' | 'badge' | 'link';
  sortable?: boolean;
}

interface ResultRow {
  [key: string]: string | number;
}

interface HistoryTurn {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  clarification?: string;
  limitation?: string;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}

interface ExplorationResponse {
  intent?: string;
  clarification?: string;
  limitation?: string;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
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
    "history": []
  }'
```

**Follow-up query:**
```bash
curl -X POST http://localhost:8000/api/exploration \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Only consider the last five years",
    "history": [
      {
        "role": "user",
        "content": "Who are the most prolific authors?"
      },
      {
        "role": "assistant",
        "content": "Here are the results:",
        "result": {
          "type": "facet_table",
          "title": "Most Prolific Authors",
          "columns": [
            {"key": "author", "label": "Author", "type": "text", "sortable": true},
            {"key": "publications", "label": "Publications", "type": "number", "sortable": true}
          ],
          "rows": [
            {"author": "Marti A. Hearst", "publications": 42}
          ]
        },
        "status": "answerable"
      }
    ]
  }'
```

### Validation Checklist

- [ ] Request has `message` and `history` fields
- [ ] Response has at least one of: `intent`, `clarification`, `limitation`
- [ ] If `columns` present, `rows` must also be present
- [ ] Column `key` values match row object keys
- [ ] Sortable columns have `sortable: true`
- [ ] Unsupported queries have `limitation` and `suggestions` (no `columns`/`rows`)
