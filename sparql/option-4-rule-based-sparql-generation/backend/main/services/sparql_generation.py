"""Stage 2 — SPARQL generation service.

Receives the accumulated context (including interpretation) and produces a
SPARQL query.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from backend.main.config import EXAMPLES_PATH
from backend.main.llm.client import LLMClient, load_prompt
from backend.main.schema.provider import DBLPSchemaProvider
from backend.main.schemas.context import ExplorationContext
from backend.main.schemas.llm import SPARQLGeneration

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = load_prompt("sparql_generation")


class SPARQLGenerationService:
    """Runs Stage 2: generate a SPARQL query from the interpreted request."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        schema_provider: DBLPSchemaProvider | None = None,
    ) -> None:
        self._llm = llm or LLMClient()
        self._schema = schema_provider or DBLPSchemaProvider()
        self._examples = self._load_examples()

    def run(self, context: ExplorationContext) -> SPARQLGeneration | None:
        """Generate a SPARQL query.  Returns None on failure."""
        logger.info("Stage 2: Generating SPARQL")

        user_prompt = self._build_user_prompt(context)

        result = self._llm.generate_structured(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=SPARQLGeneration,
        )

        if result is None or not result.query.strip():
            logger.warning("SPARQL generation returned empty result")
            return None

        # Ensure prefixes are present
        query = result.query
        if "PREFIX" not in query.upper():
            query = self._schema.get_prefixes() + "\n" + query

        result = SPARQLGeneration(query=query)
        logger.info("SPARQL generated (%d chars)", len(result.query))
        return result

    # ------------------------------------------------------------------

    def _build_user_prompt(self, context: ExplorationContext) -> str:
        parts: list[str] = []

        # Schema context
        if context.dblp_schema:
            parts.append(f"DBLP SCHEMA:\n{context.dblp_schema}")

        # Few-shot examples
        examples_ctx = self._format_examples()
        if examples_ctx:
            parts.append(f"\nEXAMPLES:\n{examples_ctx}")

        # Interpretation context
        if context.interpretation:
            interp = context.interpretation
            parts.append(f"\nINTERPRETED REQUEST:")
            parts.append(f"Summary: {interp.summary}")
            if interp.entities:
                parts.append(f"Entities: {', '.join(interp.entities)}")
            if interp.constraints:
                parts.append(f"Constraints: {', '.join(interp.constraints)}")
            if interp.requested_information:
                parts.append(f"Requested: {', '.join(interp.requested_information)}")

        # History context (for resolving references)
        if context.history:
            history_lines = []
            for turn in context.history[-3:]:
                history_lines.append(f"{turn.role}: {turn.content}")
            parts.append(f"\nRECENT CONVERSATION:\n{chr(10).join(history_lines)}")

        parts.append(f"\nQUESTION:\n{context.user_message}")
        parts.append(
            "\nGenerate a SPARQL query for this question using entity names (not URIs)."
        )

        return "\n".join(parts)

    def _format_examples(self) -> str:
        if not self._examples:
            return ""
        lines: list[str] = []
        for i, ex in enumerate(self._examples[:5], 1):
            lines.append(f"Example {i}:")
            lines.append(f"  Question: {ex.get('question', '')}")
            lines.append(f"  SPARQL: {ex.get('sparql', '')}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _load_examples() -> list[dict]:
        if EXAMPLES_PATH.exists():
            try:
                with open(EXAMPLES_PATH, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.warning("Could not load examples from %s", EXAMPLES_PATH)
        return []
