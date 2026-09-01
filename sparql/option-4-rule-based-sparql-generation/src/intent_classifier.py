"""Step 1: LLM-based intent classification for DBLP queries."""

import logging
from openai import OpenAI
from .config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS
from .models import IntentResult, IntentType
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
            IntentResult with classified intent, entity mentions, and constraints
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
                    intent=IntentType.unknown,
                    entities_mentioned=[],
                    constraints={},
                    needs_clarification=True,
                    clarification_question="I couldn't understand your query. Could you rephrase it?",
                )

            logger.info(
                "Classified intent: %s, entities: %d",
                result.intent.value,
                len(result.entities_mentioned),
            )
            return result

        except Exception as e:
            logger.error("Intent classification failed: %s", str(e))
            return IntentResult(
                intent=IntentType.unknown,
                entities_mentioned=[],
                constraints={},
                needs_clarification=True,
                clarification_question=f"I encountered an error processing your query: {str(e)}",
            )
