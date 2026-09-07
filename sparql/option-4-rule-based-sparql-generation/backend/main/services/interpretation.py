"""Stage 1 — Interpretation service.

Determines what the user is asking and decides the scope (in_scope / out_of_scope / ambiguous).
"""

from __future__ import annotations

import logging

from backend.main.llm.client import LLMClient, load_prompt
from backend.main.schemas.context import ExplorationContext
from backend.main.schemas.llm import Interpretation

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = load_prompt("interpretation")


class InterpretationService:
    """Runs Stage 1: interpret the user's request."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    def run(self, context: ExplorationContext) -> Interpretation:
        """Interpret the user message and return an Interpretation."""
        logger.info("Stage 1: Interpreting query: %s", context.user_message)

        user_prompt = self._build_user_prompt(context)

        result: Interpretation | None = self._llm.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=Interpretation,
        )

        if result is None:
            logger.warning(
                "Interpretation LLM returned None — defaulting to out_of_scope"
            )
            return Interpretation(
                scope="out_of_scope",
                message="The query could not be understood. Please try rephrasing your question.",
            )

        logger.info("Interpretation scope=%s", result.scope)
        return result

    # ------------------------------------------------------------------

    @staticmethod
    def _build_user_prompt(context: ExplorationContext) -> str:
        parts = [
            "Interpret the following natural language question about DBLP.",
        ]

        if context.history:
            history_lines = []
            for turn in context.history[-5:]:
                history_lines.append(f"{turn.role}: {turn.content}")
            parts.append(f"\nCONVERSATION HISTORY:\n{chr(10).join(history_lines)}")

        parts.append(f"\nQuestion: {context.user_message}")
        return "\n".join(parts)
