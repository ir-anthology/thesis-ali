"""Tests for clarification detector."""

import pytest
from unittest.mock import Mock, patch
from src.models import (
    IntentResult,
    EntityMention,
    ResolvedEntity,
    ClarificationResult,
    Candidate,
    Constraints,
)
from src.clarification_detector import ClarificationDetector


@pytest.fixture
def detector():
    return ClarificationDetector()


def test_unresolved_entity(detector):
    intent = IntentResult(
        intent="The user is asking for publications authored by UnknownPerson",
        entities_mentioned=[EntityMention(text="UnknownPerson", type_hint="Person")],
        constraints=Constraints(),
    )
    entities = [ResolvedEntity(mention="UnknownPerson", not_found=True)]

    mock_result = ClarificationResult(
        needs_clarification=True,
        clarification="I couldn't find 'UnknownPerson' in DBLP. Could you provide more details?",
        suggestions=[
            "Show me papers by Geoffrey Hinton",
            "Show me papers by Yann LeCun",
        ],
    )

    with patch.object(
        detector.client.responses, "parse", return_value=Mock(output_parsed=mock_result)
    ):
        result = detector.detect(intent, entities)

    assert result.needs_clarification is True
    assert "couldn't find" in result.clarification.lower()


def test_ambiguous_entity(detector):
    intent = IntentResult(
        intent="The user is asking for publications authored by Smith",
        entities_mentioned=[EntityMention(text="Smith", type_hint="Person")],
        constraints=Constraints(),
    )
    entities = [
        ResolvedEntity(
            mention="Smith",
            ambiguous=True,
            candidates=[
                Candidate(uri="https://dblp.org/pid/s/JohnSmith", label="John Smith"),
                Candidate(uri="https://dblp.org/pid/s/MikeSmith", label="Mike Smith"),
            ],
        )
    ]

    mock_result = ClarificationResult(
        needs_clarification=True,
        clarification="Multiple matches found for 'Smith'. Which one did you mean?",
        suggestions=[
            "Show me papers by John Smith",
            "Show me papers by Mike Smith",
        ],
    )

    with patch.object(
        detector.client.responses, "parse", return_value=Mock(output_parsed=mock_result)
    ):
        result = detector.detect(intent, entities)

    assert result.needs_clarification is True
    assert "multiple" in result.clarification.lower()


def test_no_clarification_needed(detector):
    intent = IntentResult(
        intent="The user is asking for publications authored by Geoffrey Hinton",
        entities_mentioned=[EntityMention(text="Geoffrey Hinton", type_hint="Person")],
        constraints=Constraints(),
    )
    entities = [
        ResolvedEntity(
            mention="Geoffrey Hinton",
            uri="https://dblp.org/pid/10/3248",
            label="Geoffrey Hinton",
            type="Person",
            confidence=1.0,
        )
    ]

    mock_result = ClarificationResult(
        needs_clarification=False,
        clarification=None,
        suggestions=[],
    )

    with patch.object(
        detector.client.responses, "parse", return_value=Mock(output_parsed=mock_result)
    ):
        result = detector.detect(intent, entities)

    assert result.needs_clarification is False
    assert result.clarification is None


def test_llm_returns_none(detector):
    intent = IntentResult(
        intent="The user is asking for publications",
        entities_mentioned=[],
        constraints=Constraints(),
    )
    entities = []

    with patch.object(
        detector.client.responses, "parse", return_value=Mock(output_parsed=None)
    ):
        result = detector.detect(intent, entities)

    assert result.needs_clarification is False
    assert result.clarification is None


def test_llm_error(detector):
    intent = IntentResult(
        intent="The user is asking for publications",
        entities_mentioned=[],
        constraints=Constraints(),
    )
    entities = []

    with patch.object(
        detector.client.responses, "parse", side_effect=Exception("API Error")
    ):
        result = detector.detect(intent, entities)

    assert result.needs_clarification is False
    assert result.clarification is None
