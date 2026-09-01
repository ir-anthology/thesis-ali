"""Step 1: LLM-based intent classification with limitation detection."""

import logging
from openai import OpenAI
from .config import OPENAI_API_KEY, LLM_MODEL
from .models import IntentResult, Constraints
from .prompts import INTENT_SYSTEM_PROMPT, build_intent_prompt

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user query intent using LLM."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL

    def classify(self, user_query: str) -> IntentResult:
        """Classify the intent of a user query.

        Args:
            user_query: Natural language question about DBLP

        Returns:
            IntentResult with intent, entity mentions, constraints, and limitation info
        """
        logger.info("Classifying intent for query: %s", user_query)

        prompt = build_intent_prompt(user_query)

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                text_format=IntentResult,
            )

            result = response.output_parsed

            if result is None:
                logger.warning("LLM returned None for intent classification")
                return IntentResult(
                    intent="The user's query could not be understood",
                    entities_mentioned=[],
                    constraints=Constraints(),
                    has_limitation=False,
                    limitation=None,
                    suggestions=[],
                )

            logger.info(
                "Classified intent: %s, entities: %d, has_limitation: %s",
                result.intent,
                len(result.entities_mentioned),
                result.has_limitation,
            )
            return result

        except Exception as e:
            logger.error("Intent classification failed: %s", str(e))
            return IntentResult(
                intent="The user's query could not be processed due to an error",
                entities_mentioned=[],
                constraints=Constraints(),
                has_limitation=False,
                limitation=None,
                suggestions=[],
            )
