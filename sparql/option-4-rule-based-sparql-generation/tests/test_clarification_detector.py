"""Tests for clarification detector."""

import pytest
from src.models import (
    IntentResult,
    IntentType,
    EntityMention,
    ResolvedEntity,
    ClarificationResult,
    Candidate,
)
from src.clarification_detector import ClarificationDetector


@pytest.fixture
def detector():
    return ClarificationDetector()


def test_unresolved_entity(detector):
    intent = IntentResult(
        intent=IntentType.find_publications_by_author,
        entities_mentioned=[EntityMention(text="UnknownPerson", type_hint="Person")],
    )
    entities = [ResolvedEntity(mention="UnknownPerson", not_found=True)]
    result = detector.detect(intent, entities)
    assert result.needs_clarification is True
    assert "couldn't find" in result.clarification.lower()


def test_ambiguous_entity(detector):
    intent = IntentResult(
        intent=IntentType.find_publications_by_author,
        entities_mentioned=[EntityMention(text="Smith", type_hint="Person")],
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
    result = detector.detect(intent, entities)
    assert result.needs_clarification is True
    assert "multiple" in result.clarification.lower()


def test_missing_author(detector):
    intent = IntentResult(
        intent=IntentType.find_publications_by_author,
        entities_mentioned=[],
    )
    entities = []
    result = detector.detect(intent, entities)
    assert result.needs_clarification is True
    assert "author" in result.clarification.lower()


def test_missing_venue(detector):
    intent = IntentResult(
        intent=IntentType.find_publications_by_venue,
        entities_mentioned=[],
    )
    entities = []
    result = detector.detect(intent, entities)
    assert result.needs_clarification is True
    assert "venue" in result.clarification.lower()


def test_no_clarification_needed(detector):
    intent = IntentResult(
        intent=IntentType.find_publications_by_author,
        entities_mentioned=[EntityMention(text="Geoffrey Hinton", type_hint="Person")],
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
    result = detector.detect(intent, entities)
    assert result.needs_clarification is False
    assert result.clarification is None


def test_llm_flagged_clarification(detector):
    intent = IntentResult(
        intent=IntentType.find_publications_by_author,
        needs_clarification=True,
        clarification_question="Which author do you mean?",
    )
    entities = []
    result = detector.detect(intent, entities)
    assert result.needs_clarification is True
    assert "which author" in result.clarification.lower()
