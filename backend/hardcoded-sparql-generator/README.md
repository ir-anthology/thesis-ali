# Conversational Knowledge Graph Backend

Backend API for the conversational knowledge graph project.

## Setup

```bash
uv sync
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

Server starts at `http://127.0.0.1:8000`.

## API Endpoints

### `GET /health`

Health check.

**Response:**
```json
{"status": "ok"}
```

### `POST /sparql`

Returns a SPARQL query for DBLP publications.

**Request:**
```json
{"request": "List publications with authors, venues, and years"}
```

**Response:**
```json
{
  "sparql": "PREFIX dblp: <https://dblp.org/rdf/schema#>\n\nSELECT ..."
}
```

### `POST /results`

Returns query results as a markdown table.

**Request:**
```json
{"sparql": "PREFIX dblp: <https://dblp.org/rdf/schema#> SELECT ..."}
```

**Response:**
```json
{
  "table": "|  # | ?pubTitle | ?Authors | ... |\n| -: | ... | ... |"
}
```

## Project Structure

```
app/
  __init__.py
  main.py        # FastAPI app and endpoints
  schemas.py     # Pydantic v2 request/response models
pyproject.toml   # Project config (uv + hatch)
```
