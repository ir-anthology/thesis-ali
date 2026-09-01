"""Tests for limitation detector."""

import pytest
from src.models import IntentResult, IntentType, LimitationResult
from src.limitation_detector import LimitationDetector


@pytest.fixture
def detector():
    return LimitationDetector()


def test_citation_limitation(detector):
    intent = IntentResult(intent=IntentType.count_publications)
    result = detector.detect("How many citations does this paper have?", intent)
    assert result.has_limitation is True
    assert "citation" in result.limitation.lower()


def test_abstract_limitation(detector):
    intent = IntentResult(intent=IntentType.unknown)
    result = detector.detect("What is the abstract of this paper?", intent)
    assert result.has_limitation is True
    assert "abstract" in result.limitation.lower()


def test_fulltext_limitation(detector):
    intent = IntentResult(intent=IntentType.unknown)
    result = detector.detect("Where can I find the full text?", intent)
    assert result.has_limitation is True
    assert "full text" in result.limitation.lower()


def test_impact_factor_limitation(detector):
    intent = IntentResult(intent=IntentType.find_venue_info)
    result = detector.detect("What is the impact factor of TODS?", intent)
    assert result.has_limitation is True
    assert "impact factor" in result.limitation.lower()


def test_no_limitation(detector):
    intent = IntentResult(intent=IntentType.find_publications_by_author)
    result = detector.detect("Papers by Geoffrey Hinton", intent)
    assert result.has_limitation is False
    assert result.limitation is None


def test_non_cs_topic(detector):
    intent = IntentResult(intent=IntentType.unknown)
    result = detector.detect("Papers about biology", intent)
    assert result.has_limitation is True
    assert "biology" in result.limitation.lower()
