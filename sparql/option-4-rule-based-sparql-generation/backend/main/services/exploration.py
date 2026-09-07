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
        logger.info("Exploration request: %s", request.message)

        # C0 — initial context
        context = self._context_builder.build(request)

        # C1 — interpretation
        interpretation = self._interpretation.run(context)
        context.set_interpretation(interpretation)

        # Scope routing
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

        # C2 — SPARQL generation
        sparql_gen = self._sparql_generation.run(context)
        if sparql_gen is None:
            suggestions = self._suggestions.run(context)
            return ExplorationResponse(
                interpretation=context.interpretation.summary
                if context.interpretation
                else None,
                suggestions=suggestions or None,
            )

        context.set_sparql(sparql_gen.query)

        # Validate
        validation = self._sparql_validator.validate(sparql_gen.query)
        if not validation.valid:
            logger.warning("SPARQL validation failed: %s", validation.errors)
            suggestions = self._suggestions.run(context)
            return ExplorationResponse(
                interpretation=(
                    f"Generated query is invalid: {'; '.join(validation.errors)}"
                ),
                sparql_query=sparql_gen.query,
                suggestions=suggestions or None,
            )

        # Execute
        try:
            query_result = self._sparql_client.execute(sparql_gen.query)
        except SPARQLError as exc:
            logger.error("SPARQL execution failed: %s", exc)
            suggestions = self._suggestions.run(context)
            return ExplorationResponse(
                interpretation=f"Query execution failed: {exc}",
                sparql_query=sparql_gen.query,
                suggestions=suggestions or None,
            )

        context.set_query_result(query_result)

        # Normalise result columns/rows
        columns = format_result_columns(query_result)
        context.set_result_table(columns, format_result_rows(query_result))

        # C3 — result analysis (questions + observations)
        if query_result.row_count > 0:
            rows_with_questions, observations = self._result_analysis.run(context)
            context.set_result_table(columns, rows_with_questions)
            context.set_observations(observations)

        # C4 — suggestions
        suggestions = self._suggestions.run(context)
        context.set_suggestions(suggestions)

        return self._build_response(context)

    async def _handle_out_of_scope(
        self, context: ExplorationContext
    ) -> ExplorationResponse:
        """Out-of-scope: skip SPARQL, generate suggestions only."""
        suggestions = self._suggestions.run(context)
        context.set_suggestions(suggestions)

        interpretation_text = None
        if context.interpretation:
            interpretation_text = context.interpretation.summary

        return ExplorationResponse(
            interpretation=interpretation_text,
            suggestions=suggestions or None,
        )

    def _handle_ambiguous(self, context: ExplorationContext) -> ExplorationResponse:
        """Ambiguous: return clarification questions as suggestions."""
        interp = context.interpretation
        if interp is None:
            return ExplorationResponse(interpretation="The request is ambiguous.")

        # Use clarification questions + possible scopes as suggestions
        suggestions: list[str] = []
        if interp.possible_scopes:
            suggestions = interp.possible_scopes[:3]
        elif interp.clarification_questions:
            suggestions = interp.clarification_questions[:3]

        interpretation_text = interp.summary
        if interp.clarification_questions:
            interpretation_text = interp.clarification_questions[0]

        return ExplorationResponse(
            interpretation=interpretation_text,
            suggestions=suggestions or None,
        )

    # ------------------------------------------------------------------
    # Response building
    # ------------------------------------------------------------------

    @staticmethod
    def _build_response(context: ExplorationContext) -> ExplorationResponse:
        interpretation_text = None
        if context.interpretation:
            interpretation_text = context.interpretation.summary

        has_data = (
            context.query_result is not None and context.query_result.row_count > 0
        )  # type: ignore[union-attr]

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
