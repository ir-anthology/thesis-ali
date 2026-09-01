"""Step 3: LLM-based clarification detection for DBLP queries."""

import logging
from openai import OpenAI
from .config import OPENAI_API_KEY, LLM_MODEL
from .models import IntentResult, ResolvedEntity, ClarificationResult
from .prompts import (
    CLARIFICATION_SYSTEM_PROMPT,
    build_clarification_prompt,
    format_entities_for_prompt,
)

logger = logging.getLogger(__name__)


class ClarificationDetector:
    """Detects if clarification is needed using LLM."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL

    def detect(
        self,
        intent_result: IntentResult,
        resolved_entities: list[ResolvedEntity],
    ) -> ClarificationResult:
        """Detect if clarification is needed using LLM.

        Args:
            intent_result: Result from intent classification
            resolved_entities: List of resolved entities

        Returns:
            ClarificationResult with clarification status and message
        """
        logger.info("Checking clarification needs for intent: %s", intent_result.intent)

        # Build context for LLM
        entities_context = format_entities_for_prompt(resolved_entities)
        prompt = build_clarification_prompt(intent_result.intent, entities_context)

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": CLARIFICATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                text_format=ClarificationResult,
            )

            result = response.output_parsed

            if result is None:
                logger.warning("LLM returned None for clarification detection")
                return ClarificationResult(
                    needs_clarification=False,
                    clarification=None,
                    suggestions=[],
                )

            if result.needs_clarification:
                logger.info("Clarification needed: %s", result.clarification)
            else:
                logger.info("No clarification needed")

            return result

        except Exception as e:
            logger.error("Clarification detection failed: %s", str(e))
            return ClarificationResult(
                needs_clarification=False,
                clarification=None,
                suggestions=[],
            )
