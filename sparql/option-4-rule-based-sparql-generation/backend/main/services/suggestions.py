"""Stage 4 — Suggestions service.

Generates follow-up questions / suggestions based on the full accumulated
context.  Used for all three scope paths (in_scope, out_of_scope, ambiguous).
"""

from __future__ import annotations

import logging

from backend.main.llm.client import LLMClient, load_prompt
from backend.main.schemas.context import ExplorationContext

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = load_prompt("suggestions")


class SuggestionService:
    """Runs Stage 4: generate follow-up suggestions."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    def run(self, context: ExplorationContext) -> list[str]:
        """Generate 2-3 follow-up suggestions."""
        logger.info("Stage 4: Generating suggestions")

        user_prompt = self._build_user_prompt(context)

        data = self._llm.generate_json(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        if data is None:
            logger.warning("Suggestion generation failed")
            return []

        suggestions = data.get("suggestions", [])
        result = suggestions[:3] if suggestions else []
        logger.info("Generated %d suggestions", len(result))
        return result

    # ------------------------------------------------------------------

    @staticmethod
    def _build_user_prompt(context: ExplorationContext) -> str:
        parts: list[str] = [
            f"USER REQUEST: {context.user_message}",
        ]

        # Interpretation
        if context.interpretation:
            interp = context.interpretation
            parts.append(f"\nINTERPRETATION: {interp.summary}")
            parts.append(f"Scope: {interp.scope}")

        # SPARQL query
        if context.sparql_query:
            parts.append(f"\nSPARQL QUERY:\n{context.sparql_query}")

        # Results summary
        if context.query_result and context.query_result.row_count > 0:
            parts.append(f"\nRESULTS: {context.query_result.row_count} rows returned")
            parts.append(f"COLUMNS: {', '.join(context.query_result.columns)}")
            # Include first few rows as context
            for i, row in enumerate(context.query_result.rows[:5]):
                row_str = ", ".join(f"{k}: {v}" for k, v in row.items())
                parts.append(f"  Row {i + 1}: {row_str}")
            if context.query_result.row_count > 5:
                parts.append(
                    f"  ... and {context.query_result.row_count - 5} more rows"
                )
        elif context.query_result and context.query_result.row_count == 0:
            parts.append("\nRESULTS: 0 rows returned (empty result)")

        # Observations
        if context.observations:
            parts.append(f"\nOBSERVATIONS:")
            for obs in context.observations:
                parts.append(f"  - {obs}")

        return "\n".join(parts)
