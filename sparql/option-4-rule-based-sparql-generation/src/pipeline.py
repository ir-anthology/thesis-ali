"""Main pipeline: orchestrates the rule-based SPARQL generation."""

import logging
from .models import QueryResponse
from .intent_classifier import IntentClassifier
from .entity_resolver import EntityResolver
from .clarification_detector import ClarificationDetector
from .sparql_generator import SPARQLGenerator
from .validator import SPARQLValidator
from .sparql_executor import SPARQLExecutor
from .response_formatter import ResponseFormatter

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline for natural language to SPARQL conversion."""

    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_resolver = EntityResolver()
        self.clarification_detector = ClarificationDetector()
        self.sparql_generator = SPARQLGenerator()
        self.validator = SPARQLValidator()
        self.executor = SPARQLExecutor()
        self.formatter = ResponseFormatter()

    def convert(self, user_query: str) -> QueryResponse:
        """Convert a natural language question to SPARQL.

        Args:
            user_query: Natural language question about DBLP

        Returns:
            QueryResponse with intent, clarification, limitation, or SPARQL query
        """
        logger.info("Processing query: %s", user_query)

        # Step 1: Intent + Limitation Detection (LLM Call #1)
        logger.info("Step 1: Classifying intent and detecting limitations")
        intent_result = self.intent_classifier.classify(user_query)
        logger.info("Intent: %s", intent_result.intent)

        # Check limitation from intent result
        if intent_result.has_limitation:
            logger.info("Limitation detected: %s", intent_result.limitation)
            return QueryResponse(
                intent=intent_result.intent,
                clarification=None,
                limitation=intent_result.limitation,
                sparql_query=None,
                suggestions=intent_result.suggestions,
            )

        # Step 2: Entity Resolution (DBLP API)
        logger.info("Step 2: Resolving entities")
        resolution_result = self.entity_resolver.resolve_batch(
            intent_result.entities_mentioned
        )
        logger.info(
            "Resolved %d entities, %d unresolved",
            len(resolution_result.resolved_entities),
            len(resolution_result.unresolved_mentions),
        )

        # Step 3: Clarification Detection (LLM Call #2)
        logger.info("Step 3: Checking clarification needs")
        clarification_result = self.clarification_detector.detect(
            intent_result, resolution_result.resolved_entities
        )

        if clarification_result.needs_clarification:
            logger.info("Clarification needed: %s", clarification_result.clarification)
            return QueryResponse(
                intent=intent_result.intent,
                clarification=clarification_result.clarification,
                limitation=None,
                sparql_query=None,
                suggestions=clarification_result.suggestions,
            )

        # Step 4: SPARQL Generation (LLM Call #3)
        logger.info("Step 4: Generating SPARQL")
        sparql_result = self.sparql_generator.generate(
            user_query, resolution_result.resolved_entities
        )

        if not sparql_result.sparql:
            logger.warning("SPARQL generation failed")
            return QueryResponse(
                intent=intent_result.intent,
                clarification=None,
                limitation=None,
                sparql_query=None,
                suggestions=[],
            )

        # Step 5: Validation (Rule-based)
        logger.info("Step 5: Validating SPARQL")
        validation_result = self.validator.validate(sparql_result.sparql)

        if not validation_result.valid:
            logger.warning("SPARQL validation failed: %s", validation_result.errors)
            return QueryResponse(
                intent=intent_result.intent,
                clarification=None,
                limitation=None,
                sparql_query=sparql_result.sparql,
                suggestions=[],
                error=f"Validation failed: {'; '.join(validation_result.errors)}",
            )

        # Step 6: SPARQL Execution (DBLP endpoint)
        logger.info("Step 6: Executing SPARQL")
        execution_result = self.executor.execute(sparql_result.sparql)

        if not execution_result.success:
            logger.warning("SPARQL execution failed: %s", execution_result.error)
            return QueryResponse(
                intent=intent_result.intent,
                clarification=None,
                limitation=None,
                sparql_query=sparql_result.sparql,
                suggestions=sparql_result.suggestions,
                error=execution_result.error,
            )

        # Step 7: Response Formatting (LLM Call #4)
        logger.info("Step 7: Formatting response")
        formatted = self.formatter.format(
            user_query, execution_result, intent_result.intent
        )

        # Success - return formatted response
        logger.info("SPARQL generation and execution successful")
        return QueryResponse(
            intent=intent_result.intent,
            clarification=None,
            limitation=None,
            sparql_query=sparql_result.sparql,
            suggestions=sparql_result.suggestions,
            columns=formatted.columns,
            rows=formatted.rows,
            row_count=formatted.row_count,
        )

    def close(self):
        """Cleanup resources."""
        self.entity_resolver.close()
        self.executor.close()
