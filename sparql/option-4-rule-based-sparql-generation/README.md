# Rule-Based SPARQL Generation for DBLP

A multi-step LLM pipeline for converting natural language questions to SPARQL queries against the DBLP Computer Science Bibliography.

## Architecture

```
User Query
    ↓
Step 1: Intent Classification (LLM Call #1)
    ↓
Step 2: Entity Resolution (DBLP API + Cache)
    ↓
Step 3: Limitation Detection (Rule-based)
    ↓
Step 4: Clarification Detection (Rule-based)
    ↓
Step 5: SPARQL Generation (LLM Call #2)
    ↓
Step 6: Validation (Rule-based)
    ↓
Final Response (JSON)
```

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
```

## Usage

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
pytest tests/ -v
```

## Output Format

```json
{
  "intent": "find_publications_by_author",
  "clarification": null,
  "limitation": null,
  "sparql_query": "PREFIX dblp: <https://dblp.org/rdf/schema#> ...",
  "suggestions": [
    "Add a year filter: 'papers by [author] from 2023'",
    "Filter by venue: 'papers by [author] at [venue]'"
  ]
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
│   ├── config.py              # Configuration
│   ├── models.py              # Pydantic models
│   ├── prompts.py             # LLM prompts
│   ├── intent_classifier.py   # Step 1
│   ├── entity_resolver.py     # Step 2
│   ├── limitation_detector.py # Step 3
│   ├── clarification_detector.py # Step 4
│   ├── sparql_generator.py    # Step 5
│   ├── validator.py           # Step 6
│   └── pipeline.py            # Orchestrator
├── tests/
│   ├── test_limitation_detector.py
│   ├── test_clarification_detector.py
│   └── test_validator.py
├── data/
│   ├── examples.json          # Few-shot examples
│   └── entity_cache.json      # Entity cache
├── main.py                    # CLI entry point
├── pyproject.toml             # Project config
└── README.md
```
