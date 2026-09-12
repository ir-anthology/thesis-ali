"""Exploration orchestrator — coordinates the four LLM stages.

This is the single entry point for the API layer.  It builds the context,
runs the pipeline, and converts the internal context to the frontend response.
"""

from __future__ import annotations

import logging

from backend.main.context.builder import ContextBuilder
from backend.main.schema.provider import DBLPSchemaProvider
from backend.main.schemas.context import ExplorationContext
from backend.main.schemas.requests import ChatRequest
from backend.main.schemas.responses import ExplorationResponse, ResultColumn, CellValue
from backend.main.services.interpretation import InterpretationService
from backend.main.services.sparql_generation import SPARQLGenerationService
from backend.main.services.result_analysis import ResultAnalysisService
from backend.main.services.suggestions import SuggestionService
from backend.main.sparql.client import SPARQLClient, SPARQLError
from backend.main.sparql.formatter import format_result_columns, format_result_rows
from backend.main.sparql.validator import SPARQLValidator

logger = logging.getLogger(__name__)


class ExplorationService:
    """Main orchestrator for the exploration pipeline."""

    def __init__(self) -> None:
        schema_provider = DBLPSchemaProvider()

        self._context_builder = ContextBuilder(schema_provider)
        self._interpretation = InterpretationService()
        self._sparql_generation = SPARQLGenerationService(
            schema_provider=schema_provider
        )
        self._result_analysis = ResultAnalysisService()
        self._suggestions = SuggestionService()
        self._sparql_client = SPARQLClient()
        self._sparql_validator = SPARQLValidator()

    async def explore(self, request: ChatRequest) -> ExplorationResponse:
        """Process an exploration request through the full pipeline."""
        logger.info("=" * 60)
        logger.info("PIPELINE START: %s", request.message)
        logger.info("=" * 60)

        # C0 — initial context
        context = self._context_builder.build(request)

        # C1 — interpretation
        logger.info("[Stage 1/4] Interpretation")
        interpretation = self._interpretation.run(context)
        context.set_interpretation(interpretation)
        logger.info("  → scope: %s", interpretation.scope)
        logger.info("  → message: %s", interpretation.message)

        # Scope routing
        logger.info("[Scope Routing] → %s", interpretation.scope.upper())
        if interpretation.scope == "out_of_scope":
            return await self._handle_out_of_scope(context)

        if interpretation.scope == "ambiguous":
            return self._handle_ambiguous(context)

        # In-scope path
        return await self._handle_in_scope(context)

    # ------------------------------------------------------------------
    # Scope handlers
    # ------------------------------------------------------------------

    async def _handle_in_scope(
        self, context: ExplorationContext
    ) -> ExplorationResponse:
        """Full pipeline: SPARQL → execute → analyse → suggest."""
        logger.info("[Path] IN_SCOPE — running full pipeline")

        # C2 — SPARQL generation
        logger.info("[Stage 2/4] SPARQL Generation")
        sparql_gen = self._sparql_generation.run(context)
        if sparql_gen is None:
            logger.warning("  → SPARQL generation failed (returned None)")
            suggestions = self._suggestions.run(context)
            return ExplorationResponse(
                interpretation=context.interpretation.message
                if context.interpretation
                else None,
                suggestions=suggestions or None,
            )

        context.set_sparql(sparql_gen.query)
        logger.info("  → SPARQL generated (%d chars)", len(sparql_gen.query))

        # Validate
        logger.info("[Stage 2/4] SPARQL Validation")
        validation = self._sparql_validator.validate(sparql_gen.query)
        if not validation.valid:
            logger.warning("  → Validation FAILED: %s", validation.errors)
            suggestions = self._suggestions.run(context)
            return ExplorationResponse(
                interpretation=(
                    f"Generated query is invalid: {'; '.join(validation.errors)}"
                ),
                sparql_query=sparql_gen.query,
                suggestions=suggestions or None,
            )
        logger.info("  → Validation PASSED")

        # Execute
        logger.info("[Stage 2/4] SPARQL Execution")
        try:
            query_result = self._sparql_client.execute(sparql_gen.query)
        except SPARQLError as exc:
            logger.error("  → Execution FAILED: %s", exc)
            suggestions = self._suggestions.run(context)
            return ExplorationResponse(
                interpretation=f"Query execution failed: {exc}",
                sparql_query=sparql_gen.query,
                suggestions=suggestions or None,
            )

        context.set_query_result(query_result)
        logger.info("  → Execution SUCCESS: %d rows returned", query_result.row_count)

        # Normalise result columns/rows
        columns = format_result_columns(query_result)
        context.set_result_table(columns, format_result_rows(query_result))

        # C3 — result analysis (questions + observations)
        if query_result.row_count > 0:
            logger.info("[Stage 3/4] Result Analysis")
            rows_with_questions, observations = self._result_analysis.run(context)
            logger.info("  → rows_with_questions count: %d", len(rows_with_questions))
            if rows_with_questions:
                logger.info("  → First row sample: %s", rows_with_questions[0])
            context.set_result_table(columns, rows_with_questions)
            context.set_observations(observations)
            logger.info("  → Generated %d observations", len(observations))
            logger.info("  → context.result_rows count: %d", len(context.result_rows))
            if context.result_rows:
                logger.info(
                    "  → context.result_rows[0] sample: %s", context.result_rows[0]
                )
        else:
            logger.info("[Stage 3/4] Result Analysis — skipped (0 rows)")

        # C4 — suggestions
        logger.info("[Stage 4/4] Suggestions")
        suggestions = self._suggestions.run(context)
        context.set_suggestions(suggestions)
        logger.info("  → Generated %d suggestions", len(suggestions))

        logger.info("PIPELINE COMPLETE")
        return self._build_response(context)

    async def _handle_out_of_scope(
        self, context: ExplorationContext
    ) -> ExplorationResponse:
        """Out-of-scope: skip SPARQL, generate suggestions only."""
        logger.info("[Path] OUT_OF_SCOPE — skipping SPARQL pipeline")

        logger.info("[Stage 4/4] Suggestions")
        suggestions = self._suggestions.run(context)
        context.set_suggestions(suggestions)
        logger.info("  → Generated %d suggestions", len(suggestions))

        interpretation_text = None
        if context.interpretation:
            interpretation_text = context.interpretation.message

        logger.info("PIPELINE COMPLETE (out_of_scope)")
        return ExplorationResponse(
            interpretation=interpretation_text,
            suggestions=suggestions or None,
        )

    def _handle_ambiguous(self, context: ExplorationContext) -> ExplorationResponse:
        """Ambiguous: return clarification questions as suggestions."""
        logger.info("[Path] AMBIGUOUS — returning clarification questions")

        interp = context.interpretation
        if interp is None:
            return ExplorationResponse(interpretation="The request is ambiguous.")

        # For ambiguous, the message contains the clarification question
        interpretation_text = interp.message

        logger.info("PIPELINE COMPLETE (ambiguous)")
        return ExplorationResponse(
            interpretation=interpretation_text,
            suggestions=None,
        )

    # ------------------------------------------------------------------
    # Response building
    # ------------------------------------------------------------------

    @staticmethod
    def _build_response(context: ExplorationContext) -> ExplorationResponse:
        interpretation_text = None
        if context.interpretation:
            interpretation_text = context.interpretation.message

        has_data = (
            context.query_result is not None and context.query_result.row_count > 0
        )  # type: ignore[union-attr]

        logger.info("[_build_response] has_data: %s", has_data)
        logger.info(
            "[_build_response] context.result_rows count: %d", len(context.result_rows)
        )
        if context.result_rows:
            logger.info(
                "[_build_response] First result_row sample: %s", context.result_rows[0]
            )

        return ExplorationResponse(
            interpretation=interpretation_text,
            columns=context.result_columns if has_data else None,
            rows=context.result_rows if has_data else None,
            observations=context.observations or None,
            suggestions=context.suggestions or None,
            sparql_query=context.sparql_query,
        )

    def close(self) -> None:
        self._sparql_client.close()
