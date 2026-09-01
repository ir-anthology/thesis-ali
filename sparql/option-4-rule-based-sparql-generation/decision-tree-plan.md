# DBLP SPARQL Decision Tree - Rule-Based Generation

## Output Options

1. **Valid SPARQL query** - when clarification=None AND limitation=None
2. **Clarification required** - when user intent is ambiguous or info missing
3. **Request cannot be answered** - when query exceeds DBLP capabilities

## Output Format

```json
{
  "intent": "User is asking for......",
  "clarification": "Ask for what sort of information you need to clarify the request" | null,
  "limitation": "Tell the limitation and give the reason." | null,
  "sparql_query": "provide sparql query here..." | null,
  "suggestions": ["Give 1st suggestion...", "Give 2nd suggestion...", "Give 3rd Suggestion..."]
}
```

---

## Schema Summary

### Core Classes

| Class | Subclasses | Description |
|-------|------------|-------------|
| `Entity` | - | Base identifiable entity |
| `Creator` | Person, Group, AmbiguousCreator | Publication creators |
| `Publication` | Book, Article, Inproceedings, Incollection, Editorship, Reference, Data, Informal, Withdrawn | Published works |
| `Stream` | Conference, Journal, Series, Repository | Publication venues |
| `Signature` | AuthorSignature, EditorSignature | Creator-Publication links |
| `VersionRelation` | - | Publication version links |

### Key Properties by Class

| Class | Properties | Relationships |
|-------|------------|---------------|
| **Creator** | creatorName, primaryCreatorName, orcid, affiliation, primaryAffiliation, homepage, primaryHomepage, creatorNote | creatorOf, authorOf, editorOf, coCreatorWith, coAuthorWith, coEditorWith |
| **Publication** | title, doi, isbn, omid, yearOfPublication, yearOfEvent, monthOfPublication, pagination, bibtexType, numberOfCreators, publishedBy, publishedIn, publishedInJournal, publishedInSeries, publishedInBook | createdBy, authoredBy, editedBy, publishedInStream, publishedAsPartOf, hasVersion, isVersionOf, hasSignature |
| **Stream** | streamTitle, primaryStreamTitle, formerStreamTitle, issn, iso4 | relatedStream, superStream, subStream, predecessorStream, successorStream |
| **Signature** | signatureDblpName, signatureOrcid, signatureOrdinal | signatureCreator, signaturePublication |

---

## Decision Tree Structure

```
START: Parse User Query
│
├─── STEP 1: Intent Classification
│    │
│    ├─── 1.1 Publication Queries
│    │    ├── Find publications by author
│    │    ├── Find publications by title/topic
│    │    ├── Find publications by venue/journal
│    │    ├── Find publications by year
│    │    ├── Find publications by type
│    │    └── Find publication details (DOI, pages, etc.)
│    │
│    ├─── 1.2 Creator/Author Queries
│    │    ├── Find author by name
│    │    ├── Find author's publications
│    │    ├── Find co-authors
│    │    ├── Find author affiliations
│    │    └── Find author identifiers (ORCID, homepage)
│    │
│    ├─── 1.3 Venue/Stream Queries
│    │    ├── Find journal/conference by name
│    │    ├── Find publications in venue
│    │    ├── Find venue relationships (sub/super)
│    │    └── Find venue identifiers (ISSN)
│    │
│    ├─── 1.4 Relationship Queries
│    │    ├── Co-authorship relationships
│    │    ├── Citation relationships
│    │    ├── Author-Venue relationships
│    │    └── Publication version relationships
│    │
│    └─── 1.5 Aggregate/Statistical Queries
│         ├── Count publications
│         ├── Count authors
│         ├── Publication trends over time
│         └── Venue statistics
│
├─── STEP 2: Entity Resolution
│    │
│    ├─── 2.1 Named Entity Present?
│    │    ├── YES → Attempt to resolve entity
│    │    │   ├── Resolved → Continue
│    │    │   └── Ambiguous → CLARIFICATION
│    │    └── NO → Check if entity required
│    │        ├── Required → CLARIFICATION
│    │        └── Optional → Continue
│    │
│    └─── 2.2 Entity Type Clear?
│         ├── YES → Map to schema class
│         └── NO → CLARIFICATION
│
├─── STEP 3: Property/Relationship Mapping
│    │
│    ├─── 3.1 Requested properties exist in schema?
│    │    ├── YES → Map to schema properties
│    │    └── NO → LIMITATION
│    │
│    └─── 3.2 Relationships traversable?
│         ├── YES → Define path
│         └── NO → LIMITATION
│
├─── STEP 4: Constraint Validation
│    │
│    ├─── 4.1 All required constraints specified?
│    │    ├── YES → Validate constraints
│    │    └── NO → CLARIFICATION
│    │
│    └─── 4.2 Constraints valid per schema?
│         ├── YES → Continue
│         └── NO → LIMITATION
│
└─── STEP 5: Output Decision
     │
     ├─── Clarification = None AND Limitation = None
     │    └── GENERATE SPARQL QUERY
     │
     ├─── Clarification != None
     │    └── RETURN clarification request
     │
     └─── Limitation != None
          └── RETURN limitation explanation
```

---

## STEP 1: Intent Classification Rules

| Query Pattern | Intent Category | Example |
|---------------|-----------------|---------|
| "papers by [author]" | Publication by Author | "papers by John Doe" |
| "articles about [topic]" | Publication by Topic | "articles about machine learning" |
| "publications in [venue]" | Publication by Venue | "publications in SIGMOD" |
| "papers from [year]" | Publication by Year | "papers from 2023" |
| "[type] by [author]" | Publication by Type+Author | "journal articles by Smith" |
| "who wrote [title]" | Author of Publication | "who wrote 'Deep Learning'?" |
| "co-authors of [author]" | Co-authorship | "co-authors of Alice" |
| "affiliation of [author]" | Author Metadata | "affiliation of Bob" |
| "journals about [topic]" | Venue Search | "journals about AI" |
| "how many papers [condition]" | Aggregate | "how many papers by X?" |

---

## STEP 2: Entity Resolution Rules

```
IF entity_name provided:
    IF matches single known entity:
        → RESOLVED (use entity URI)
    ELIF matches multiple entities:
        → CLARIFICATION: "Multiple entities found: [list]. Which one?"
    ELIF no match:
        → CLARIFICATION: "Entity not found. Did you mean: [suggestions]?"
ELSE:
    IF entity required for query:
        → CLARIFICATION: "Please specify [entity type]"
    ELSE:
        → Continue without entity constraint
```

---

## STEP 3: Property Mapping

### Natural Language to Schema Property Mapping

| User Says | Schema Property | Class |
|-----------|-----------------|-------|
| "author name" | `creatorName` or `primaryCreatorName` | Creator |
| "ORCID" | `orcid` | Creator |
| "affiliation" | `affiliation` or `primaryAffiliation` | Creator |
| "homepage" | `homepage` or `primaryHomepage` | Creator |
| "title" | `title` | Publication |
| "DOI" | `doi` | Publication |
| "year" | `yearOfPublication` or `yearOfEvent` | Publication |
| "pages" | `pagination` | Publication |
| "journal" | `publishedInJournal` | Publication |
| "conference" | `publishedInSeries` | Publication |
| "publisher" | `publishedBy` | Publication |
| "venue" | `publishedInStream` | Publication |
| "ISSN" | `issn` | Stream |
| "volume" | `publishedInJournalVolume` or `publishedInSeriesVolume` | Publication |
| "issue" | `publishedInJournalVolumeIssue` | Publication |

---

## STEP 4: Clarification Rules

| Scenario | Clarification Message |
|----------|----------------------|
| Ambiguous author name | "Multiple authors found with name '[name]'. Please specify: [list with affiliations]" |
| Missing author for publication query | "Which author's publications are you looking for?" |
| Missing venue for venue query | "Which journal or conference are you interested in?" |
| Missing year range for temporal query | "What time period are you interested in?" |
| Ambiguous publication type | "Do you mean journal articles, conference papers, or all publications?" |
| Missing search criteria | "What criteria should I use to search? (author, title, venue, year)" |
| Entity not found | "I couldn't find '[entity]'. Did you mean: [suggestions]?" |
| Multiple interpretations | "Your query could mean: [option 1] or [option 2]. Which one?" |

---

## STEP 5: Limitation Rules

| Scenario | Limitation Message |
|----------|-------------------|
| Citation network queries | "DBLP does not store citation relationships between publications. This information is not available in the knowledge graph." |
| Full-text search | "DBLP does not contain full text of publications. Only metadata (titles, authors, venues) is available." |
| Abstract/summary queries | "DBLP does not store publication abstracts or summaries." |
| Download/access queries | "DBLP provides metadata only, not access to full publications." |
| Review/rating queries | "DBLP does not include peer reviews or ratings." |
| Funding information | "DBLP does not track funding information for publications." |
| Author career history | "DBLP does not store detailed career history, only current affiliations." |
| Citation count queries | "DBLP does not track citation counts. Consider using Semantic Scholar or Google Scholar." |
| Impact factor queries | "DBLP does not store journal impact factors." |
| Price/availability queries | "DBLP does not track publication pricing or availability." |
| Non-CS publications | "DBLP focuses on computer science publications only." |

---

## STEP 6: SPARQL Query Templates

### Template 1: Find Publications by Author

```sparql
SELECT ?pub ?title ?year
WHERE {
  ?author dblp:creatorName "AUTHOR_NAME" .
  ?pub dblp:authoredBy ?author .
  ?pub dblp:title ?title .
  ?pub dblp:yearOfPublication ?year .
}
ORDER BY DESC(?year)
```

### Template 2: Find Authors of Publication

```sparql
SELECT ?author ?name
WHERE {
  ?pub dblp:title "PUB_TITLE" .
  ?pub dblp:authoredBy ?author .
  ?author dblp:creatorName ?name .
}
```

### Template 3: Find Co-authors

```sparql
SELECT ?coauthor ?name
WHERE {
  ?author dblp:creatorName "AUTHOR_NAME" .
  ?author dblp:coAuthorWith ?coauthor .
  ?coauthor dblp:creatorName ?name .
}
```

### Template 4: Find Publications in Venue

```sparql
SELECT ?pub ?title ?year
WHERE {
  ?pub dblp:publishedInStream ?venue .
  ?venue dblp:streamTitle "VENUE_NAME" .
  ?pub dblp:title ?title .
  ?pub dblp:yearOfPublication ?year .
}
ORDER BY DESC(?year)
```

### Template 5: Find Venue Info

```sparql
SELECT ?title ?issn ?type
WHERE {
  ?venue dblp:streamTitle "VENUE_NAME" .
  ?venue dblp:primaryStreamTitle ?title .
  OPTIONAL { ?venue dblp:issn ?issn }
  {
    ?venue a dblp:Journal .
    BIND("Journal" AS ?type)
  }
  UNION
  {
    ?venue a dblp:Conference .
    BIND("Conference" AS ?type)
  }
}
```

### Template 6: Count Publications by Author

```sparql
SELECT (COUNT(?pub) AS ?count)
WHERE {
  ?author dblp:creatorName "AUTHOR_NAME" .
  ?pub dblp:authoredBy ?author .
}
```

### Template 7: Find Author Metadata

```sparql
SELECT ?name ?affiliation ?orcid ?homepage
WHERE {
  ?author dblp:creatorName "AUTHOR_NAME" .
  OPTIONAL { ?author dblp:primaryCreatorName ?name }
  OPTIONAL { ?author dblp:primaryAffiliation ?affiliation }
  OPTIONAL { ?author dblp:orcid ?orcid }
  OPTIONAL { ?author dblp:primaryHomepage ?homepage }
}
```

### Template 8: Find Publications by Year

```sparql
SELECT ?pub ?title ?author
WHERE {
  ?pub dblp:yearOfPublication "YEAR"^^xsd:gYear .
  ?pub dblp:title ?title .
  ?pub dblp:authoredBy ?author .
  ?author dblp:creatorName ?authorName .
}
```

### Template 9: Find Publications by Type

```sparql
SELECT ?pub ?title ?year
WHERE {
  ?pub a dblp:TYPE .
  ?pub dblp:title ?title .
  ?pub dblp:yearOfPublication ?year .
}
ORDER BY DESC(?year)
```

### Template 10: Find Author by Affiliation

```sparql
SELECT ?author ?name
WHERE {
  ?author dblp:primaryAffiliation "AFFILIATION" .
  ?author dblp:creatorName ?name .
}
```

### Template 11: Find Recent Publications in Venue

```sparql
SELECT ?pub ?title ?author
WHERE {
  ?pub dblp:publishedInStream ?venue .
  ?venue dblp:streamTitle "VENUE_NAME" .
  ?pub dblp:title ?title .
  ?pub dblp:yearOfPublication ?year .
  ?pub dblp:authoredBy ?author .
  ?author dblp:creatorName ?authorName .
  FILTER(?year >= "START_YEAR"^^xsd:gYear)
}
ORDER BY DESC(?year)
```

### Template 12: Find Publications by DOI

```sparql
SELECT ?pub ?title ?author
WHERE {
  ?pub dblp:doi "DOI_URI"^^xsd:anyUri .
  ?pub dblp:title ?title .
  ?pub dblp:authoredBy ?author .
  ?author dblp:creatorName ?authorName .
}
```

### Template 13: Find Venue Relationships

```sparql
SELECT ?related ?relatedTitle ?relationship
WHERE {
  {
    ?venue dblp:streamTitle "VENUE_NAME" .
    ?venue dblp:subStream ?related .
    ?related dblp:primaryStreamTitle ?relatedTitle .
    BIND("sub-stream" AS ?relationship)
  }
  UNION
  {
    ?venue dblp:streamTitle "VENUE_NAME" .
    ?venue dblp:superStream ?related .
    ?related dblp:primaryStreamTitle ?relatedTitle .
    BIND("super-stream" AS ?relationship)
  }
}
```

### Template 14: Find Editor of Publication

```sparql
SELECT ?editor ?name
WHERE {
  ?pub dblp:title "PUB_TITLE" .
  ?pub dblp:editedBy ?editor .
  ?editor dblp:creatorName ?name .
}
```

### Template 15: Count Publications in Venue by Year

```sparql
SELECT (COUNT(?pub) AS ?count)
WHERE {
  ?pub dblp:publishedInStream ?venue .
  ?venue dblp:streamTitle "VENUE_NAME" .
  ?pub dblp:yearOfPublication "YEAR"^^xsd:gYear .
}
```

---

## Example Outputs

### Example 1: Valid SPARQL Query

**User Query**: "Which papers did Geoffrey Hinton publish?"

```json
{
  "intent": "User is asking for publications authored by Geoffrey Hinton",
  "clarification": null,
  "limitation": null,
  "sparql_query": "PREFIX dblp: <https://dblp.org/rdf/schema#> SELECT ?pub ?title ?year WHERE { ?author dblp:creatorName \"Geoffrey Hinton\" . ?pub dblp:authoredBy ?author . ?pub dblp:title ?title . ?pub dblp:yearOfPublication ?year . } ORDER BY DESC(?year)",
  "suggestions": [
    "You can also filter by publication type (Article, Inproceedings, etc.)",
    "Try adding LIMIT to restrict the number of results",
    "You can ask for specific years with: publications by Geoffrey Hinton from 2023"
  ]
}
```

### Example 2: Clarification Required

**User Query**: "papers by Smith"

```json
{
  "intent": "User is asking for publications by 'Smith'",
  "clarification": "Multiple authors found with name 'Smith'. Please specify: Michael Smith (MIT), John Smith (Stanford), Sarah Smith (CMU). Which author do you mean?",
  "limitation": null,
  "sparql_query": null,
  "suggestions": [
    "Provide the full name with affiliation: 'Michael Smith from MIT'",
    "Use ORCID if available: 'author with ORCID 0000-0002-1234-5678'",
    "Specify the research area: 'Michael Smith who works on machine learning'"
  ]
}
```

### Example 3: Limitation Encountered

**User Query**: "How many citations does 'Deep Learning' have?"

```json
{
  "intent": "User is asking for citation count of a paper",
  "clarification": null,
  "limitation": "DBLP does not track citation counts between publications. This information is not available in the DBLP knowledge graph. Consider using Semantic Scholar, Google Scholar, or OpenCitations for citation data.",
  "sparql_query": null,
  "suggestions": [
    "Ask for the paper's metadata instead: 'What is the title and year of this paper?'",
    "Find the paper's authors: 'Who authored this paper?'",
    "Find related papers in the same venue: 'What other papers were published in this venue?'"
  ]
}
```

### Example 4: Valid SPARQL with Venue Filter

**User Query**: "Conference papers by Jiawei Han at SIGMOD"

```json
{
  "intent": "User is asking for conference papers by Jiawei Han published at SIGMOD",
  "clarification": null,
  "limitation": null,
  "sparql_query": "PREFIX dblp: <https://dblp.org/rdf/schema#> SELECT ?pub ?title ?year WHERE { ?author dblp:creatorName \"Jiawei Han\" . ?pub dblp:authoredBy ?author . ?pub dblp:publishedInStream <https://dblp.org/streams/conf/sigmod> . ?pub dblp:title ?title . ?pub dblp:yearOfPublication ?year . } ORDER BY DESC(?year)",
  "suggestions": [
    "You can filter by year range: 'papers by Jiawei Han at SIGMOD after 2020'",
    "Try other venues: VLDB, KDD, ICDE",
    "Add LIMIT 10 to see only the first 10 results"
  ]
}
```

### Example 5: Clarification for Missing Entity

**User Query**: "What papers were published in this journal?"

```json
{
  "intent": "User is asking for publications in a journal but did not specify which journal",
  "clarification": "Which journal are you interested in? Please provide the journal name (e.g., TODS, TKDE, PVLDB).",
  "limitation": null,
  "sparql_query": null,
  "suggestions": [
    "Specify the journal name: 'papers published in TODS'",
    "Use the full name: 'papers published in ACM Transactions on Database Systems'",
    "List available journals: 'list all journals in DBLP'"
  ]
}
```

### Example 6: Limitation for Abstract Query

**User Query**: "What is the abstract of 'Attention Is All You Need'?"

```json
{
  "intent": "User is asking for the abstract/summary of a publication",
  "clarification": null,
  "limitation": "DBLP does not store publication abstracts or summaries. Only metadata such as title, authors, venue, and year is available.",
  "sparql_query": null,
  "suggestions": [
    "Get the paper's metadata: 'Who authored Attention Is All You Need?'",
    "Find the DOI to access the full paper: 'What is the DOI of Attention Is All You Need?'",
    "Find related papers: 'What other papers did the authors publish?'"
  ]
}
```

---

## Implementation Checklist

- [ ] Intent classifier (regex/keyword-based)
- [ ] Entity resolver (DBLP API + cache)
- [ ] Property mapper (NL to schema property)
- [ ] Clarification generator
- [ ] Limitation detector
- [ ] SPARQL template engine
- [ ] Response formatter
- [ ] Test suite with example queries
