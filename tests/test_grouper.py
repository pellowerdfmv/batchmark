"""Tests for batchmark.grouper."""

from batchmark.timer import TimingResult
from batchmark.grouper import (
    GroupConfig,
    GroupedResult,
    _find_label,
    group_results,
    results_by_label,
)


def _r(size: int, returncode: int = 0, duration: float = 0.1) -> TimingResult:
    return TimingResult(size=size, returncode=returncode, duration=duration, stdout="", stderr="")


DEFAULT_CONFIG = GroupConfig(
    buckets=[
        ("small", 1, 100),
        ("medium", 101, 1000),
        ("large", 1001, None),
    ],
    default_label="unknown",
)


def test_find_label_small():
    assert _find_label(50, DEFAULT_CONFIG) == "small"


def test_find_label_medium():
    assert _find_label(500, DEFAULT_CONFIG) == "medium"


def test_find_label_large():
    assert _find_label(5000, DEFAULT_CONFIG) == "large"


def test_find_label_boundary_inclusive():
    assert _find_label(100, DEFAULT_CONFIG) == "small"
    assert _find_label(101, DEFAULT_CONFIG) == "medium"
    assert _find_label(1001, DEFAULT_CONFIG) == "large"


def test_find_label_default_when_no_match():
    cfg = GroupConfig(buckets=[("only", 10, 20)], default_label="other")
    assert _find_label(5, cfg) == "other"
    assert _find_label(99, cfg) == "other"


def test_group_results_returns_one_per_result():
    results = [_r(10), _r(200), _r(2000)]
    grouped = group_results(results, DEFAULT_CONFIG)
    assert len(grouped) == 3


def test_group_results_labels_correct():
    results = [_r(10), _r(500), _r(9999)]
    grouped = group_results(results, DEFAULT_CONFIG)
    assert grouped[0].label == "small"
    assert grouped[1].label == "medium"
    assert grouped[2].label == "large"


def test_group_results_preserves_result_reference():
    r = _r(42)
    grouped = group_results([r], DEFAULT_CONFIG)
    assert grouped[0].result is r


def test_grouped_result_properties():
    r = _r(size=77, returncode=0, duration=0.25)
    g = GroupedResult(result=r, label="small")
    assert g.size == 77
    assert g.duration == 0.25
    assert g.success is True


def test_grouped_result_failure():
    r = _r(size=10, returncode=1)
    g = GroupedResult(result=r, label="small")
    assert g.success is False


def test_results_by_label_groups_correctly():
    results = [_r(10), _r(20), _r(500)]
    grouped = group_results(results, DEFAULT_CONFIG)
    by_label = results_by_label(grouped)
    assert "small" in by_label
    assert "medium" in by_label
    assert len(by_label["small"]) == 2
    assert len(by_label["medium"]) == 1


def test_results_by_label_empty_input():
    assert results_by_label([]) == {}
