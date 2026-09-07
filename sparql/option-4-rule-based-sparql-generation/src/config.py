"""Configuration management for rule-based SPARQL generation."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.6-luna")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

DBLP_SPARQL_ENDPOINT = os.getenv(
    "DBLP_SPARQL_ENDPOINT", "https://sparql.dblp.org/sparql"
)

EXAMPLES_PATH = BASE_DIR / os.getenv("EXAMPLES_PATH", "data/examples.json")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
MAX_RESULT_ROWS = int(os.getenv("MAX_RESULT_ROWS", "50"))
QUESTION_BATCH_SIZE = int(os.getenv("QUESTION_BATCH_SIZE", "10"))

# FastAPI settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

DBLP_PREFIXES = """PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>"""

DBLP_KEY_CLASSES = [
    "AmbiguousCreator",
    "Article",
    "AuthorSignature",
    "Book",
    "Conference",
    "Creator",
    "Data",
    "EditorSignature",
    "Editorship",
    "Entity",
    "Group",
    "Incollection",
    "Informal",
    "Inproceedings",
    "Journal",
    "Person",
    "Publication",
    "Reference",
    "Repository",
    "Series",
    "Signature",
    "Stream",
    "VersionRelation",
    "Withdrawn",
]

DBLP_KEY_PREDICATES = [
    "affiliation",
    "archivedWebpage",
    "authorOf",
    "authoredBy",
    "awardWebpage",
    "bibtexType",
    "coAuthorWith",
    "coCreatorWith",
    "coEditorWith",
    "createdBy",
    "creatorName",
    "creatorNote",
    "creatorOf",
    "documentPage",
    "doi",
    "editedBy",
    "editorOf",
    "formerStreamTitle",
    "hasSignature",
    "hasVersion",
    "homepage",
    "homonymousCreator",
    "identifier",
    "indexPage",
    "isVersion",
    "isVersionOf",
    "isbn",
    "iso4",
    "issn",
    "listedOnTocPage",
    "monthOfPublication",
    "numberOfCreators",
    "omid",
    "orcid",
    "pagination",
    "possibleActualCreator",
    "predecessorStream",
    "primaryAffiliation",
    "primaryCreatorName",
    "primaryDocumentPage",
    "primaryHomepage",
    "primaryStreamTitle",
    "proxyAmbiguousCreator",
    "publicationNote",
    "publishedAsPartOf",
    "publishedBy",
    "publishedIn",
    "publishedInBook",
    "publishedInBookChapter",
    "publishedInJournal",
    "publishedInJournalVolume",
    "publishedInJournalVolumeIssue",
    "publishedInSeries",
    "publishedInSeriesVolume",
    "publishedInStream",
    "publishersAddress",
    "relatedStream",
    "signatureCreator",
    "signatureDblpName",
    "signatureOrcid",
    "signatureOrdinal",
    "signaturePublication",
    "streamTitle",
    "subStream",
    "successorStream",
    "superStream",
    "thesisAcceptedBySchool",
    "title",
    "versionConcept",
    "versionInstance",
    "versionLabel",
    "versionOrdinal",
    "versionUri",
    "webpage",
    "wikidata",
    "wikipedia",
    "yearOfEvent",
    "yearOfPublication",
]

LIMITATION_KEYWORDS = {
    "citation": "DBLP does not track citation counts between publications. Consider using Semantic Scholar or Google Scholar for citation data.",
    "cited by": "DBLP does not track citation relationships between publications. This information is not available in the DBLP knowledge graph.",
    "abstract": "DBLP does not store publication abstracts or summaries. Only metadata such as title, authors, venue, and year is available.",
    "full text": "DBLP does not contain full text of publications. Only metadata (titles, authors, venues) is available.",
    "impact factor": "DBLP does not store journal impact factors.",
    "h-index": "DBLP does not compute author metrics like h-index.",
    "download": "DBLP provides metadata only, not access to full publications.",
    "peer review": "DBLP does not include peer review information.",
    "funding": "DBLP does not track funding information for publications.",
    "price": "DBLP does not track publication pricing or availability.",
    "availability": "DBLP does not track publication pricing or availability.",
}
