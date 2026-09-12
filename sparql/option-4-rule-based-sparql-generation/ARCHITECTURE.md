# Project Architecture: Rule-Based SPARQL Generation for DBLP

## What it does (one sentence)

A user types a plain-English question about computer science research papers, and the system converts it into a database query, runs it against the DBLP bibliography database, and returns a structured answer with follow-up suggestions.

---

## The Big Picture

Think of it like a **4-step assembly line**:

```
User Question (e.g., "What papers did Turing publish?")
        |
        v
   [1] UNDERSTAND — An AI (LLM) reads the question and decides:
       • Is this something the DBLP database can answer? (in_scope)
       • Is this unclear and needs clarification? (ambiguous)
       • Is this outside what DBLP can do? (out_of_scope)
        |
        v
   [2] TRANSLATE — If it's answerable, another AI call converts
       the question into a SPARQL query (the database's language).
       The system also checks the query for errors before running it.
        |
        v
   [3] ANALYZE — The raw database results get processed:
       • Every cell in every row gets a follow-up question attached
       • The AI writes 1-3 observations about the data
        |
        v
   [4] SUGGEST — A final AI call generates 2-3 follow-up questions
       the user might want to ask next.
        |
        v
   A single JSON response goes back to the frontend with everything.
```

---

## How the Code is Organized

| Folder | Role | Analogy |
|---|---|---|
| `backend/main/api/` | Receives HTTP requests, sends responses | The front door / receptionist |
| `backend/main/services/` | One file per pipeline stage — the actual logic | The workers on the assembly line |
| `backend/main/llm/` | Talks to the OpenAI API + loads prompt templates | The translator who talks to the AI |
| `backend/main/llm/prompts/` | The instruction templates given to the AI | Cheat sheets for the translator |
| `backend/main/sparql/` | Builds, validates, and runs database queries | The database operator |
| `backend/main/schema/` | Knows what the DBLP database contains (classes, predicates) | The database's table of contents |
| `backend/main/schemas/` | Data structures (Pydantic models) for requests/responses | The standardized forms everyone fills out |
| `backend/main/context/` | Builds and carries info through the pipeline | The clipboard passed between stations |
| `data/examples.json` | 10 example question→SPARQL pairs for the AI to learn from | A study guide for the AI |
| `tests/` | Unit tests for each layer | Quality checks |

---

## Tech Stack

- **Language:** Python 3.11+
- **Web framework:** FastAPI (serves the API over HTTP)
- **AI:** OpenAI's API (structured outputs via Pydantic)
- **Database:** DBLP knowledge graph (queried via SPARQL over HTTP to a QLever endpoint)
- **Deployment:** Docker container → Kubernetes cluster at Bauhaus-Universität Weimar
- **Package manager:** `uv` (fast Python package manager)

---

## Key Design Decisions

1. **Multi-step LLM pipeline** — Instead of one big AI call, the work is split into 4 focused calls, each with a specific prompt. This makes each step simpler and more reliable.
2. **Externalized prompts** — All AI instructions live in `.txt` files, not buried in code. Easy to tweak without touching Python.
3. **Rule-based validation before execution** — Before running a generated SPARQL query, the system checks it against known DBLP predicates/classes using hardcoded rules. This catches obvious errors cheaply.
4. **Conversation history support** — The system accepts prior chat turns, so follow-up questions can reference earlier context.
5. **Three response types** — The system can return: data results (clear), a clarification request (ambiguous), or an explanation of limitations (out_of_scope).

---

## Data Flow Summary

```
Frontend sends:  { message: "...", history: [...] }
                        |
                        v
         ExplorationService orchestrates 4 stages
         (each stage uses a different LLM prompt)
                        |
                        v
Frontend receives: { interpretation, columns, rows,
                     observations, suggestions, sparql_query }
```

The frontend gets back everything it needs in one shot — the interpretation message, a data table (columns + rows), observations about the data, clickable follow-up suggestions, and the actual SPARQL query that was run (for transparency/debugging).
