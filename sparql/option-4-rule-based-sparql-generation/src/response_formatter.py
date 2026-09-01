"""Step 7: Format SPARQL results with questions for each cell."""

import json
import logging
from openai import OpenAI
from .config import OPENAI_API_KEY, LLM_MODEL
from .models import (
    QueryExecutionResult,
    ColumnDef,
    CellValue,
    FormattedResponse,
)
from .prompts import QUESTION_GENERATION_PROMPT

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formats SPARQL results with questions for each cell."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = LLM_MODEL

    def format(
        self,
        user_query: str,
        execution_result: QueryExecutionResult,
        intent: str,
    ) -> FormattedResponse:
        """Format execution result with questions.

        Args:
            user_query: Original user question
            execution_result: Result from SPARQL execution
            intent: Intent description

        Returns:
            FormattedResponse with columns, rows, and questions
        """
        logger.info("Formatting response with %d rows", execution_result.row_count)

        # Handle empty results
        if execution_result.row_count == 0:
            return FormattedResponse(
                columns=[
                    ColumnDef(key=col, label=col.replace("_", " ").title())
                    for col in execution_result.columns
                ],
                rows=[],
                row_count=0,
                query_explanation="No results found for this query.",
            )

        # Create column definitions
        columns = [
            ColumnDef(key=col, label=col.replace("_", " ").title())
            for col in execution_result.columns
        ]

        # Generate questions for all cells using LLM
        rows_with_questions = self._generate_questions(
            user_query, intent, execution_result.columns, execution_result.rows
        )

        return FormattedResponse(
            columns=columns,
            rows=rows_with_questions,
            row_count=execution_result.row_count,
            query_explanation=f"Found {execution_result.row_count} results.",
        )

    def _generate_questions(
        self,
        user_query: str,
        intent: str,
        columns: list[str],
        rows: list[dict[str, str]],
    ) -> list[dict[str, CellValue]]:
        """Generate questions for all cells using LLM.

        Args:
            user_query: Original user question
            intent: Intent description
            columns: Column names
            rows: Raw rows from SPARQL execution

        Returns:
            List of rows with CellValue objects containing values and questions
        """
        logger.info("Generating questions for %d rows", len(rows))

        # Build context for LLM (limit to first 10 rows for prompt)
        rows_context = []
        for i, row in enumerate(rows[:10]):
            row_str = ", ".join([f"{col}: {row.get(col, '')}" for col in columns])
            rows_context.append(f"Row {i + 1}: {row_str}")

        prompt = f"""Generate a question for each cell in the following SPARQL query results.

ORIGINAL QUESTION: {user_query}
INTENT: {intent}

COLUMNS: {", ".join(columns)}

ROWS:
{chr(10).join(rows_context)}

For each cell, generate a natural language question that:
1. Is self-contained (no placeholders)
2. Can be answered by DBLP
3. Relates to the cell value and column context
4. Uses entity names from other columns when relevant

Return a JSON object with structure:
{{
  "rows": [
    {{
      "column_name": {{"value": "cell_value", "question": "generated question"}},
      ...
    }},
    ...
  ]
}}"""

        try:
            # Use a simpler approach - generate questions as JSON
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": QUESTION_GENERATION_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                return self._parse_questions(data, columns, rows)

        except Exception as e:
            logger.error("Question generation failed: %s", str(e))

        # Fallback: return rows without questions
        return [
            {col: CellValue(value=row.get(col, ""), question="") for col in columns}
            for row in rows
        ]

    def _parse_questions(
        self,
        data: dict,
        columns: list[str],
        rows: list[dict[str, str]],
    ) -> list[dict[str, CellValue]]:
        """Parse LLM response and create CellValue objects.

        Args:
            data: Parsed JSON from LLM
            columns: Column names
            rows: Raw rows from SPARQL execution

        Returns:
            List of rows with CellValue objects
        """
        result_rows = []
        llm_rows = data.get("rows", [])

        for i, row in enumerate(rows):
            result_row = {}
            llm_row = llm_rows[i] if i < len(llm_rows) else {}

            for col in columns:
                value = row.get(col, "")
                question = ""

                # Get question from LLM response
                if col in llm_row:
                    cell_data = llm_row[col]
                    if isinstance(cell_data, dict):
                        question = cell_data.get("question", "")
                    elif isinstance(cell_data, str):
                        question = cell_data

                result_row[col] = CellValue(value=value, question=question)

            result_rows.append(result_row)

        return result_rows

    def close(self):
        """Close resources."""
        pass
