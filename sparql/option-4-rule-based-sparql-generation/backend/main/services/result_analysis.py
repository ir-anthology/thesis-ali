"""Stage 3 — Result analysis service.

Generates cell-level questions and data-grounded observations from SPARQL
results.  Receives the full accumulated context.
"""

from __future__ import annotations

import logging

from backend.main.config import QUESTION_BATCH_SIZE
from backend.main.llm.client import LLMClient, load_prompt
from backend.main.schemas.context import ExplorationContext
from backend.main.schemas.responses import ResultColumn, CellValue

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = load_prompt("result_analysis")


class ResultAnalysisService:
    """Runs Stage 3: generate cell questions and observations."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()
        self._batch_size = QUESTION_BATCH_SIZE

    def run(
        self, context: ExplorationContext
    ) -> tuple[list[dict[str, CellValue]], list[str]]:
        """Analyse results and return (rows_with_questions, observations).

        If there are no results, returns empty lists.
        """
        if not context.query_result or context.query_result.row_count == 0:
            logger.info("Stage 3: No results to analyse")
            return [], []

        logger.info("Stage 3: Analysing %d rows", context.query_result.row_count)

        rows_with_questions = self._generate_questions(context)
        observations = self._generate_observations(context, rows_with_questions)

        return rows_with_questions, observations

    # ------------------------------------------------------------------
    # Cell questions
    # ------------------------------------------------------------------

    def _generate_questions(
        self, context: ExplorationContext
    ) -> list[dict[str, CellValue]]:
        columns = context.result_columns
        raw_rows = context.query_result.rows  # type: ignore[union-attr]
        all_rows: list[dict[str, CellValue]] = []

        for batch_start in range(0, len(raw_rows), self._batch_size):
            batch = raw_rows[batch_start : batch_start + self._batch_size]
            batch_result = self._generate_questions_batch(
                context, columns, batch, batch_start
            )
            all_rows.extend(batch_result)

        return all_rows

    def _generate_questions_batch(
        self,
        context: ExplorationContext,
        columns: list[ResultColumn],
        batch_rows: list[dict[str, object]],
        offset: int,
    ) -> list[dict[str, CellValue]]:
        col_keys = [c.key for c in columns]

        # Build row descriptions
        rows_context: list[str] = []
        for i, row in enumerate(batch_rows):
            row_num = offset + i + 1
            row_str = ", ".join(f"{k}: {row.get(k, '')}" for k in col_keys)
            rows_context.append(f"Row {row_num}: {row_str}")

        user_prompt = (
            f"ORIGINAL QUESTION: {context.user_message}\n\n"
            f"COLUMNS: {', '.join(col_keys)}\n\n"
            f"ROWS:\n{chr(10).join(rows_context)}"
        )

        data = self._llm.generate_json(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        if data is None:
            logger.warning("Stage 3: LLM returned None for questions")
            # Fallback: rows without questions
            return [
                {k: CellValue(value=str(row.get(k, "")), question="") for k in col_keys}
                for row in batch_rows
            ]

        logger.info("Stage 3: LLM response keys: %s", list(data.keys()))
        return self._parse_cell_questions(data, col_keys, batch_rows)

    @staticmethod
    def _parse_cell_questions(
        data: dict,
        col_keys: list[str],
        batch_rows: list[dict[str, object]],
    ) -> list[dict[str, CellValue]]:
        result: list[dict[str, CellValue]] = []

        # Try multiple possible keys for the questions data
        llm_rows = None
        for key in ["cell_questions", "rows", "questions"]:
            if key in data:
                llm_rows = data[key]
                logger.info("Stage 3: Found questions under key '%s'", key)
                break

        if llm_rows is None:
            logger.warning(
                "Stage 3: No questions key found in LLM response: %s", list(data.keys())
            )
            # Fallback: rows without questions
            return [
                {k: CellValue(value=str(row.get(k, "")), question="") for k in col_keys}
                for row in batch_rows
            ]

        for i, row in enumerate(batch_rows):
            parsed: dict[str, CellValue] = {}
            # llm_rows may be a list or a dict keyed by row index
            if isinstance(llm_rows, dict):
                llm_row = llm_rows.get(str(i), llm_rows.get(i, {}))
            elif isinstance(llm_rows, list) and i < len(llm_rows):
                llm_row = llm_rows[i]
            else:
                llm_row = {}

            for k in col_keys:
                value = str(row.get(k, ""))
                question = ""
                cell_data = llm_row.get(k)
                if isinstance(cell_data, dict):
                    question = cell_data.get("question", "")
                elif isinstance(cell_data, str):
                    question = cell_data
                parsed[k] = CellValue(value=value, question=question)

            result.append(parsed)

        return result

    # ------------------------------------------------------------------
    # Observations
    # ------------------------------------------------------------------

    def _generate_observations(
        self,
        context: ExplorationContext,
        rows_with_questions: list[dict[str, CellValue]],
    ) -> list[str]:
        columns = context.result_columns
        # Use first 20 rows for observation generation
        sample_rows = rows_with_questions[:20]

        columns_str = ", ".join(c.label for c in columns)
        rows_context: list[str] = []
        for i, row in enumerate(sample_rows):
            parts = [
                f"{c.label}: {row.get(c.key, CellValue(value='', question='')).value}"
                for c in columns
            ]
            rows_context.append(f"Row {i + 1}: {', '.join(parts)}")

        user_prompt = (
            f"ORIGINAL QUESTION: {context.user_message}\n\n"
            f"COLUMNS: {columns_str}\n\n"
            f"DATA:\n{chr(10).join(rows_context)}"
        )

        data = self._llm.generate_json(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        if data is None:
            return []

        observations = data.get("observations", [])
        return observations[:3] if observations else []
