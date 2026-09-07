"""Main pipeline: orchestrates the rule-based SPARQL generation."""

import logging
from .models import (
    QueryResponse,
    ExplorationResponse,
    ResultColumn,
    HistoryTurn,
)
from .query_interpreter import QueryInterpreter
from .entity_resolver import EntityResolver
from .sparql_generator import SPARQLGenerator
from .validator import SPARQLValidator
from .sparql_executor import SPARQLExecutor
from .response_formatter import ResponseFormatter
from .observation_generator import ObservationGenerator

logger = logging.getLogger(__name__)


class Pipeline:
    """Main pipeline for natural language to SPARQL conversion."""

    def __init__(self):
        self.interpreter = QueryInterpreter()
        self.entity_resolver = EntityResolver()
        self.sparql_generator = SPARQLGenerator()
        self.validator = SPARQLValidator()
        self.executor = SPARQLExecutor()
        self.formatter = ResponseFormatter()
        self.observation_generator = ObservationGenerator()

    def convert(self, user_query: str) -> QueryResponse:
        """Convert a natural language question to SPARQL (backward compatibility).

        Args:
            user_query: Natural language question about DBLP

        Returns:
            QueryResponse with intent, clarification, limitation, or SPARQL query
        """
        logger.info("Processing query: %s", user_query)

        # Step 1: Unified Query Interpretation (LLM Call #1)
        logger.info("Step 1: Interpreting query")
        interpretation = self.interpreter.interpret(user_query)
        logger.info("Outcome: %s", interpretation.outcome)

        # Check out_of_scope
        if interpretation.outcome == "out_of_scope":
            logger.info("Query is out of scope: %s", interpretation.limitation)
            return QueryResponse(
                interpretation=interpretation.limitation,
                sparql_query=None,
                suggestions=interpretation.suggestions,
            )

        # Check ambiguous (from LLM interpretation)
        if interpretation.outcome == "ambiguous":
            logger.info("Query is ambiguous: %s", interpretation.clarification)
            return QueryResponse(
                interpretation=interpretation.clarification,
                sparql_query=None,
                suggestions=interpretation.options or interpretation.suggestions,
            )

        # Step 2: Entity Resolution (DBLP API)
        logger.info("Step 2: Resolving entities")
        resolution_result = self.entity_resolver.resolve_batch(
            interpretation.entities_mentioned
        )
        logger.info(
            "Resolved %d entities, %d unresolved",
            len(resolution_result.resolved_entities),
            len(resolution_result.unresolved_mentions),
        )

        # Step 2b: Rule-based ambiguity check after entity resolution
        clarification_response = self._check_entity_ambiguity(resolution_result)
        if clarification_response:
            return clarification_response

        # Step 3: SPARQL Generation (LLM Call #2)
        logger.info("Step 3: Generating SPARQL")
        sparql_result = self.sparql_generator.generate(
            user_query, resolution_result.resolved_entities
        )

        if not sparql_result.sparql:
            logger.warning("SPARQL generation failed")
            return QueryResponse(
                interpretation=interpretation.intent,
                sparql_query=None,
                suggestions=[],
            )

        # Step 4: Validation (Rule-based)
        logger.info("Step 4: Validating SPARQL")
        validation_result = self.validator.validate(sparql_result.sparql)

        if not validation_result.valid:
            logger.warning("SPARQL validation failed: %s", validation_result.errors)
            return QueryResponse(
                interpretation=interpretation.intent,
                sparql_query=sparql_result.sparql,
                suggestions=[],
                error=f"Validation failed: {'; '.join(validation_result.errors)}",
            )

        # Step 5: SPARQL Execution (DBLP endpoint)
        logger.info("Step 5: Executing SPARQL")
        execution_result = self.executor.execute(sparql_result.sparql)

        if not execution_result.success:
            logger.warning("SPARQL execution failed: %s", execution_result.error)
            return QueryResponse(
                interpretation=interpretation.intent,
                sparql_query=sparql_result.sparql,
                suggestions=sparql_result.suggestions,
                error=execution_result.error,
            )

        # Step 6: Response Formatting (LLM Call #3)
        logger.info("Step 6: Formatting response")
        formatted = self.formatter.format(
            user_query, execution_result, interpretation.intent
        )

        # Success - return formatted response
        logger.info("SPARQL generation and execution successful")
        return QueryResponse(
            interpretation=interpretation.intent,
            sparql_query=sparql_result.sparql,
            suggestions=sparql_result.suggestions,
            columns=formatted.columns,
            rows=formatted.rows,
            row_count=formatted.row_count,
        )

    def explore(
        self,
        user_query: str,
        history: list[HistoryTurn] | None = None,
    ) -> ExplorationResponse:
        """Process exploration query with history (frontend-compatible).

        Args:
            user_query: Natural language question about DBLP
            history: Conversation history (last 5 turns used for context)

        Returns:
            ExplorationResponse matching frontend contract
        """
        logger.info("Processing exploration query: %s", user_query)

        # Step 1: Unified Query Interpretation (uses history)
        logger.info("Step 1: Interpreting query")
        interpretation = self.interpreter.interpret(user_query, history)
        logger.info("Outcome: %s", interpretation.outcome)

        # Check out_of_scope
        if interpretation.outcome == "out_of_scope":
            logger.info("Query is out of scope: %s", interpretation.limitation)
            return ExplorationResponse(
                interpretation=interpretation.limitation,
                suggestions=interpretation.suggestions,
            )

        # Check ambiguous (from LLM interpretation)
        if interpretation.outcome == "ambiguous":
            logger.info("Query is ambiguous: %s", interpretation.clarification)
            return ExplorationResponse(
                interpretation=interpretation.clarification,
                suggestions=interpretation.options or interpretation.suggestions,
            )

        # Step 2: Entity Resolution (DBLP API)
        logger.info("Step 2: Resolving entities")
        resolution_result = self.entity_resolver.resolve_batch(
            interpretation.entities_mentioned
        )
        logger.info(
            "Resolved %d entities, %d unresolved",
            len(resolution_result.resolved_entities),
            len(resolution_result.unresolved_mentions),
        )

        # Step 2b: Rule-based ambiguity check after entity resolution
        clarification_response = self._check_entity_ambiguity_exploration(
            resolution_result
        )
        if clarification_response:
            return clarification_response

        # Step 3: SPARQL Generation (LLM Call #2)
        logger.info("Step 3: Generating SPARQL")
        sparql_result = self.sparql_generator.generate(
            user_query, resolution_result.resolved_entities
        )

        if not sparql_result.sparql:
            logger.warning("SPARQL generation failed")
            return ExplorationResponse(
                interpretation="Failed to generate a valid SPARQL query.",
                suggestions=[
                    "Try rephrasing your question",
                    "Be more specific about what you're looking for",
                    "Check if the entity names are correct",
                ],
            )

        # Step 4: Validation (Rule-based)
        logger.info("Step 4: Validating SPARQL")
        validation_result = self.validator.validate(sparql_result.sparql)

        if not validation_result.valid:
            logger.warning("SPARQL validation failed: %s", validation_result.errors)
            return ExplorationResponse(
                interpretation=f"Generated query is invalid: {'; '.join(validation_result.errors)}",
                suggestions=[
                    "Try rephrasing your question",
                    "Ask about authors, publications, or venues",
                ],
            )

        # Step 5: SPARQL Execution (DBLP endpoint)
        logger.info("Step 5: Executing SPARQL")
        execution_result = self.executor.execute(sparql_result.sparql)

        if not execution_result.success:
            logger.warning("SPARQL execution failed: %s", execution_result.error)
            return ExplorationResponse(
                interpretation=f"Query execution failed: {execution_result.error}",
                sparql_query=sparql_result.sparql,
                suggestions=sparql_result.suggestions,
            )

        # Step 6: Response Formatting (LLM Call #3)
        logger.info("Step 6: Formatting response")
        formatted = self.formatter.format(
            user_query, execution_result, interpretation.intent
        )

        # Convert ColumnDef to ResultColumn for frontend
        result_columns = [
            ResultColumn(
                key=col.key,
                label=col.label,
                type=col.type,
                sortable=col.sortable,
            )
            for col in formatted.columns
        ]

        # Step 7: Observation Generation (LLM Call #4 - only if data exists)
        observations = []
        if formatted.row_count > 0:
            logger.info("Step 7: Generating observations")
            observations = self.observation_generator.generate(
                user_query, interpretation.intent, result_columns, formatted.rows
            )

        # Success - return exploration response
        logger.info("Exploration successful")
        return ExplorationResponse(
            interpretation=interpretation.intent,
            columns=result_columns if formatted.row_count > 0 else None,
            rows=formatted.rows if formatted.row_count > 0 else None,
            observations=observations if observations else None,
            suggestions=sparql_result.suggestions,
            sparql_query=sparql_result.sparql,
        )

    def _check_entity_ambiguity(self, resolution_result) -> QueryResponse | None:
        """Check for ambiguity after entity resolution and return clarification if needed.

        Args:
            resolution_result: Result from entity resolution

        Returns:
            QueryResponse with clarification if ambiguous, None otherwise
        """
        for entity in resolution_result.resolved_entities:
            # Check for ambiguous entities
            if entity.ambiguous:
                candidates = [c.label for c in entity.candidates[:3]]
                clarification = f"Multiple matches found for '{entity.mention}'. Which one did you mean?"
                options = [f"Show me information about {c}" for c in candidates]
                suggestions = [
                    f"Try being more specific, e.g., '{entity.mention} from [affiliation]'"
                ]
                return QueryResponse(
                    interpretation=clarification,
                    sparql_query=None,
                    suggestions=options + suggestions,
                )

            # Check for not found entities
            if entity.not_found:
                clarification = f"I couldn't find '{entity.mention}' in DBLP. Could you provide more details or check the spelling?"
                suggestions = [
                    "Try using the full name (e.g., 'Geoffrey Hinton' instead of 'Hinton')",
                    "Check the spelling of the name",
                    "Ask about a different author or venue",
                ]
                return QueryResponse(
                    interpretation=clarification,
                    sparql_query=None,
                    suggestions=suggestions,
                )

        # Check for unresolved mentions
        if resolution_result.unresolved_mentions:
            mention = resolution_result.unresolved_mentions[0]
            clarification = (
                f"I couldn't find '{mention}' in DBLP. Could you provide more details?"
            )
            suggestions = [
                "Try using the full name",
                "Check the spelling",
                "Ask about a different entity",
            ]
            return QueryResponse(
                interpretation=clarification,
                sparql_query=None,
                suggestions=suggestions,
            )

        return None

    def _check_entity_ambiguity_exploration(
        self, resolution_result
    ) -> ExplorationResponse | None:
        """Check for ambiguity after entity resolution and return clarification if needed.

        Args:
            resolution_result: Result from entity resolution

        Returns:
            ExplorationResponse with clarification if ambiguous, None otherwise
        """
        for entity in resolution_result.resolved_entities:
            # Check for ambiguous entities
            if entity.ambiguous:
                candidates = [c.label for c in entity.candidates[:3]]
                clarification = f"Multiple matches found for '{entity.mention}'. Which one did you mean?"
                options = [f"Show me information about {c}" for c in candidates]
                suggestions = [
                    f"Try being more specific, e.g., '{entity.mention} from [affiliation]'"
                ]
                return ExplorationResponse(
                    interpretation=clarification,
                    suggestions=options + suggestions,
                )

            # Check for not found entities
            if entity.not_found:
                clarification = f"I couldn't find '{entity.mention}' in DBLP. Could you provide more details or check the spelling?"
                suggestions = [
                    "Try using the full name (e.g., 'Geoffrey Hinton' instead of 'Hinton')",
                    "Check the spelling of the name",
                    "Ask about a different author or venue",
                ]
                return ExplorationResponse(
                    interpretation=clarification,
                    suggestions=suggestions,
                )

        # Check for unresolved mentions
        if resolution_result.unresolved_mentions:
            mention = resolution_result.unresolved_mentions[0]
            clarification = (
                f"I couldn't find '{mention}' in DBLP. Could you provide more details?"
            )
            suggestions = [
                "Try using the full name",
                "Check the spelling",
                "Ask about a different entity",
            ]
            return ExplorationResponse(
                interpretation=clarification,
                suggestions=suggestions,
            )

        return None

    def close(self):
        """Cleanup resources."""
        self.entity_resolver.close()
        self.executor.close()
