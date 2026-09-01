"""Step 5: LLM-based SPARQL query generation."""

import json
import logging
from pathlib import Path
from openai import OpenAI
from .config import (
    OPENAI_API_KEY,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    EXAMPLES_PATH,
    DBLP_PREFIXES,
)
from .models import ResolvedEntity, SPARQLResult
from .prompts import (
    SPARQL_SYSTEM_PROMPT,
    build_sparql_prompt,
    format_entities_for_prompt,
    format_examples_for_prompt,
)

logger = logging.getLogger(__name__)


class SPARQLGenerator:
    """Generates SPARQL queries using LLM."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL
        self.examples = self._load_examples()

    def _load_examples(self) -> list[dict]:
        """Load few-shot examples from file."""
        if EXAMPLES_PATH.exists():
            try:
                with open(EXAMPLES_PATH) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning("Could not load examples: %s", str(e))
        return []

    def generate(
        self,
        user_query: str,
        resolved_entities: list[ResolvedEntity],
        schema_context: str = "",
    ) -> SPARQLResult:
        """Generate a SPARQL query for the given question.

        Args:
            user_query: Original natural language question
            resolved_entities: List of resolved entities with URIs
            schema_context: Optional schema context for prompting

        Returns:
            SPARQLResult with generated SPARQL query and confidence
        """
        logger.info("Generating SPARQL for query: %s", user_query)

        entities_context = format_entities_for_prompt(resolved_entities)
        examples_context = format_examples_for_prompt(self.examples[:5])

        prompt = build_sparql_prompt(
            user_query, entities_context, schema_context, examples_context
        )

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": SPARQL_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                text_format=SPARQLResult,
            )

            result = response.output_parsed

            if result is None:
                logger.warning("LLM returned None for SPARQL generation")
                return SPARQLResult(
                    sparql="",
                    confidence=0.0,
                    explanation="Failed to generate SPARQL query",
                )

            # Ensure prefixes are included
            if result.sparql and "PREFIX" not in result.sparql.upper():
                result.sparql = DBLP_PREFIXES + "\n" + result.sparql

            logger.info("Generated SPARQL with confidence: %.2f", result.confidence)
            return result

        except Exception as e:
            logger.error("SPARQL generation failed: %s", str(e))
            return SPARQLResult(
                sparql="",
                confidence=0.0,
                explanation=f"Error generating SPARQL: {str(e)}",
            )

    def repair(
        self,
        original_query: str,
        failed_sparql: str,
        error_message: str,
        resolved_entities: list[ResolvedEntity],
    ) -> SPARQLResult:
        """Attempt to repair a failed SPARQL query.

        Args:
            original_query: Original natural language question
            failed_sparql: The SPARQL query that failed
            error_message: Error message from execution
            resolved_entities: List of resolved entities

        Returns:
            SPARQLResult with repaired SPARQL query
        """
        logger.info("Attempting to repair SPARQL query")

        entities_context = format_entities_for_prompt(resolved_entities)

        repair_prompt = f"""The following SPARQL query failed:

{failed_sparql}

Error: {error_message}

Original question: {original_query}

Resolved entities:
{entities_context}

Fix the query and return a corrected SPARQL query that will work against the DBLP endpoint."""

        try:
            response = self.client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": SPARQL_SYSTEM_PROMPT},
                    {"role": "user", "content": repair_prompt},
                ],
                text_format=SPARQLResult,
            )

            result = response.output_parsed

            if result is None:
                logger.warning("LLM returned None for SPARQL repair")
                return SPARQLResult(
                    sparql=failed_sparql,
                    confidence=0.0,
                    explanation="Failed to repair SPARQL query",
                )

            # Ensure prefixes are included
            if result.sparql and "PREFIX" not in result.sparql.upper():
                result.sparql = DBLP_PREFIXES + "\n" + result.sparql

            logger.info("Repaired SPARQL with confidence: %.2f", result.confidence)
            return result

        except Exception as e:
            logger.error("SPARQL repair failed: %s", str(e))
            return SPARQLResult(
                sparql=failed_sparql,
                confidence=0.0,
                explanation=f"Error repairing SPARQL: {str(e)}",
            )
