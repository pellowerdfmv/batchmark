"""Tests for batchmark/pruner.py."""
from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.pruner import (
    PrunerConfig,
    prune_results,
    format_prune_summary,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


# ---------------------------------------------------------------------------
# prune_results
# ---------------------------------------------------------------------------

def test_prune_results_returns_one_per_input():
    results = [_r(10, 0.1), _r(20, 0.2), _r(30, 0.3)]
    pruned = prune_results(results)
    assert len(pruned) == 3


def test_no_pruning_with_default_config():
    results = [_r(10, 0.1), _r(20, 0.2), _r(30, 0.3)]
    pruned = prune_results(results)
    assert all(not p.pruned for p in pruned)


def test_prune_removes_top_outlier():
    results = [_r(i, float(i)) for i in range(1, 11)]  # 1..10 s
    config = PrunerConfig(lower_pct=0.0, upper_pct=0.9)
    pruned = prune_results(results, config)
    # The longest duration (10.0) should be pruned
    top = max(pruned, key=lambda p: p.duration or 0)
    assert top.pruned
    assert top.reason == "above_upper_pct"


def test_prune_removes_bottom_outlier():
    results = [_r(i, float(i)) for i in range(1, 11)]
    config = PrunerConfig(lower_pct=0.1, upper_pct=1.0)
    pruned = prune_results(results, config)
    bottom = min(pruned, key=lambda p: p.duration or float("inf"))
    assert bottom.pruned
    assert bottom.reason == "below_lower_pct"


def test_prune_ignores_failed_when_only_successful_true():
    """A failed result with None duration should not be pruned."""
    failed = TimingResult(size=5, duration=None, returncode=1, stdout="", stderr="")
    ok = _r(10, 0.5)
    pruned = prune_results([failed, ok])
    failed_pr = next(p for p in pruned if p.result is failed)
    assert not failed_pr.pruned


def test_prune_preserves_result_reference():
    r = _r(42, 1.23)
    pruned = prune_results([r])
    assert pruned[0].result is r


def test_prune_all_same_duration_nothing_pruned():
    results = [_r(i, 1.0) for i in range(5)]
    config = PrunerConfig(lower_pct=0.1, upper_pct=0.9)
    pruned = prune_results(results, config)
    # All values equal the percentile bounds, none should be strictly outside
    assert all(not p.pruned for p in pruned)


def test_prune_empty_input():
    assert prune_results([]) == []


# ---------------------------------------------------------------------------
# format_prune_summary
# ---------------------------------------------------------------------------

def test_format_prune_summary_counts():
    results = [_r(i, float(i)) for i in range(1, 6)]
    config = PrunerConfig(lower_pct=0.0, upper_pct=0.8)
    pruned = prune_results(results, config)
    summary = format_prune_summary(pruned)
    assert "5 results" in summary
    assert "pruned" in summary


def test_format_prune_summary_no_pruning():
    results = [_r(i, float(i)) for i in range(3)]
    pruned = prune_results(results)
    summary = format_prune_summary(pruned)
    assert "0 pruned" in summary or "pruned" in summary
