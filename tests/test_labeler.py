"""Tests for batchmark.labeler."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.labeler import (
    LabelConfig,
    LabeledResult,
    available_labels,
    group_by_label,
    label_results,
)


def _r(size: int, returncode: int = 0, duration: float = 1.0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, output="")


# ---------------------------------------------------------------------------
# label_results
# ---------------------------------------------------------------------------

def test_label_results_applies_correct_label():
    config = LabelConfig(label_map={"small": [10, 20], "large": [100]})
    results = [_r(10), _r(100)]
    labeled = label_results(results, config)
    assert labeled[0].label == "small"
    assert labeled[1].label == "large"


def test_label_results_uses_default_for_unknown_size():
    config = LabelConfig(label_map={"small": [10]}, default_label="other")
    labeled = label_results([_r(999)], config)
    assert labeled[0].label == "other"


def test_label_results_empty_input():
    config = LabelConfig()
    assert label_results([], config) == []


def test_label_results_preserves_result_reference():
    r = _r(42)
    config = LabelConfig(label_map={"mid": [42]})
    labeled = label_results([r], config)
    assert labeled[0].result is r


def test_labeled_result_proxies_size_and_duration():
    r = _r(size=50, duration=3.14)
    lr = LabeledResult(result=r, label="test")
    assert lr.size == 50
    assert lr.duration == 3.14


def test_labeled_result_success_flag_true():
    lr = LabeledResult(result=_r(1, returncode=0), label="ok")
    assert lr.success is True


def test_labeled_result_success_flag_false():
    lr = LabeledResult(result=_r(1, returncode=1), label="fail")
    assert lr.success is False


# ---------------------------------------------------------------------------
# group_by_label
# ---------------------------------------------------------------------------

def test_group_by_label_creates_correct_keys():
    config = LabelConfig(label_map={"a": [1], "b": [2]})
    labeled = label_results([_r(1), _r(2)], config)
    groups = group_by_label(labeled)
    assert set(groups.keys()) == {"a", "b"}


def test_group_by_label_puts_items_in_right_bucket():
    config = LabelConfig(label_map={"x": [10, 20]})
    labeled = label_results([_r(10), _r(20)], config)
    groups = group_by_label(labeled)
    assert len(groups["x"]) == 2


def test_group_by_label_empty_input():
    assert group_by_label([]) == {}


# ---------------------------------------------------------------------------
# available_labels
# ---------------------------------------------------------------------------

def test_available_labels_sorted():
    config = LabelConfig(label_map={"z": [1], "a": [2]})
    labeled = label_results([_r(1), _r(2)], config)
    assert available_labels(labeled) == ["a", "z"]


def test_available_labels_deduplicates():
    config = LabelConfig(label_map={"same": [1, 2]})
    labeled = label_results([_r(1), _r(2)], config)
    assert available_labels(labeled) == ["same"]
