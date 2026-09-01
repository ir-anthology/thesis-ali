"""Step 8: Generate observations about query results using LLM."""

import json
import logging
from openai import OpenAI
from .config import OPENAI_API_KEY, LLM_MODEL
from .models import ResultColumn, CellValue
from .prompts import OBSERVATION_GENERATION_PROMPT

logger = logging.getLogger(__name__)


class ObservationGenerator:
    """Generates observations about query results using LLM."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL

    def generate(
        self,
        user_query: str,
        intent: str,
        columns: list[ResultColumn],
        rows: list[dict[str, CellValue]],
    ) -> list[str]:
        """Generate 1-3 observations about the data.

        Args:
            user_query: Original user question
            intent: Intent description
            columns: Column definitions
            rows: Data rows with cell values

        Returns:
            List of 1-3 observation strings
        """
        logger.info("Generating observations for %d rows", len(rows))

        if not rows:
            return []

        # Build context for LLM
        columns_str = ", ".join([col.label for col in columns])

        # Build rows context (limit to first 20 rows for prompt)
        rows_context = []
        for i, row in enumerate(rows[:20]):
            row_parts = []
            for col in columns:
                cell = row.get(col.key)
                if cell:
                    row_parts.append(f"{col.label}: {cell.value}")
            rows_context.append(f"Row {i + 1}: {', '.join(row_parts)}")

        prompt = f"""Generate observations about the following DBLP query results.

ORIGINAL QUESTION: {user_query}
INTENT: {intent}

COLUMNS: {columns_str}

DATA:
{chr(10).join(rows_context)}

Generate 1-3 key observations about this data. Focus on:
- Patterns or trends
- Notable findings
- Rankings or comparisons
- Statistical insights

Return a JSON object with structure:
{{
  "observations": ["observation 1", "observation 2", "observation 3"]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": OBSERVATION_GENERATION_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                observations = data.get("observations", [])
                # Ensure 1-3 observations
                return observations[:3] if observations else []

        except Exception as e:
            logger.error("Observation generation failed: %s", str(e))

        return []

    def close(self):
        """Close resources."""
        pass
