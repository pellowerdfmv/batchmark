"""Tests for batchmark.merger."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.merger import (
    MergeConfig,
    MergedResult,
    merge_results,
    format_merge_summary,
)


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


# ---------------------------------------------------------------------------
# merge_results
# ---------------------------------------------------------------------------

def test_merge_returns_all_results_flat():
    batch_a = [_r(10), _r(20)]
    batch_b = [_r(30)]
    result = merge_results([batch_a, batch_b])
    assert len(result) == 3


def test_merge_assigns_default_labels():
    batch_a = [_r(10)]
    batch_b = [_r(20)]
    result = merge_results([batch_a, batch_b])
    labels = {m.label for m in result}
    assert "batch_0" in labels
    assert "batch_1" in labels


def test_merge_uses_provided_labels():
    config = MergeConfig(labels=["run_A", "run_B"])
    result = merge_results([[_r(10)], [_r(20)]], config=config)
    labels = {m.label for m in result}
    assert labels == {"run_A", "run_B"}


def test_merge_partial_labels_padded():
    config = MergeConfig(labels=["only_one"])
    result = merge_results([[_r(10)], [_r(20)]], config=config)
    labels = {m.label for m in result}
    assert "only_one" in labels
    assert "batch_1" in labels


def test_merge_empty_input_returns_empty():
    assert merge_results([]) == []


def test_merge_sorted_by_size_within_batch():
    batch = [_r(30), _r(10), _r(20)]
    result = merge_results([batch])
    sizes = [m.size for m in result]
    assert sizes == sorted(sizes)


def test_merge_intersect_sizes_keeps_common_only():
    batch_a = [_r(10), _r(20), _r(30)]
    batch_b = [_r(20), _r(30)]
    config = MergeConfig(intersect_sizes=True)
    result = merge_results([batch_a, batch_b], config=config)
    sizes = {m.size for m in result}
    assert sizes == {20, 30}


def test_merge_intersect_sizes_false_keeps_all():
    batch_a = [_r(10), _r(20)]
    batch_b = [_r(20), _r(30)]
    config = MergeConfig(intersect_sizes=False)
    result = merge_results([batch_a, batch_b], config=config)
    sizes = {m.size for m in result}
    assert sizes == {10, 20, 30}


def test_merged_result_proxy_properties():
    r = _r(size=42, duration=0.25, returncode=0)
    m = MergedResult(result=r, label="x")
    assert m.size == 42
    assert m.duration == 0.25
    assert m.success is True


def test_merged_result_failure_proxy():
    r = _r(size=5, returncode=1)
    m = MergedResult(result=r, label="y")
    assert m.success is False


# ---------------------------------------------------------------------------
# format_merge_summary
# ---------------------------------------------------------------------------

def test_format_merge_summary_empty():
    summary = format_merge_summary([])
    assert "No merged" in summary


def test_format_merge_summary_contains_label():
    config = MergeConfig(labels=["alpha"])
    merged = merge_results([[_r(10), _r(20)]], config=config)
    summary = format_merge_summary(merged)
    assert "alpha" in summary


def test_format_merge_summary_counts_results():
    merged = merge_results([[_r(10), _r(20), _r(30)]])
    summary = format_merge_summary(merged)
    assert "3" in summary
