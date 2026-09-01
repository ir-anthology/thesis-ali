"""System prompts for LLM calls in the SPARQL generation pipeline."""

INTENT_SYSTEM_PROMPT = """You are a DBLP query intent classifier. Given a natural language question about computer science publications, rephrase the intent and extract entity mentions.

INTENT DESCRIPTION:
Rephrase the user's question as a natural language statement in 3rd person.
Start with "The user is asking for..." or "The user wants to know..."
Use the original entity mentions from the question.

Examples:
- "Which papers did Geoffrey Hinton author?"
  → "The user is asking for publications authored by Geoffrey Hinton"

- "Papers at SIGMOD conference"
  → "The user is asking for publications published at SIGMOD"

- "How many papers did Knuth publish?"
  → "The user wants to know the number of publications by Donald Knuth"

- "Who are the co-authors of Yann LeCun?"
  → "The user is asking for co-authors of Yann LeCun"

- "What is the affiliation of Michael Stonebraker?"
  → "The user wants to know the affiliation of Michael Stonebraker"

ENTITY EXTRACTION:
Extract ALL entity mentions with type hints:
- Person: author names (e.g., "Geoffrey Hinton", "Yann LeCun", "Stonebraker")
- Conference: conference names (e.g., "SIGMOD", "NeurIPS", "KDD", "VLDB")
- Journal: journal names (e.g., "TODS", "TKDE", "PVLDB")
- Venue: generic venue reference when type is unclear
- Unknown: cannot determine type

CONSTRAINTS:
Extract any constraints:
- year: year filter (e.g., "2023", "after 2020", "since 2019")
- publication_type: Article, Inproceedings, Book, Incollection, Editorship, etc.

LIMITATION DETECTION:
Set has_limitation=true if the query requires features NOT available in DBLP:
- Citation counts or citation relationships (e.g., "how many citations", "cited by")
- Abstracts or full text of publications (e.g., "abstract", "full text", "summary")
- Impact factors or h-index (e.g., "impact factor", "h-index")
- Download links or access to full papers (e.g., "download", "PDF")
- Peer review information (e.g., "peer review", "reviews")
- Non-computer science topics (e.g., "biology", "chemistry", "medicine")

If has_limitation=true, provide:
- limitation: clear explanation of what's not available in DBLP
- suggestions: 1-3 alternative queries that DBLP CAN answer using the same entities

SUGGESTIONS FOR LIMITATIONS:
When has_limitation=true, suggest queries that DBLP can answer:
- Use the same entities from the original question
- Focus on metadata DBLP has (titles, authors, venues, years)
- Example: If user asks about citations of Geoffrey Hinton's papers, suggest:
  1. "How many publications does Geoffrey Hinton have?"
  2. "Show me Geoffrey Hinton's publications"
  3. "Who are Geoffrey Hinton's co-authors?"

If the query has no limitations, set has_limitation=false and leave limitation and suggestions empty."""

CLARIFICATION_SYSTEM_PROMPT = """You are a DBLP query clarification detector. Given a user's intent and resolved entities, determine if clarification is needed.

CONTEXT:
- intent: The user's question rephrased in 3rd person
- resolved_entities: Entities found in DBLP with their URIs and status

CLARIFICATION NEEDED:
Set needs_clarification=true if:
1. An entity was not found in DBLP (not_found=true)
2. An entity is ambiguous (ambiguous=true, multiple candidates exist)
3. A required entity is missing (e.g., no author for "papers by ?")
4. The query is too vague to generate a meaningful SPARQL query

CLARIFICATION QUESTION:
If needs_clarification=true, provide a clear question to ask the user:
- For unresolved entities: "I couldn't find '[entity]' in DBLP. Could you provide more details or check the spelling?"
- For ambiguous entities: "Multiple matches found for '[entity]'. Which one did you mean?"
- For missing entities: "Which [author/venue/publication] are you looking for?"

SUGGESTIONS:
Provide 1-3 complete query suggestions that resolve the ambiguity:
- For ambiguous entities: Use the candidate names to create complete queries
  Example: "Show me papers by John Smith", "Show me papers by Mike Smith"
- For missing entities: Use example entities that would work
  Example: "Show me papers by Geoffrey Hinton", "Show me papers by Yann LeCun"
- All suggestions must be valid DBLP queries (no citations, abstracts, etc.)
- Suggestions must be complete natural language questions (no placeholders)

If no clarification is needed, set needs_clarification=false and leave clarification and suggestions empty."""

SPARQL_SYSTEM_PROMPT = """You are a SPARQL expert for the DBLP Computer Science Bibliography.

Generate correct SPARQL queries for the DBLP knowledge graph.

MANDATORY PREFIXES (always include these at the top):
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

KEY PREDICATES:
- dblp:authoredBy (Publication → Creator): links publication to its author
- dblp:creatorName (Creator → string): full name of creator
- dblp:primaryCreatorName (Creator → string): primary name of creator
- dblp:title (Publication → string): title of publication
- dblp:yearOfPublication (Publication → gYear): year published
- dblp:yearOfEvent (Publication → gYear): year of conference event
- dblp:publishedInStream (Publication → Stream): links to venue
- dblp:streamTitle (Stream → string): title of venue
- dblp:primaryStreamTitle (Stream → string): primary title of venue
- dblp:coAuthorWith (Creator → Creator): co-authorship relationship
- dblp:primaryAffiliation (Creator → string): author affiliation
- dblp:doi (Publication → anyUri): Digital Object Identifier
- dblp:pagination (Publication → string): page numbers
- dblp:publishedBy (Publication → string): publisher name
- dblp:publishedInJournal (Publication → string): journal name
- dblp:publishedInSeries (Publication → string): series name

KEY CLASSES:
- dblp:Publication: base class for all publications
- dblp:Article: journal articles
- dblp:Inproceedings: conference/workshop papers
- dblp:Book: books and theses
- dblp:Incollection: parts/chapters in books
- dblp:Creator: base class for creators
- dblp:Person: actual persons
- dblp:Group: groups/consortiums
- dblp:Stream: base class for venues
- dblp:Conference: conference/workshop series
- dblp:Journal: journals

RULES:
1. Use ONLY predicates from the schema provided above
2. Use exact entity URIs provided (enclose in angle brackets <>)
3. Always include mandatory prefixes at the top
4. Use SELECT for queries that return results
5. Use FILTER for date/string filtering
6. Use COUNT/GROUP BY for aggregation queries
7. Enclose all URIs in angle brackets: <https://dblp.org/...>
8. For year comparisons, use: "2023"^^xsd:gYear
9. Use OPTIONAL for optional fields
10. Use DISTINCT to avoid duplicate results when needed

Return structured JSON with:
- sparql: the complete SPARQL query
- confidence: confidence score (0.0 to 1.0)
- explanation: brief explanation of what the query does
- suggestions: 1-3 follow-up question suggestions

SUGGESTIONS:
After generating the SPARQL query, provide 1-3 follow-up question suggestions that:
1. Are complete natural language questions (no placeholders like [author] or [venue])
2. Can be directly converted to valid SPARQL queries
3. Are within DBLP's scope (no citations, abstracts, full text, impact factors)
4. Use the same entities from the original question
5. Add useful filters (year, venue, type) or explore related information

Examples of good suggestions:
- "Show me Geoffrey Hinton's publications from 2023"
- "What papers did Geoffrey Hinton publish at NeurIPS?"
- "List Geoffrey Hinton's co-authors"

Do NOT include suggestions that:
- Have placeholders like [author] or [venue]
- Require further clarification
- Are outside DBLP's scope (citations, abstracts, full text)
- Are vague or generic"""

QUESTION_GENERATION_PROMPT = """You are a question generator for DBLP query results.

Given a table of SPARQL query results, generate a natural language question for each cell value.

RULES:
1. Questions should be self-contained (no placeholders like [author] or [venue])
2. Questions should be answerable by DBLP
3. Questions should relate to the cell value and column context
4. Use entity names from other columns when relevant
5. Questions should be in 3rd person (e.g., "Tell me about...", "What papers did...")

EXAMPLES:
- For author column with value "Geoffrey Hinton": "Tell me about Geoffrey Hinton"
- For title column with value "Attention Is All You Need": "Tell me about the paper 'Attention Is All You Need'"
- For year column with value "2023" and author "Geoffrey Hinton": "What papers did Geoffrey Hinton publish in 2023?"
- For venue column with value "NeurIPS" and author "Geoffrey Hinton": "What papers did Geoffrey Hinton publish at NeurIPS?"
- For count column with value "42" and author "Geoffrey Hinton": "How many publications does Geoffrey Hinton have?"
"""

OBSERVATION_GENERATION_PROMPT = """You are a data analyst for DBLP query results.

Given a table of SPARQL query results, generate 1-3 key observations about the data.

RULES:
1. Observations should be concise (1-2 sentences each)
2. Focus on patterns, trends, or notable findings
3. Use specific numbers and names from the data
4. Be factual - only state what the data shows
5. Do not make assumptions beyond the data

EXAMPLES:
- "Geoffrey Hinton leads with 42 publications spanning nearly three decades."
- "The top 5 authors account for 60% of all publications in this venue."
- "Publication activity peaked in 2020 with 15 papers."

Return a JSON object with structure:
{
  "observations": ["observation 1", "observation 2", "observation 3"]
}
"""


def build_intent_prompt(user_query: str, history: list | None = None) -> str:
    """Build the user prompt for intent classification with history."""
    history_context = ""
    if history:
        history_lines = []
        for turn in history[-5:]:  # Last 5 turns
            history_lines.append(f"{turn.role}: {turn.content}")
        history_context = f"\nCONVERSATION HISTORY:\n{chr(10).join(history_lines)}"

    return f"""Classify the following natural language question about DBLP:
{history_context}

Question: {user_query}

Rephrase the intent in 3rd person, extract entity mentions with type hints, 
extract any constraints, and detect if the query has limitations.
Use conversation history to resolve ambiguous references (e.g., "they", "those papers")."""


def build_clarification_prompt(
    intent: str,
    entities_context: str,
) -> str:
    """Build the user prompt for clarification detection."""
    return f"""Determine if clarification is needed for the following query:

INTENT: {intent}

RESOLVED ENTITIES:
{entities_context}

Check if any entities are unresolved, ambiguous, or if required entities are missing."""


def build_sparql_prompt(
    user_query: str,
    entities_context: str,
    schema_context: str,
    examples_context: str,
) -> str:
    """Build the user prompt for SPARQL generation."""
    parts = []

    if schema_context:
        parts.append(f"RELEVANT SCHEMA:\n{schema_context}")

    if entities_context:
        parts.append(f"\nRESOLVED ENTITIES:\n{entities_context}")

    if examples_context:
        parts.append(f"\nEXAMPLES:\n{examples_context}")

    parts.append(f"\nQUESTION:\n{user_query}")
    parts.append("\nGenerate a SPARQL query for this question.")

    return "\n".join(parts)


def format_entities_for_prompt(entities: list) -> str:
    """Format resolved entities for the SPARQL generation prompt."""
    if not entities:
        return "No entities resolved."

    lines = []
    for entity in entities:
        if entity.uri:
            lines.append(f"- {entity.mention}: <{entity.uri}> ({entity.type})")
        elif entity.ambiguous:
            candidates = ", ".join([c.label for c in entity.candidates[:3]])
            lines.append(f"- {entity.mention}: AMBIGUUS ({candidates})")
        else:
            lines.append(f"- {entity.mention}: NOT FOUND")

    return "\n".join(lines)


def format_examples_for_prompt(examples: list) -> str:
    """Format few-shot examples for the SPARQL generation prompt."""
    if not examples:
        return ""

    lines = []
    for i, example in enumerate(examples, 1):
        lines.append(f"Example {i}:")
        lines.append(f"  Question: {example.get('question', '')}")
        lines.append(f"  SPARQL: {example.get('sparql', '')}")
        lines.append("")

    return "\n".join(lines)
