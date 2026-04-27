"""Tests for batchmark.flattener."""

from __future__ import annotations

from batchmark.flattener import (
    FlattenConfig,
    FlattenedResult,
    flatten_results,
    format_flatten_summary,
)
from batchmark.timer import TimingResult


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_flatten_results_returns_one_per_input():
    group = [_r(10, 0.1), _r(20, 0.2)]
    results = flatten_results([group])
    assert len(results) == 2


def test_flatten_results_sequential_indices():
    groups = [[_r(10, 0.1), _r(20, 0.2)], [_r(30, 0.3)]]
    results = flatten_results(groups)
    assert [r.flat_index for r in results] == [0, 1, 2]


def test_flatten_results_assigns_default_labels():
    groups = [[_r(10, 0.1)], [_r(20, 0.2)]]
    results = flatten_results(groups)
    assert results[0].source_label == "set_0"
    assert results[1].source_label == "set_1"


def test_flatten_results_uses_provided_labels():
    groups = [[_r(10, 0.1)], [_r(20, 0.2)]]
    cfg = FlattenConfig(labels=["alpha", "beta"])
    results = flatten_results(groups, cfg)
    assert results[0].source_label == "alpha"
    assert results[1].source_label == "beta"


def test_flatten_results_pads_missing_labels():
    groups = [[_r(10, 0.1)], [_r(20, 0.2)], [_r(30, 0.3)]]
    cfg = FlattenConfig(labels=["only_one"])
    results = flatten_results(groups, cfg)
    assert results[0].source_label == "only_one"
    assert results[1].source_label == "set_1"
    assert results[2].source_label == "set_2"


def test_flatten_results_excludes_failures_when_configured():
    group = [_r(10, 0.1, returncode=0), _r(20, 0.2, returncode=1)]
    cfg = FlattenConfig(include_failures=False)
    results = flatten_results([group], cfg)
    assert len(results) == 1
    assert results[0].success is True


def test_flatten_results_includes_failures_by_default():
    group = [_r(10, 0.1, returncode=0), _r(20, 0.2, returncode=1)]
    results = flatten_results([group])
    assert len(results) == 2


def test_flatten_results_sort_by_size():
    groups = [[_r(30, 0.3), _r(10, 0.1)], [_r(20, 0.2)]]
    cfg = FlattenConfig(sort_by_size=True)
    results = flatten_results(groups, cfg)
    assert [r.size for r in results] == [10, 20, 30]


def test_flatten_results_reindexes_after_sort():
    groups = [[_r(30, 0.3)], [_r(10, 0.1)]]
    cfg = FlattenConfig(sort_by_size=True)
    results = flatten_results(groups, cfg)
    assert [r.flat_index for r in results] == [0, 1]


def test_flatten_results_preserves_result_reference():
    original = _r(10, 0.1)
    results = flatten_results([[original]])
    assert results[0].result is original


def test_format_flatten_summary_counts():
    group = [_r(10, 0.1), _r(20, 0.2, returncode=1)]
    results = flatten_results([group], FlattenConfig(labels=["mygroup"]))
    summary = format_flatten_summary(results)
    assert "2" in summary
    assert "1" in summary
    assert "mygroup" in summary


def test_format_flatten_summary_no_failures():
    group = [_r(10, 0.1), _r(20, 0.2)]
    results = flatten_results([group])
    summary = format_flatten_summary(results)
    assert "0 failure" in summary
