"""DBLP schema provider — centralises schema knowledge for LLM prompts."""

from __future__ import annotations


class DBLPSchemaProvider:
    """Provides DBLP schema information for LLM prompting and validation."""

    PREFIXES = """PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX schema: <https://schema.org/>"""

    KEY_CLASSES: list[str] = [
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

    KEY_PREDICATES: list[str] = [
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

    LIMITATION_KEYWORDS: dict[str, str] = {
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

    def get_schema(self) -> str:
        """Return a human-readable schema description for LLM prompts."""
        classes = ", ".join(self.KEY_CLASSES)
        predicates = ", ".join(self.KEY_PREDICATES)
        return (
            f"DBLP SCHEMA\n\n"
            f"Classes: {classes}\n\n"
            f"Predicates: {predicates}\n\n"
            f"Prefixes:\n{self.PREFIXES}"
        )

    def get_prefixes(self) -> str:
        """Return the SPARQL PREFIX declarations."""
        return self.PREFIXES

    def get_classes(self) -> list[str]:
        """Return the list of known DBLP classes."""
        return list(self.KEY_CLASSES)

    def get_predicates(self) -> list[str]:
        """Return the list of known DBLP predicates."""
        return list(self.KEY_PREDICATES)
