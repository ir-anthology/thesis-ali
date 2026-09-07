# Backend API Guide: Frontend Consumption Contract

**Application:** Adaptive Conversational Knowledge Graph Explorer
**Frontend:** `frontend/adaptive/` (SvelteKit)
**Backend:** `backend/main/` (FastAPI + Python)
**Date:** September 2026

---

## 1. Overview

This guide defines the API contract between the IR Anthology Chat frontend and backend. The frontend is a conversation-driven adaptive UI that renders structured exploration results from a scholarly knowledge graph. The backend must return **semantic exploration state** — not raw SPARQL or text — so the frontend can dynamically render the appropriate visualization.

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
2. **Response is flat** — optional fields for text, table data, observations, and suggestions
3. **Backend is stateless** — frontend sends the full conversation history with each request
4. **LLM generates insights** — observations and follow-up questions come from the backend
5. **Cell values include questions** — each table cell has a clickable question for drill-down

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
  "interpretation": "User is asking for the most prolific authors based on publication count.",
  "columns": [
    { "key": "author", "label": "Author", "type": "text", "sortable": true },
    { "key": "publications", "label": "Publications", "type": "number", "sortable": true },
    { "key": "venues", "label": "Venues", "type": "number", "sortable": true },
    { "key": "years", "label": "Years", "type": "text" }
  ],
  "rows": [
    {
      "author": { "value": "Marti A. Hearst", "question": "Tell me about Marti A. Hearst" },
      "publications": { "value": 42, "question": "How many publications does Marti A. Hearst have?" },
      "venues": { "value": 12, "question": "Which venues does Marti A. Hearst publish in?" },
      "years": { "value": "1995–2024", "question": "What years was Marti A. Hearst active?" }
    },
    {
      "author": { "value": "Ryen W. White", "question": "Tell me about Ryen W. White" },
      "publications": { "value": 38, "question": "How many publications does Ryen W. White have?" },
      "venues": { "value": 10, "question": "Which venues does Ryen W. White publish in?" },
      "years": { "value": "2003–2024", "question": "What years was Ryen W. White active?" }
    }
  ],
  "observations": ["Marti A. Hearst leads with 42 publications spanning nearly three decades."],
  "suggestions": ["Who are the most prolific authors?", "What about citation counts?", "Tell me about something"],
  "sparql_query": "PREFIX schema: <http://schema.org/>\nPREFIX dcterms: <http://purl.org/dc/terms/>\n\nSELECT ?author\n       (COUNT(?pub) AS ?publications)\n       (COUNT(DISTINCT ?venue) AS ?venues)\n       (CONCAT(MIN(STR(?year)), \"–\", MAX(STR(?year))) AS ?years)\nWHERE {\n  ?pub a schema:ScholarlyArticle ;\n       dcterms:creator ?author ;\n       schema:isPartOf ?venue ;\n       dcterms:date ?year .\n}\nGROUP BY ?author\nORDER BY DESC(?publications)\nLIMIT 5"
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
| `interpretation` | string | No | Backend's interpretation of the query (assistant turns only) |
| `columns` | ResultColumn[] | No | Column definitions (assistant turns only) |
| `rows` | ResultRow[] | No | Data rows (assistant turns only) |
| `observations` | string[] | No | LLM-generated insights (assistant turns only) |
| `suggestions` | string[] | No | Follow-up suggestions (assistant turns only) |
| `sparql_query` | string | No | The SPARQL query used (assistant turns only) |

---

## 5. Response Schema

### ExplorationResponse

The response is a flat object. All fields are optional except the backend should always return at least one text field.

| Field | Type | Description |
|-------|------|-------------|
| `interpretation` | string | Backend's interpretation of the query (optional) |
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

### CellValue

Each cell in a row is a `CellValue` object with a display value and a clickable question.

| Field | Type | Description |
|-------|------|-------------|
| `value` | string \| number | The display value for the cell |
| `question` | string | The question sent as a user message when the cell is clicked. If empty/null, no tooltip or click handler. |

### ResultRow

A JSON object where keys match column `key` values. Each value is a `CellValue`.

```json
{
  "author": { "value": "Marti A. Hearst", "question": "Tell me about Marti A. Hearst" },
  "publications": { "value": 42, "question": "How many publications does Marti A. Hearst have?" },
  "venues": { "value": 12, "question": "Which venues does Marti A. Hearst publish in?" },
  "years": { "value": "1995–2024", "question": "What years was Marti A. Hearst active?" }
}
```

---

## 6. Response Structure

The response is a flat object with optional fields. The UI renders only what's present.

### Answerable Query (with table data)

```json
{
  "intent": "User is asking for the most prolific authors based on publication count.",
  "columns": [
    { "key": "author", "label": "Author", "type": "text", "sortable": true },
    { "key": "publications", "label": "Publications", "type": "number", "sortable": true }
  ],
  "rows": [
    {
      "author": { "value": "Marti A. Hearst", "question": "Tell me about Marti A. Hearst" },
      "publications": { "value": 42, "question": "How many publications does Marti A. Hearst have?" }
    }
  ],
  "observations": ["Marti A. Hearst leads with 42 publications."],
  "suggestions": ["Who are the most prolific authors?", "What about citation counts?", "Tell me about something"],
  "sparql_query": "PREFIX schema: <http://schema.org/> ..."
}
```

### Unsupported Query (no table data)

```json
{
  "interpretation": "I don't have data on citation counts. The knowledge graph only contains information about authors, venues, and publications.",
  "suggestions": ["Who are the most prolific authors?", "What about citation counts?", "Tell me about something"]
}
```

### Clarification Needed

```json
{
  "interpretation": "Could you clarify whether you are looking for authors, venues, or publications?",
  "suggestions": ["Who are the most prolific authors?", "What about citation counts?", "Tell me about something"]
}
```

### Key Rules

1. **`interpretation`** — Backend's interpretation of the query (what the user is asking, clarification, or limitation).
2. **`columns` + `rows`** — Present together for tabular data. Absent for unsupported queries. Each row value must be a `CellValue` object.
3. **`observations`** — Optional. LLM-generated insights about the data.
4. **`suggestions`** — Optional. Follow-up questions the user might ask.
5. **`sparql_query`** — Optional. The SPARQL query used to retrieve data.
6. **Cell questions** — If a cell's `question` is empty/null, no tooltip or click handler is shown for that cell.

---

## 7. Conversation Context

The backend is **stateless**. The frontend sends the full conversation history with each request.

### Context Flow

```
Request 1: { message: "Who are the most prolific authors?", history: [] }
  → Response: { interpretation: "...", columns: [...], rows: [...] }

Request 2: { message: "Only consider the last five years", history: [
    { role: "user", content: "Who are the most prolific authors?" },
    { role: "assistant", content: "...", interpretation: "...", columns: [...], rows: [...] }
  ]}
  → Response: { interpretation: "...", columns: [...], rows: [...] }

Request 3: { message: "Which venues do they publish in?", history: [
    { role: "user", content: "Who are the most prolific authors?" },
    { role: "assistant", content: "...", interpretation: "...", columns: [...], rows: [...] },
    { role: "user", content: "Only consider the last five years" },
    { role: "assistant", content: "...", interpretation: "...", columns: [...], rows: [...] }
  ]}
  → Response: { interpretation: "...", columns: [...], rows: [...] }
```

### Key Rules

1. **Backend is stateless** — No session storage needed. Each request contains all required context.
2. **History is advisory** — The backend may ignore or modify context if the query requires it.
3. **First message has empty history** — `history: []` for the initial request.
4. **Loading turns excluded** — The frontend filters out turns with `loading: true` from history.

---

## 8. LLM Integration

The backend must use an LLM for two purposes:

### 8.1 Query Interpretation

Parse the user's natural language query into:
- **interpretation** — A sentence describing what the user is asking or clarifying (e.g., "User is asking for the most prolific authors based on publication count.")

### 8.2 Observation & Suggestion Generation

After retrieving data from the knowledge graph, the LLM should generate:
- **Observations** — Key insights about the data (1-3 per response)
- **Suggestions** — Follow-up questions the user might ask (2-3 per response)

### 8.3 Unsupported Handling

When the LLM cannot map the query to a valid exploration:
- Set `interpretation` with an explanation of the limitation
- Provide `suggestions` for alternative queries
- Do NOT include `columns` or `rows`

---

## 9. Migration Guide

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
2. **Integrate LLM for query interpretation** — Replace hardcoded SPARQL generation with LLM-based interpretation
3. **Add observation generation** — Use LLM to generate insights from query results
4. **Add suggestion generation** — Use LLM to generate follow-up questions
5. **Update route** — Change `POST /chat` to `POST /api/exploration`
6. **Add CellValue to rows** — Each cell must return `{ value, question }` objects

### New schemas.py

```python
from pydantic import BaseModel
from typing import Optional

class ResultColumn(BaseModel):
    key: str
    label: str
    type: str  # "text", "number", "badge", "link"
    sortable: bool = False

class CellValue(BaseModel):
    value: str | int | float
    question: str

class HistoryTurn(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    interpretation: Optional[str] = None
    columns: Optional[list[ResultColumn]] = None
    rows: Optional[list[dict[str, CellValue]]] = None
    observations: Optional[list[str]] = None
    suggestions: Optional[list[str]] = None
    sparql_query: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    history: list[HistoryTurn] = []

class ExplorationResponse(BaseModel):
    interpretation: Optional[str] = None
    columns: Optional[list[ResultColumn]] = None
    rows: Optional[list[dict[str, CellValue]]] = None
    observations: Optional[list[str]] = None
    suggestions: Optional[list[str]] = None
    sparql_query: Optional[str] = None
```

---

## 10. TypeScript Types Reference

The frontend defines these types in `src/lib/types/exploration.ts`. The backend should return JSON that matches these shapes.

```typescript
interface ResultColumn {
  key: string;
  label: string;
  type: 'text' | 'number' | 'badge' | 'link';
  sortable?: boolean;
}

interface CellValue {
  value: string | number;
  question: string;
}

interface ResultRow {
  [key: string]: CellValue;
}

interface HistoryTurn {
  role: 'user' | 'assistant';
  content: string;
  interpretation?: string;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}

interface ExplorationResponse {
  interpretation?: string;
  columns?: ResultColumn[];
  rows?: ResultRow[];
  observations?: string[];
  suggestions?: string[];
  sparql_query?: string;
}
```

---

## 11. Testing the API

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
        "content": "User is asking for the most prolific authors based on publication count.",
        "interpretation": "User is asking for the most prolific authors based on publication count.",
        "columns": [
          {"key": "author", "label": "Author", "type": "text", "sortable": true},
          {"key": "publications", "label": "Publications", "type": "number", "sortable": true}
        ],
        "rows": [
          {
            "author": {"value": "Marti A. Hearst", "question": "Tell me about Marti A. Hearst"},
            "publications": {"value": 42, "question": "How many publications does Marti A. Hearst have?"}
          }
        ],
        "observations": ["Marti A. Hearst leads with 42 publications."],
        "suggestions": ["Who are the most prolific authors?", "What about citation counts?", "Tell me about something"]
      }
    ]
  }'
```

### Validation Checklist

- [ ] Request has `message` and `history` fields
- [ ] Response has `interpretation` field
- [ ] If `columns` present, `rows` must also be present
- [ ] Each row value is a `CellValue` object with `value` and `question` fields
- [ ] Column `key` values match row object keys
- [ ] Sortable columns have `sortable: true`
- [ ] Unsupported queries have `interpretation` explaining the limitation and `suggestions` (no `columns`/`rows`)
- [ ] All 3 suggestions are consistent across responses
