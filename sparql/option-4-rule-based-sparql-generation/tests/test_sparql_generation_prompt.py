"""Regression tests for the SPARQL-generation limit policy."""

from pathlib import Path


PROMPT_PATH = (
    Path(__file__).parents[1]
    / "backend"
    / "main"
    / "llm"
    / "prompts"
    / "sparql_generation.txt"
)


def test_prompt_leaves_limit_selection_to_the_llm():
    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    assert prompt.count("RESULT LIMIT POLICY") == 1
    policy_start = prompt.index("RESULT LIMIT POLICY")
    query_rules_start = prompt.index("QUERY RULES")
    conference_rules_start = prompt.index("For conference years")
    policy = prompt[policy_start:query_rules_start]
    query_rules = prompt[query_rules_start:conference_rules_start]

    assert "LIMIT 15" not in prompt
    assert "LIMIT 50" not in prompt
    assert "LIMIT 100" not in prompt
    assert "number of structured SPARQL solution" in policy
    assert "explicit result quantity" in policy
    assert '"show 5 authors" → LIMIT 5' in policy
    assert '"top 20 publications" → LIMIT 20' in policy
    assert "years, dates, publication counts" in policy
    assert "a few" in policy
    assert "user may not know the result count in advance" in policy
    assert "broad, exploratory" in policy
    assert "prefer a bounded sample" in policy
    assert "Derive that limit" in policy
    assert "dynamically from the filters" in policy
    assert "LIMIT 1" in policy
    assert "5. Ranking, aggregation, and grouping" in policy
    assert "exploring a ranked subset" in policy
    assert "LIMIT and OFFSET" in policy
    assert "If the user explicitly requests all matching results, omit LIMIT" in policy
    assert "Do not use a predefined default LIMIT" in policy
    assert "fixed fallback" in policy
    assert "Every query must reflect an" in policy
    assert "intentional LIMIT decision" in policy
    assert "Apply this hierarchy" in policy
    assert "honor explicit quantity or pagination" in policy
    assert "implicit exploratory requests" in policy
    assert "never" in policy
    assert "invent a fixed default number" in policy
    assert "unspecified quantity does not mean" in policy
    assert "unstructured information" in policy
    assert "LIMIT does not make unavailable DBLP information available" in policy
    assert "Every generated SELECT query must include a LIMIT" not in prompt
    assert "smallest result set" not in prompt
    assert "LIMIT" not in query_rules
    assert "count\nlimits" not in prompt
