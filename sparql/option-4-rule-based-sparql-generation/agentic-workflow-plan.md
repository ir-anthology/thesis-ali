# Agentic Workflow Plan - Rule-Based SPARQL Generation

## Overview

Multi-step LLM pipeline for converting natural language questions to SPARQL queries against the DBLP Knowledge Graph.

**Model**: `gpt-5.6-luna` (OpenAI Responses API with Structured Outputs)  
**Architecture**: 2 LLM calls + 4 rule-based steps  
**Entity Resolution**: DBLP Search API with JSON file caching

---

## Module Structure

```
option-4-rule-based-sparql-generation/
├── src/
│   ├── __init__.py
│   ├── config.py                  # API keys, endpoints, constants
│   ├── models.py                  # Pydantic models for all data structures
│   ├── intent_classifier.py       # Step 1: LLM intent classification
│   ├── entity_resolver.py         # Step 2: DBLP API entity resolution
│   ├── limitation_detector.py     # Step 3: Rule-based limitation detection
│   ├── clarification_detector.py  # Step 4: Clarification detection
│   ├── sparql_generator.py        # Step 5: LLM SPARQL generation
│   ├── validator.py               # Step 6: SPARQL validation
│   ├── pipeline.py                # Main orchestrator
│   └── prompts.py                 # System prompts for LLM calls
├── tests/
│   ├── __init__.py
│   ├── test_intent_classifier.py
│   ├── test_entity_resolver.py
│   ├── test_limitation_detector.py
│   ├── test_clarification_detector.py
│   ├── test_sparql_generator.py
│   ├── test_validator.py
│   ├── test_pipeline.py
│   └── fixtures/
│       └── test_cases.json
├── data/
│   ├── examples.json              # 10 few-shot examples for SPARQL generation
│   └── entity_cache.json          # Cached entity lookups
├── main.py                        # CLI entry point for testing
├── requirements.txt
└── README.md
```

---

## Dependencies

```
openai>=1.0.0
pydantic>=2.0.0
httpx>=0.24.0
python-dotenv>=1.0.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

---

## Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER QUERY                                      │
│                    "papers by Hinton at NeurIPS"                         │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 1: INTENT CLASSIFICATION (LLM Call #1)                            │
│                                                                          │
│  Model: gpt-5.6-luna                                                    │
│  API: OpenAI Responses API with Structured Outputs                      │
│                                                                          │
│  System Prompt: Classify query into intent categories                   │
│  Input: Raw user query string                                           │
│                                                                          │
│  Output (Pydantic - IntentResult):                                      │
│  {                                                                       │
│    "intent": "find_publications_by_author_and_venue",                    │
│    "entities_mentioned": [                                               │
│      {"text": "Hinton", "type_hint": "Person"},                         │
│      {"text": "NeurIPS", "type_hint": "Conference"}                     │
│    ],                                                                    │
│    "constraints": {"year": null, "publication_type": null},              │
│    "needs_clarification": false,                                         │
│    "clarification_question": null                                        │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ENTITY RESOLUTION (DBLP API - No LLM)                          │
│                                                                          │
│  Input: entities_mentioned from Step 1                                   │
│                                                                          │
│  For each entity:                                                        │
│    1. Check local cache (data/entity_cache.json)                        │
│    2. If not cached, call DBLP Search API                               │
│       - Person → https://dblp.org/search/author/api                     │
│       - Conference/Journal → https://dblp.org/search/venue/api          │
│    3. If multiple matches, mark as ambiguous                            │
│                                                                          │
│  Output (Pydantic - ResolvedEntity):                                    │
│  {                                                                       │
│    "mention": "Hinton",                                                  │
│    "uri": "https://dblp.org/pid/10/3248",                               │
│    "label": "Geoffrey Hinton",                                           │
│    "type": "Person",                                                     │
│    "confidence": 1.0,                                                    │
│    "ambiguous": false,                                                   │
│    "not_found": false,                                                   │
│    "candidates": []                                                      │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 3: LIMITATION DETECTION (Rule-Based - No LLM)                     │
│                                                                          │
│  Input: Original query + intent from Step 1                             │
│                                                                          │
│  Check if query requires unsupported features:                           │
│    - "citation", "cited by" → DBLP doesn't track citations             │
│    - "abstract", "full text" → DBLP doesn't store full text            │
│    - "impact factor", "h-index" → DBLP doesn't compute metrics         │
│    - "download" → DBLP provides metadata only                           │
│                                                                          │
│  Output (Pydantic - LimitationResult):                                  │
│  {                                                                       │
│    "has_limitation": false,                                              │
│    "limitation": null                                                    │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 4: CLARIFICATION DETECTION (Rule-Based - No LLM)                  │
│                                                                          │
│  Input: IntentResult from Step 1 + ResolvedEntity from Step 2           │
│                                                                          │
│  Check for:                                                              │
│    - Unresolved entities (not_found = true)                             │
│    - Ambiguous entities (ambiguous = true, multiple candidates)         │
│    - Missing required entities (e.g., no author for "papers by ?")      │
│                                                                          │
│  Output (Pydantic - ClarificationResult):                               │
│  {                                                                       │
│    "needs_clarification": false,                                         │
│    "clarification": null,                                                │
│    "suggestions": []                                                     │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 5: SPARQL GENERATION (LLM Call #2)                                │
│                                                                          │
│  Model: gpt-5.6-luna                                                    │
│  API: OpenAI Responses API with Structured Outputs                      │
│                                                                          │
│  System Prompt: Generate SPARQL for DBLP using schema context            │
│  Input:                                                                  │
│    - Original question                                                   │
│    - Resolved entities with URIs                                         │
│    - Schema context (relevant classes/properties)                        │
│    - Few-shot examples (10 examples from data/examples.json)            │
│                                                                          │
│  Output (Pydantic - SPARQLResult):                                      │
│  {                                                                       │
│    "sparql": "PREFIX dblp: <https://dblp.org/rdf/schema#> ...",         │
│    "confidence": 0.95,                                                   │
│    "explanation": "Query finds publications by Geoffrey Hinton at NeurIPS"│
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  STEP 6: VALIDATION (Rule-Based - No LLM)                               │
│                                                                          │
│  Input: sparql from Step 5                                              │
│                                                                          │
│  Checks:                                                                 │
│    - Valid SPARQL syntax (starts with SELECT)                           │
│    - All prefixes declared (dblp:, rdf:, rdfs:, xsd:)                   │
│    - Predicates exist in DBLP schema                                    │
│    - Balanced braces                                                    │
│                                                                          │
│  Output (Pydantic - ValidationResult):                                  │
│  {                                                                       │
│    "valid": true,                                                        │
│    "errors": [],                                                         │
│    "warnings": []                                                        │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  FINAL RESPONSE                                                          │
│                                                                          │
│  {                                                                       │
│    "intent": "find_publications_by_author_and_venue",                    │
│    "clarification": null,                                                │
│    "limitation": null,                                                   │
│    "sparql_query": "PREFIX dblp: <https://dblp.org/rdf/schema#> ...",   │
│    "suggestions": [                                                      │
│      "You can filter by year: 'papers by Hinton at NeurIPS after 2020'",│
│      "Try other venues: ICML, AAAI, IJCAI",                             │
│      "Add LIMIT 10 to restrict results"                                  │
│    ]                                                                     │
│  }                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Pydantic Models

### Intent Classification Models

```python
from enum import Enum
from pydantic import BaseModel

class IntentType(str, Enum):
    find_publications_by_author = "find_publications_by_author"
    find_publications_by_venue = "find_publications_by_venue"
    find_publications_by_author_and_venue = "find_publications_by_author_and_venue"
    find_publications_by_year = "find_publications_by_year"
    find_publications_by_type = "find_publications_by_type"
    find_authors_of_publication = "find_authors_of_publication"
    find_coauthors = "find_coauthors"
    find_author_metadata = "find_author_metadata"
    find_venue_info = "find_venue_info"
    count_publications = "count_publications"
    unknown = "unknown"

class EntityMention(BaseModel):
    text: str
    type_hint: str  # "Person", "Conference", "Journal", "Venue", "Unknown"

class IntentResult(BaseModel):
    intent: IntentType
    entities_mentioned: list[EntityMention]
    constraints: dict  # {"year": "2023", "publication_type": "Article"}
    needs_clarification: bool
    clarification_question: str | None
```

### Entity Resolution Models

```python
class ResolvedEntity(BaseModel):
    mention: str
    uri: str | None
    label: str | None
    type: str | None
    confidence: float
    ambiguous: bool = False
    not_found: bool = False
    candidates: list[dict] = []
```

### Limitation & Clarification Models

```python
class LimitationResult(BaseModel):
    has_limitation: bool
    limitation: str | None

class ClarificationResult(BaseModel):
    needs_clarification: bool
    clarification: str | None
    suggestions: list[str] = []
```

### SPARQL Generation Models

```python
class SPARQLResult(BaseModel):
    sparql: str
    confidence: float
    explanation: str

class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
```

### Final Response Model

```python
class QueryResponse(BaseModel):
    intent: str
    clarification: str | None
    limitation: str | None
    sparql_query: str | None
    suggestions: list[str] = []
```

---

## System Prompts

### Intent Classification Prompt

```
You are a DBLP query intent classifier. Given a natural language question about computer science publications, classify the intent and extract entity mentions.

INTENT CATEGORIES:
- find_publications_by_author: "papers by X", "publications by X"
- find_publications_by_venue: "papers in Y", "publications at Y"
- find_publications_by_author_and_venue: "papers by X at Y"
- find_publications_by_year: "papers from 2023"
- find_publications_by_type: "journal articles by X"
- find_authors_of_publication: "who wrote Z"
- find_coauthors: "co-authors of X"
- find_author_metadata: "affiliation of X", "homepage of X"
- find_venue_info: "info about Y", "ISSN of Y"
- count_publications: "how many papers by X"
- unknown: cannot determine intent

ENTITY TYPE HINTS:
- Person: author names (e.g., "Geoffrey Hinton", "Yann LeCun")
- Conference: conference names (e.g., "SIGMOD", "NeurIPS", "KDD")
- Journal: journal names (e.g., "TODS", "TKDE", "PVLDB")
- Venue: generic venue reference
- Unknown: cannot determine type

CONSTRAINTS TO EXTRACT:
- year: year filter (e.g., "2023", "after 2020")
- publication_type: Article, Inproceedings, Book, etc.

Return structured JSON with intent, entities, constraints, and clarification status.
```

### SPARQL Generation Prompt

```
You are a SPARQL expert for the DBLP Computer Science Bibliography.

Generate correct SPARQL queries for the DBLP knowledge graph.

MANDATORY PREFIXES:
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

KEY PREDICATES:
- dblp:authoredBy (Publication → Creator)
- dblp:creatorName (Creator → string)
- dblp:title (Publication → string)
- dblp:yearOfPublication (Publication → gYear)
- dblp:publishedInStream (Publication → Stream)
- dblp:streamTitle (Stream → string)
- dblp:coAuthorWith (Creator → Creator)
- dblp:primaryAffiliation (Creator → string)
- dblp:doi (Publication → anyUri)

KEY CLASSES:
- dblp:Publication, dblp:Article, dblp:Inproceedings, dblp:Book
- dblp:Creator, dblp:Person, dblp:Group
- dblp:Stream, dblp:Conference, dblp:Journal

RULES:
1. Use ONLY predicates from the schema
2. Use exact entity URIs provided (enclose in angle brackets)
3. Always include mandatory prefixes
4. Use SELECT for queries that return results
5. Use FILTER for date/string filtering
6. Use COUNT/GROUP BY for aggregation
7. Enclose URIs in angle brackets: <https://dblp.org/...>
8. For year comparisons: "2023"^^xsd:gYear

Return structured JSON with sparql query, confidence score, and explanation.
```

---

## Test Cases

| # | Category | Input Query | Expected Output | Notes |
|---|----------|-------------|-----------------|-------|
| 1 | Author search | "papers by Geoffrey Hinton" | Valid SPARQL | Simple author lookup |
| 2 | Author+Venue | "papers by Hinton at NeurIPS" | Valid SPARQL | Multi-entity |
| 3 | Venue search | "conferences about databases" | Valid SPARQL | Venue query |
| 4 | Ambiguous | "papers by Smith" | Clarification | Multiple Smiths |
| 5 | Missing entity | "papers by ??? at SIGMOD" | Clarification | No author given |
| 6 | Citation query | "citations of paper X" | Limitation | DBLP limitation |
| 7 | Abstract query | "abstract of paper Y" | Limitation | DBLP limitation |
| 8 | Year filter | "papers by Han from 2023" | Valid SPARQL | With constraint |
| 9 | Count query | "how many papers by Knuth?" | Valid SPARQL | Aggregation |
| 10 | Complex | "co-authors of LeCun who also worked with Hinton" | Valid SPARQL | Relationship |

---

## Implementation Order

1. `src/config.py` - Configuration and constants
2. `src/models.py` - All Pydantic models
3. `src/prompts.py` - System prompts for LLM calls
4. `src/intent_classifier.py` - Step 1: LLM intent classification
5. `src/entity_resolver.py` - Step 2: DBLP API resolution with caching
6. `src/limitation_detector.py` - Step 3: Rule-based limitation detection
7. `src/clarification_detector.py` - Step 4: Clarification detection
8. `src/sparql_generator.py` - Step 5: LLM SPARQL generation
9. `src/validator.py` - Step 6: SPARQL validation
10. `src/pipeline.py` - Main orchestrator
11. `data/examples.json` - 10 few-shot examples
12. `tests/` - All test files
13. `main.py` - CLI entry point
14. `requirements.txt` - Dependencies
15. `README.md` - Documentation

---

## Error Handling Strategy

- **OpenAI API errors**: Retry with exponential backoff (max 3 retries)
- **DBLP API errors**: Return cached results if available, else mark as not_found
- **Invalid SPARQL**: Return validation errors, do not attempt execution
- **Rate limiting**: 1 second delay between DBLP API calls

---

## Logging Strategy

Each step logs:
- Input parameters
- Output results
- Errors encountered
- Timing information

Use Python `logging` module with configurable levels (DEBUG, INFO, WARNING, ERROR).
