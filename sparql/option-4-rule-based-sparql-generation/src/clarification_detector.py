"""Step 4: Clarification detection for DBLP queries."""

import logging
from .models import IntentResult, ResolvedEntity, ClarificationResult

logger = logging.getLogger(__name__)

INTENTS_REQUIRING_AUTHOR = [
    "find_publications_by_author",
    "find_publications_by_author_and_venue",
    "find_coauthors",
    "find_author_metadata",
    "count_publications",
]

INTENTS_REQUIRING_VENUE = [
    "find_publications_by_venue",
    "find_publications_by_author_and_venue",
    "find_venue_info",
]

INTENTS_REQUIRING_PUBLICATION = [
    "find_authors_of_publication",
]


class ClarificationDetector:
    """Detects if clarification is needed for a query."""

    def detect(
        self,
        intent_result: IntentResult,
        resolved_entities: list[ResolvedEntity],
    ) -> ClarificationResult:
        """Detect if clarification is needed.

        Args:
            intent_result: Result from intent classification
            resolved_entities: List of resolved entities

        Returns:
            ClarificationResult with clarification status and message
        """
        logger.info(
            "Checking clarification needs for intent: %s", intent_result.intent.value
        )

        # Check if LLM already flagged clarification needed
        if intent_result.needs_clarification and intent_result.clarification_question:
            logger.info("LLM flagged clarification needed")
            return ClarificationResult(
                needs_clarification=True,
                clarification=intent_result.clarification_question,
                suggestions=[],
            )

        # Check for unresolved entities
        for entity in resolved_entities:
            if entity.not_found:
                logger.info("Unresolved entity: %s", entity.mention)
                return ClarificationResult(
                    needs_clarification=True,
                    clarification=f"I couldn't find '{entity.mention}' in DBLP. Could you provide more details or check the spelling?",
                    suggestions=[
                        f"Try the full name (e.g., 'Geoffrey Hinton' instead of 'Hinton')",
                        f"Check the spelling of '{entity.mention}'",
                        f"Provide additional context (e.g., affiliation or research area)",
                    ],
                )

        # Check for ambiguous entities
        for entity in resolved_entities:
            if entity.ambiguous and entity.candidates:
                candidates = [
                    c.get("label", "") for c in entity.candidates[:3] if c.get("label")
                ]
                if candidates:
                    logger.info(
                        "Ambiguous entity: %s, candidates: %s",
                        entity.mention,
                        candidates,
                    )
                    return ClarificationResult(
                        needs_clarification=True,
                        clarification=f"Multiple matches found for '{entity.mention}'. Which one did you mean?",
                        suggestions=candidates,
                    )

        # Check for missing required entities based on intent
        intent = intent_result.intent.value

        if intent in INTENTS_REQUIRING_AUTHOR:
            has_author = any(e.type == "Person" and e.uri for e in resolved_entities)
            if not has_author:
                # Check if author was mentioned but not resolved
                author_mentions = [
                    e
                    for e in intent_result.entities_mentioned
                    if e.type_hint == "Person"
                ]
                if not author_mentions:
                    logger.info("Missing author for intent: %s", intent)
                    return ClarificationResult(
                        needs_clarification=True,
                        clarification="Which author are you looking for?",
                        suggestions=[
                            "Provide the author's full name",
                            "Include the author's affiliation for better results",
                        ],
                    )

        if intent in INTENTS_REQUIRING_VENUE:
            has_venue = any(
                e.type in ("Conference", "Journal") and e.uri for e in resolved_entities
            )
            if not has_venue:
                venue_mentions = [
                    e
                    for e in intent_result.entities_mentioned
                    if e.type_hint in ("Conference", "Journal", "Venue")
                ]
                if not venue_mentions:
                    logger.info("Missing venue for intent: %s", intent)
                    return ClarificationResult(
                        needs_clarification=True,
                        clarification="Which venue (conference or journal) are you interested in?",
                        suggestions=[
                            "Specify the venue name (e.g., SIGMOD, VLDB, TODS)",
                            "Use the full name if the abbreviation is ambiguous",
                        ],
                    )

        if intent in INTENTS_REQUIRING_PUBLICATION:
            has_publication = any(
                e.type in ("Publication", "Article", "Inproceedings") and e.uri
                for e in resolved_entities
            )
            if not has_publication:
                pub_mentions = [
                    e
                    for e in intent_result.entities_mentioned
                    if e.type_hint
                    in ("Publication", "Article", "Inproceedings", "Unknown")
                ]
                if not pub_mentions:
                    logger.info("Missing publication for intent: %s", intent)
                    return ClarificationResult(
                        needs_clarification=True,
                        clarification="Which publication are you asking about?",
                        suggestions=[
                            "Provide the publication title",
                            "Include the author name for better results",
                        ],
                    )

        logger.info("No clarification needed")
        return ClarificationResult(
            needs_clarification=False, clarification=None, suggestions=[]
        )
