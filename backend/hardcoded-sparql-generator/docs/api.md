# API Reference

**Base URL:** `http://127.0.0.1:8000`

---

## Endpoints

### `GET /health`

Health check endpoint.

**Response** `200 OK`:

```json
{
  "status": "ok"
}
```

---

### `POST /chat`

Single endpoint that handles both natural language requests and SPARQL queries.

- **Natural language input:** Returns a hardcoded SPARQL query (not executed).
- **SPARQL input:** Executes against the DBLP endpoint and returns results as a markdown table.

**Request** `POST /chat`:

```json
{
  "message": "List publications with authors, venues, and years"
}
```

| Field     | Type   | Required | Description                                    |
| --------- | ------ | -------- | ---------------------------------------------- |
| `message` | string | Yes      | User message (natural language or SPARQL query) |

**Response — SPARQL (natural language input)** `200 OK`:

```json
{
  "type": "sparql",
  "content": "PREFIX dblp: <https://dblp.org/rdf/schema#>\n\nSELECT ..."
}
```

**Response — Table (SPARQL input)** `200 OK`:

```json
{
  "type": "table",
  "content": "|  # | ?pubTitle | ?Authors | ?Venues | ?Years |\n| -: | --- | --- | --- | --- |\n|  1 | Example Publication | 2 | 1 | 2024 |"
}
```

**Response — Error** `200 OK`:

```json
{
  "type": "error",
  "content": "SPARQL query timed out"
}
```

| Field     | Type   | Description                                              |
| --------- | ------ | -------------------------------------------------------- |
| `type`    | string | `"sparql"`, `"table"`, or `"error"`                      |
| `content` | string | SPARQL query, markdown table, or error message           |

**cURL — Natural Language:**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List publications with authors, venues, and years"}'
```

**cURL — SPARQL:**

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "PREFIX dblp: <https://dblp.org/rdf/schema#> SELECT ?pubTitle WHERE { ?pub dblp:title ?pubTitle } LIMIT 10"}'
```

---

## Error Responses

### `422 Validation Error`

Returned when request body fails validation.

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required",
      "input": {},
      "url": "https://errors.pydantic.dev/2.11/missing"
    }
  ]
}
```

### Application Errors

Returned in the response body when SPARQL execution fails:

| Error Message | Cause |
| ------------- | ----- |
| `SPARQL query timed out` | Query took longer than 30 seconds |
| `SPARQL endpoint returned {status_code}` | DBLP endpoint returned an error |
| `Failed to parse SPARQL results: {error}` | Unexpected response format |

---

## Architecture

```
User → POST /chat → router.is_sparql(message)
                     ├─ Yes → sparql_executor.execute(sparql) → table_formatter.format(results)
                     │                                                  ↓
                     │                                      {type: "table", content: "..."}
                     │
                     └─ No  → sparql_generator.execute(nl) → {type: "sparql", content: "..."}
```

| Agent              | Module                           | Responsibility                           |
| ------------------ | -------------------------------- | ---------------------------------------- |
| Router             | `app/agents/router.py`           | Detects if input is SPARQL or NL         |
| SPARQL Generator   | `app/agents/sparql_generator.py` | Generates SPARQL from NL request         |
| SPARQL Executor    | `app/agents/sparql_executor.py`  | Executes SPARQL against DBLP endpoint    |
| Table Formatter    | `app/agents/table_formatter.py`  | Converts SPARQL JSON results to table    |

---

## UI Implementation Notes

1. **Single input:** Provide one text input for the user to type either natural language or SPARQL.
2. **Response handling:** Check the `type` field in the response:
   - `"sparql"` → display the SPARQL query in a code block. The user can edit and resubmit it.
   - `"table"` → parse and render the markdown table.
   - `"error"` → display the error message.
3. **Table rendering:** The `content` field contains standard markdown. Use a markdown renderer or parse the pipe-delimited format into an HTML `<table>`.
4. **Loading state:** The DBLP endpoint may take a few seconds. Show a loading indicator when `type` is `"table"`.
5. **Error handling:** Show the `content` field as an error message when `type` is `"error"`.
