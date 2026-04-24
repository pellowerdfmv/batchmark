"""Tests for batchmark.classifier."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.classifier import (
    ClassifierConfig,
    ClassifiedResult,
    classify_results,
    format_classification_summary,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


def test_classify_results_returns_one_per_input():
    results = [_r(10, 0.05), _r(20, 0.5), _r(30, 2.0)]
    classified = classify_results(results)
    assert len(classified) == 3


def test_classify_fast_below_threshold():
    classified = classify_results([_r(10, 0.05)])
    assert classified[0].classification == "fast"


def test_classify_medium_between_thresholds():
    classified = classify_results([_r(10, 0.5)])
    assert classified[0].classification == "medium"


def test_classify_slow_above_threshold():
    classified = classify_results([_r(10, 1.5)])
    assert classified[0].classification == "slow"


def test_classify_failed_result():
    classified = classify_results([_r(10, 0.05, returncode=1)])
    assert classified[0].classification == "failed"


def test_classify_respects_custom_thresholds():
    cfg = ClassifierConfig(fast_below=0.01, slow_above=0.5)
    classified = classify_results([_r(10, 0.05)], config=cfg)
    assert classified[0].classification == "medium"


def test_classify_custom_labels():
    cfg = ClassifierConfig(labels={"fast": "green", "medium": "yellow", "slow": "red", "failed": "grey"})
    classified = classify_results([_r(10, 0.05)], config=cfg)
    assert classified[0].classification == "green"


def test_classified_result_properties():
    r = _r(42, 0.3)
    cr = classify_results([r])[0]
    assert cr.size == 42
    assert cr.duration == pytest.approx(0.3)
    assert cr.success is True


def test_format_classification_summary_counts():
    results = [_r(10, 0.05), _r(20, 0.5), _r(30, 2.0), _r(40, 0.1, returncode=1)]
    classified = classify_results(results)
    summary = format_classification_summary(classified)
    assert "fast" in summary
    assert "slow" in summary
    assert "failed" in summary


def test_format_classification_summary_empty():
    summary = format_classification_summary([])
    assert "no results" in summary
