"""Main pipeline: orchestrates the rule-based SPARQL generation."""

import logging
from .models import (
    QueryResponse,
    ExplorationResponse,
    ResultColumn,
    HistoryTurn,
)
from .query_interpreter import QueryInterpreter
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
            QueryResponse with interpretation and SPARQL query
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

        # Step 2: SPARQL Generation (LLM Call #2)
        logger.info("Step 2: Generating SPARQL")
        sparql_result = self.sparql_generator.generate(user_query)

        if not sparql_result.sparql:
            logger.warning("SPARQL generation failed")
            return QueryResponse(
                interpretation=interpretation.intent,
                sparql_query=None,
                suggestions=[],
            )

        # Step 3: Validation (Rule-based)
        logger.info("Step 3: Validating SPARQL")
        validation_result = self.validator.validate(sparql_result.sparql)

        if not validation_result.valid:
            logger.warning("SPARQL validation failed: %s", validation_result.errors)
            return QueryResponse(
                interpretation=interpretation.intent,
                sparql_query=sparql_result.sparql,
                suggestions=[],
                error=f"Validation failed: {'; '.join(validation_result.errors)}",
            )

        # Step 4: SPARQL Execution (DBLP endpoint)
        logger.info("Step 4: Executing SPARQL")
        execution_result = self.executor.execute(sparql_result.sparql)

        if not execution_result.success:
            logger.warning("SPARQL execution failed: %s", execution_result.error)
            return QueryResponse(
                interpretation=interpretation.intent,
                sparql_query=sparql_result.sparql,
                suggestions=sparql_result.suggestions,
                error=execution_result.error,
            )

        # Step 5: Response Formatting (LLM Call #3)
        logger.info("Step 5: Formatting response")
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

        # Step 2: SPARQL Generation (LLM Call #2)
        logger.info("Step 2: Generating SPARQL")
        sparql_result = self.sparql_generator.generate(user_query)

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

        # Step 3: Validation (Rule-based)
        logger.info("Step 3: Validating SPARQL")
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

        # Step 4: SPARQL Execution (DBLP endpoint)
        logger.info("Step 4: Executing SPARQL")
        execution_result = self.executor.execute(sparql_result.sparql)

        if not execution_result.success:
            logger.warning("SPARQL execution failed: %s", execution_result.error)
            return ExplorationResponse(
                interpretation=f"Query execution failed: {execution_result.error}",
                sparql_query=sparql_result.sparql,
                suggestions=sparql_result.suggestions,
            )

        # Step 5: Response Formatting (LLM Call #3)
        logger.info("Step 5: Formatting response")
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

        # Step 6: Observation Generation (LLM Call #4 - only if data exists)
        observations = []
        if formatted.row_count > 0:
            logger.info("Step 6: Generating observations")
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

    def close(self):
        """Cleanup resources."""
        self.executor.close()
