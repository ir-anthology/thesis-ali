from unittest.mock import Mock

from backend.main.schemas.context import ExplorationContext
from backend.main.schemas.llm import Interpretation
from backend.main.schemas.requests import EntityInteraction
from backend.main.services.interpretation import InterpretationService


def test_interpretation_preserves_ambiguous_suggestions():
    expected = Interpretation(
        scope="ambiguous",
        message="Which Smith did you mean?",
        suggestions=["Show me papers by John Smith", "Show me papers by Mike Smith"],
    )
    llm = Mock()
    llm.generate_structured.return_value = expected
    service = InterpretationService(llm=llm)

    result = service.run(ExplorationContext(user_message="papers by Smith"))

    assert result.scope == "ambiguous"
    assert result.suggestions == expected.suggestions


def test_selected_entity_cannot_remain_ambiguous():
    llm = Mock()
    llm.generate_structured.return_value = Interpretation(
        scope="ambiguous",
        message="The request could mean several things.",
        suggestions=["Show me this author's papers"],
    )
    service = InterpretationService(llm=llm)
    context = ExplorationContext(
        user_message="Tell me more",
        interaction=EntityInteraction(
            entity_id="https://dblp.org/pid/10/3248",
            entity_type="author",
        ),
    )

    result = service.run(context)

    assert result.scope == "in_scope"
    assert result.suggestions == []
    assert "selected" not in result.message.lower()


def test_selected_entity_is_in_interpretation_prompt():
    context = ExplorationContext(
        user_message="Show me more",
        interaction=EntityInteraction(
            entity_id="https://dblp.org/pid/10/3248",
            entity_type="author",
        ),
    )

    prompt = InterpretationService._build_user_prompt(context)

    assert "https://dblp.org/pid/10/3248" in prompt
    assert "Do not resolve this entity by name" in prompt
