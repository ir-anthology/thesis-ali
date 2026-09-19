"""Tests for result-analysis observation context and sampling."""

from dataclasses import dataclass, field

from backend.main.schemas.context import ExplorationContext, QueryResult
from backend.main.schemas.responses import CellValue, ResultColumn
from backend.main.services.result_analysis import ResultAnalysisService


@dataclass
class CapturingLLM:
    prompts: list[str] = field(default_factory=list)
    system_prompts: list[str] = field(default_factory=list)
    response: dict = field(
        default_factory=lambda: {"observations": ["observation"]}
    )

    def generate_json(self, *, system_prompt: str, user_prompt: str) -> dict:
        self.system_prompts.append(system_prompt)
        self.prompts.append(user_prompt)
        return self.response


def _context(row_count: int, row_values: list[str]) -> ExplorationContext:
    context = ExplorationContext(user_message="Show publications")
    context.set_query_result(
        QueryResult(
            columns=["title"],
            rows=[{"title": value} for value in row_values],
            row_count=row_count,
        )
    )
    context.set_result_table(
        [ResultColumn(key="title", label="Title")],
        [
            {"title": CellValue(value=value, question="Tell me about this")}
            for value in row_values
        ],
    )
    return context


def test_observation_prompt_includes_actual_count_and_marks_sample():
    llm = CapturingLLM()
    values = [f"Publication {i}" for i in range(37)]
    context = _context(37, values)

    observations = ResultAnalysisService(llm=llm)._generate_observations(
        context, context.result_rows
    )

    prompt = llm.prompts[0]
    assert observations == ["observation"]
    assert "ACTUAL RESULT COUNT: 37" in prompt
    assert "DATA SAMPLE:" in prompt
    assert "Row 20:" in prompt
    assert "Row 21:" not in prompt
    assert (
        "Never treat the sample row count as the total result count"
        in llm.system_prompts[0]
    )


def test_observation_prompt_uses_data_when_all_rows_are_supplied():
    llm = CapturingLLM()
    values = [f"Publication {i}" for i in range(20)]
    context = _context(20, values)

    ResultAnalysisService(llm=llm)._generate_observations(
        context, context.result_rows
    )

    prompt = llm.prompts[0]
    assert "ACTUAL RESULT COUNT: 20" in prompt
    assert "DATA:\n" in prompt
    assert "DATA SAMPLE:" not in prompt


def test_observations_are_still_capped_at_three():
    llm = CapturingLLM(response={"observations": ["one", "two", "three", "four"]})
    context = _context(1, ["Publication 1"])

    observations = ResultAnalysisService(llm=llm)._generate_observations(
        context, context.result_rows
    )

    assert observations == ["one", "two", "three"]


def test_cell_question_prompt_uses_only_cell_context():
    llm = CapturingLLM(
        response={
            "cell_questions": [
                {
                    "publication_count": {
                        "value": "2709",
                        "question": "Which publications appeared at ECIR?",
                    }
                }
            ],
            "observations": [],
        }
    )

    question = ResultAnalysisService(llm=llm).generate_cell_question(
        column="publication_count",
        value="2709",
        row={
            "venue_name": "European Conference on Advances in Information Retrieval (ECIR)",
            "publication_count": "2709",
        },
        metadata=None,
        interpretation="Let me show venues and publication counts.",
    )

    assert question == "Which publications appeared at ECIR?"
    assert "SINGLE CELL MODE" in llm.prompts[0]
    assert "Let me show venues and publication counts." in llm.prompts[0]
    assert "ORIGINAL QUESTION:" not in llm.prompts[0]
