"""Unified query interpretation: single LLM call for intent, entities, and outcome."""

import logging
from openai import OpenAI
from .config import OPENAI_API_KEY, LLM_MODEL
from .models import QueryInterpretation, HistoryTurn
from .prompts import INTERPRETATION_SYSTEM_PROMPT, build_interpretation_prompt

logger = logging.getLogger(__name__)


class QueryInterpreter:
    """Interprets user queries using a single LLM call.

    Categorizes queries into one of three outcomes:
    - clear: Query is answerable via DBLP, proceed with SPARQL generation
    - ambiguous: Query needs clarification, return options
    - out_of_scope: Query cannot be answered via DBLP
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL

    def interpret(
        self,
        user_query: str,
        history: list[HistoryTurn] | None = None,
    ) -> QueryInterpretation:
        """Interpret the user query.

        Args:
            user_query: Natural language question about DBLP
            history: Optional conversation history for context

        Returns:
            QueryInterpretation with outcome, intent, and relevant fields
        """
        logger.info("Interpreting query: %s", user_query)

        prompt = build_interpretation_prompt(user_query, history)

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": INTERPRETATION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                text_format=QueryInterpretation,
            )

            result = response.output_parsed

            if result is None:
                logger.warning("LLM returned None for query interpretation")
                return QueryInterpretation(
                    outcome="out_of_scope",
                    intent="The query could not be understood",
                    entities_mentioned=[],
                    limitation="I couldn't understand your query. Please try rephrasing.",
                    suggestions=[
                        "Ask about authors",
                        "Ask about publications",
                        "Ask about venues",
                    ],
                )

            logger.info(
                "Interpretation outcome: %s, entities: %d",
                result.outcome,
                len(result.entities_mentioned),
            )
            return result

        except Exception as e:
            logger.error("Query interpretation failed: %s", str(e))
            return QueryInterpretation(
                outcome="out_of_scope",
                intent="An error occurred while processing the query",
                entities_mentioned=[],
                limitation=f"An error occurred while processing your query: {str(e)}",
                suggestions=[
                    "Ask about authors",
                    "Ask about publications",
                    "Ask about venues",
                ],
            )
