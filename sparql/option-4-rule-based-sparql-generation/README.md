# Rule-Based SPARQL Generation for DBLP

A multi-step LLM pipeline for converting natural language questions to SPARQL queries against the DBLP Computer Science Bibliography, with a FastAPI service for frontend integration.

## Architecture

```
User Query + History
       ↓
Step 1: Query Interpretation (LLM #1)   → QueryInterpretation
       │
       ├── outcome="out_of_scope" → Limitation Response
       ├── outcome="ambiguous"    → Clarification Response
       └── outcome="clear"        ↓
                                  ↓
Step 2: SPARQL Generation (LLM #2)  → SPARQL (using entity names)
       ↓
Step 3: Validation (rules)          → ValidationResult
       ↓
Step 4: SPARQL Execution (DBLP)     → QueryExecutionResult
       ↓
Step 5: Response Formatting (LLM #3) → FormattedResponse
       ↓
Step 6: Observation Generation (LLM #4) → Observations
       ↓
ExplorationResponse (JSON)
```

**4 LLM calls**, no DBLP API calls (entity names used directly in SPARQL):
1. Query Interpretation (intent + entities + ambiguity detection)
2. SPARQL Generation (name-based lookups)
3. Response Formatting (cell questions)
4. Observation Generation

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
# Install dependencies using uv
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

### Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your-api-key-here
LLM_MODEL=gpt-5.6-luna
API_HOST=0.0.0.0
API_PORT=8000
MAX_RESULT_ROWS=50
QUESTION_BATCH_SIZE=10
```

## Usage

### FastAPI Server

```bash
# Start the server
uv run serve

# Or with custom port
API_PORT=8080 uv run serve
```

The server starts at `http://localhost:8000` with auto-generated docs at `http://localhost:8000/docs`.

### Interactive CLI

```bash
python main.py
```

### Single Query

```bash
python main.py "Which papers did Geoffrey Hinton author?"
```

### Run Tests

```bash
uv run pytest tests/ -v
```

## API Endpoints

### POST `/api/exploration`

Main exploration endpoint. Sends a user message with conversation history and returns structured exploration response.

**Request:**

```json
{
  "message": "Who are the most prolific authors?",
  "history": []
}
```

**Response:**

```json
{
  "interpretation": "Let me find the most prolific authors by publication count",
  "columns": [
    { "key": "author", "label": "Author", "type": "text", "sortable": true },
    { "key": "publications", "label": "Publications", "type": "number", "sortable": true }
  ],
  "rows": [
    {
      "author": { "value": "Geoffrey Hinton", "question": "Tell me about Geoffrey Hinton" },
      "publications": { "value": 42, "question": "How many publications does Geoffrey Hinton have?" }
    }
  ],
  "observations": ["Geoffrey Hinton leads with 42 publications spanning nearly three decades."],
  "suggestions": ["Show me Geoffrey Hinton's publications from 2023", "List Geoffrey Hinton's co-authors"],
  "sparql_query": "PREFIX dblp: ..."
}
```

### GET `/api/health`

Health check endpoint.

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### GET `/docs`

Auto-generated API documentation (Swagger UI).

## Output Format

### ExplorationResponse (success with data)

```json
{
  "interpretation": "Let me find the papers authored by Geoffrey Hinton",
  "columns": [
    { "key": "pub", "label": "Pub", "type": "text", "sortable": true },
    { "key": "title", "label": "Title", "type": "text", "sortable": true },
    { "key": "year", "label": "Year", "type": "text", "sortable": true }
  ],
  "rows": [
    {
      "pub": { "value": "https://dblp.org/rec/...", "question": "Tell me about this publication" },
      "title": { "value": "Dynamic Routing Between Capsules", "question": "Tell me about the paper 'Dynamic Routing Between Capsules'" },
      "year": { "value": "2017", "question": "What papers did Geoffrey Hinton publish in 2017?" }
    }
  ],
  "observations": ["Geoffrey Hinton's most recent publication is from 2025 on AI Safety."],
  "suggestions": ["Show me Geoffrey Hinton's publications from 2023", "What papers did Geoffrey Hinton publish at NeurIPS?"],
  "sparql_query": "PREFIX dblp: <https://dblp.org/rdf/schema#> ..."
}
```

### Limitation Response

```json
{
  "interpretation": "DBLP does not track citation counts between publications. Consider using Semantic Scholar or Google Scholar for citation data.",
  "suggestions": ["How many publications does Geoffrey Hinton have?", "Show me Geoffrey Hinton's publications"]
}
```

### Clarification Response

```json
{
  "interpretation": "Multiple authors found for 'Smith'. Which one did you mean?",
  "suggestions": ["Show me papers by John Smith", "Show me papers by Mike Smith", "Show me papers by Sarah Smith"]
}
```

### Clarification Response

```json
{
  "intent": "The user is asking for publications by Smith",
  "clarification": "There are multiple authors named Smith in DBLP. Which one did you mean?",
  "suggestions": ["Show me papers by John Smith", "Show me papers by Mike Smith", "Show me papers by Sarah Smith"]
}
```

## Supported Query Types

| Query Type | Example |
|------------|---------|
| Author publications | "Papers by Geoffrey Hinton" |
| Venue publications | "Papers at SIGMOD" |
| Author + Venue | "Papers by Hinton at NeurIPS" |
| Year filter | "Papers from 2023" |
| Publication type | "Journal articles by Smith" |
| Co-authors | "Co-authors of Yann LeCun" |
| Author metadata | "Affiliation of Michael Stonebraker" |
| Venue info | "Info about VLDB" |
| Count | "How many papers by Knuth?" |

## Limitations

The system detects and reports limitations for queries that require:

- Citation counts (not in DBLP)
- Abstracts/full text (not in DBLP)
- Impact factors (not in DBLP)
- Non-CS publications (out of scope)

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── config.py                  # Configuration
│   ├── models.py                  # Pydantic models
│   ├── prompts.py                 # LLM prompts
│   ├── query_interpreter.py       # Step 1: Unified query interpretation
│   ├── sparql_generator.py        # Step 2: SPARQL generation (name-based)
│   ├── validator.py               # Step 3: SPARQL validation
│   ├── sparql_executor.py         # Step 4: SPARQL execution
│   ├── response_formatter.py      # Step 5: Response formatting
│   ├── observation_generator.py   # Step 6: Observation generation
│   ├── pipeline.py                # Orchestrator
│   └── api.py                     # FastAPI application
├── tests/
│   ├── test_query_interpreter.py
│   ├── test_response_formatter.py
│   ├── test_sparql_executor.py
│   ├── test_validator.py
│   └── test_api.py
├── data/
│   └── examples.json              # Few-shot examples (name-based SPARQL)
├── main.py                        # CLI entry point
├── pyproject.toml                 # Project config
├── .env                           # Environment variables
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key |
| `LLM_MODEL` | `gpt-5.6-luna` | LLM model to use |
| `DBLP_SPARQL_ENDPOINT` | `https://sparql.dblp.org/sparql` | DBLP SPARQL endpoint |
| `API_HOST` | `0.0.0.0` | FastAPI server host |
| `API_PORT` | `8000` | FastAPI server port |
| `MAX_RESULT_ROWS` | `50` | Maximum rows from SPARQL |
| `QUESTION_BATCH_SIZE` | `10` | Rows per LLM call for question generation |
