# DBLP Exploration API - Frontend Integration Guide

## Base URL

```
http://localhost:8000
```

## Endpoints

### POST `/api/exploration`

Main endpoint for exploring DBLP publications using natural language queries.

**Request Body:**

```json
{
  "message": "Which papers did Geoffrey Hinton author?",
  "history": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | `string` | Yes | Natural language query about DBLP |
| `history` | `array` | No | Conversation history (see History Object below) |

**History Object:**

```json
{
  "role": "user",
  "content": "Which papers did Geoffrey Hinton author?",
  "interpretation": null,
  "columns": null,
  "rows": null,
  "observations": null,
  "suggestions": null,
  "sparql_query": null
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | `string` | Yes | `"user"` or `"assistant"` |
| `content` | `string` | Yes | Message content |
| `interpretation` | `string` | No | Backend's interpretation of the query (assistant only) |
| `columns` | `array` | No | Column definitions (see below) |
| `rows` | `array` | No | Data rows (see below) |
| `observations` | `array` | No | LLM-generated insights |
| `suggestions` | `array` | No | Follow-up suggestions |
| `sparql_query` | `string` | No | SPARQL query used |

**Response - Three Outcome Types:**

The response always has a single `interpretation` field that describes what happened. The meaning changes based on the outcome:

#### 1. Clear & Answerable (data returned)

```json
{
  "interpretation": "Let me find the papers by Geoffrey Hinton",
  "columns": [
    { "key": "pub", "label": "Pub", "type": "text", "sortable": true },
    { "key": "title", "label": "Title", "type": "text", "sortable": true },
    { "key": "year", "label": "Year", "type": "text", "sortable": true }
  ],
  "rows": [
    {
      "pub": {
        "value": "https://dblp.org/rec/journals/corr/abs-1701-00160",
        "question": "Tell me about this publication"
      },
      "title": {
        "value": "Dynamic Routing Between Capsules",
        "question": "Tell me about the paper 'Dynamic Routing Between Capsules'"
      },
      "year": {
        "value": "2017",
        "question": "What papers did Geoffrey Hinton publish in 2017?"
      }
    }
  ],
  "observations": [
    "Geoffrey Hinton has published papers spanning over three decades."
  ],
  "suggestions": [
    "Show me Geoffrey Hinton's publications from 2023",
    "Who are Geoffrey Hinton's co-authors?"
  ],
  "sparql_query": "PREFIX dblp: <https://dblp.org/rdf/schema#>\nSELECT ?pub ?title ?year WHERE { ... }"
}
```

**Column Object:**

| Field | Type | Description |
|-------|------|-------------|
| `key` | `string` | Column identifier (matches SPARQL variable) |
| `label` | `string` | Human-readable display label |
| `type` | `string` | `"text"`, `"number"`, `"badge"`, or `"link"` |
| `sortable` | `boolean` | Whether column is sortable |

**Row Cell Object:**

| Field | Type | Description |
|-------|------|-------------|
| `value` | `string\|number` | The cell value |
| `question` | `string` | Natural language follow-up question |

#### 2. Clarification Needed (ambiguity)

```json
{
  "interpretation": "Multiple authors found for 'Smith'. Which one did you mean?",
  "suggestions": [
    "Show me papers by John Smith",
    "Show me papers by Mike Smith",
    "Show me papers by Sarah Smith"
  ]
}
```

#### 3. Out of Scope (limitation)

```json
{
  "interpretation": "DBLP does not track citation counts. Consider using Semantic Scholar or Google Scholar.",
  "suggestions": [
    "How many publications does this author have?",
    "Show me papers by this author"
  ]
}
```

**Response Fields Summary:**

| Field | Type | Description |
|-------|------|-------------|
| `interpretation` | `string\|null` | Backend's interpretation of the query. For clear: first-person description ("Let me find..."). For ambiguous: clarification question. For out_of_scope: limitation explanation. |
| `columns` | `array\|null` | Column definitions (clear outcome only) |
| `rows` | `array\|null` | Data rows with cell values and questions (clear outcome only) |
| `observations` | `array\|null` | LLM-generated insights about the data (clear outcome only) |
| `suggestions` | `array\|null` | Follow-up query suggestions (all outcomes) |
| `sparql_query` | `string\|null` | Generated SPARQL query (clear outcome only) |

---

### POST `/api/sus`

Submit a completed System Usability Scale questionnaire when the participant
presses **Submit answers**:

```http
POST /api/sus
Content-Type: application/json
X-Session-Id: 123e4567-e89b-12d3-a456-426614174000
```

```json
{
  "questionnaire": "SUS",
  "version": "brooke-1996",
  "answers": [4, 2, 4, 1, 5, 2, 4, 1, 4, 2]
}
```

Exactly these fields are accepted. Answers must be exactly ten JSON integers
from 1 through 5 in question order. Booleans, floats, and numeric strings are
rejected. Conversation history and identity fields must not be included.

Reuse the UUID sent with conversation requests as `X-Session-Id` so the results
can be analyzed together. UUIDs are normalized to lowercase. The header is
optional; submissions without it are stored with a null session ID. An invalid
supplied header returns `400`. The ID is pseudonymous and does not authenticate
the participant. CORS permits this header.

Explicit survey submissions are stored independently of `X-Analytics-Enabled`.
Each accepted submission creates a new record, including repeated submissions
from the same session. Missing conversation records do not prevent submission.

Odd items contribute `answer - 1`; even items contribute `5 - answer`. The sum
is multiplied by 2.5, giving a score on the 0–100 scale, not a percentage. The
example scores **82.5**. The server stores the ordered raw answers, score,
questionnaire/version, optional session ID, submission UUID, and UTC timestamp.

After the database transaction commits, return **201 Created**:

```json
{
  "status": "accepted",
  "submission_id": "server-generated-uuid"
}
```

Invalid fields, ratings, malformed JSON, or an invalid supplied session ID
return **400 Bad Request** with a `detail` message. Storage failure returns
**500 Internal Server Error**. Show success only for an HTTP success response;
otherwise keep the modal and answers available for retry.

### GET `/api/health`

Health check endpoint.

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

### GET `/docs`

Auto-generated API documentation (Swagger UI).

---

## Frontend Handling Guide

### Check Response Type

```javascript
// Determine which outcome occurred based on columns/rows presence
if (response.columns && response.rows) {
  // Clear - show data table
  // Use response.interpretation as the header/summary
  // Use response.columns for table headers
  // Use response.rows for table data
  // Use response.observations for insights panel
} else if (response.suggestions && response.suggestions.length > 0) {
  // Check if interpretation looks like a clarification or limitation
  // Both ambiguous and out_of_scope have suggestions but no columns/rows
  // Display response.interpretation as the message
  // Show response.suggestions as clickable options
} else {
  // Empty/unexpected response
  // Display response.interpretation if present
}
```

### Data Table Rendering

```javascript
// Render table from response
const renderTable = (response) => {
  const columns = response.columns;
  const rows = response.rows;

  // Columns define table structure
  columns.forEach(col => {
    console.log(`${col.label} (${col.type})`);
  });

  // Each row has cells with value + question
  rows.forEach(row => {
    columns.forEach(col => {
      const cell = row[col.key];
      // cell.value - display this
      // cell.question - can be used as tooltip or follow-up
    });
  });
};
```

### Handling Cell Questions

Each cell in a data row includes a `question` field that can be:

1. **Sent as follow-up query** when user clicks on a cell
2. **Displayed as tooltip** to show available actions
3. **Used for drill-down navigation**

```javascript
// When user clicks on a cell
const handleCellClick = (cell) => {
  // Send the cell's question as a new query
  sendMessage(cell.question);
};
```

### Conversation History

To maintain conversation context, send back the history:

```javascript
const buildHistory = (messages) => {
  return messages.map(msg => ({
    role: msg.role,
    content: msg.content,
    interpretation: msg.interpretation || null,
    columns: msg.columns || null,
    rows: msg.rows || null,
    observations: msg.observations || null,
    suggestions: msg.suggestions || null,
    sparql_query: msg.sparql_query || null
  }));
};
```

### Suggestions as Quick Actions

Display suggestions as clickable chips or buttons:

```javascript
// Render suggestions
const renderSuggestions = (suggestions) => {
  return suggestions.map(suggestion => (
    <button onClick={() => sendMessage(suggestion)}>
      {suggestion}
    </button>
  ));
};
```

---

## Example User Flows

### Flow 1: Clear Query

```
User: "Papers by Geoffrey Hinton"
  → Response: interpretation="Let me find papers by Geoffrey Hinton", columns/rows present
  → UI: Show data table

User: (clicks on a cell with question "Tell me about Geoffrey Hinton")
  → Response: interpretation="Let me find information about Geoffrey Hinton", columns/rows present
  → UI: Show author info table
```

### Flow 2: Ambiguous Query

```
User: "Papers by Smith"
  → Response: interpretation="Multiple authors named Smith...", suggestions=[3 options]
  → UI: Show clarification message + clickable suggestion chips

User: (clicks "Show me papers by John Smith")
  → Response: interpretation="Let me find papers by John Smith", columns/rows present
  → UI: Show data table
```

### Flow 3: Out of Scope

```
User: "How many citations does this paper have?"
  → Response: interpretation="DBLP does not track citation counts...", suggestions=[alternatives]
  → UI: Show limitation message + alternative suggestions
```

### Flow 4: With History

```
User: "Papers by Geoffrey Hinton"
  → Response: columns/rows with papers
  → History updated with user + assistant messages

User: "Only from 2023" (with history)
  → Response: filtered papers from 2023
  → UI: Updated table
```

---

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Exploration success, including clarification/limitation |
| `201` | SUS submission stored |
| `400` | Invalid SUS submission or supplied session UUID |
| `500` | Server error; SUS storage failures return a `detail` message |

**Note:** Clarification and limitation responses return `200` status, not error codes. The response type is determined by the presence of `columns`/`rows` fields.
