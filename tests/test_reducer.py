"""Tests for batchmark.reducer."""

from __future__ import annotations

from typing import List

import pytest

from batchmark.timer import TimingResult
from batchmark.reducer import (
    AVAILABLE_STRATEGIES,
    ReducedResult,
    reduce_results,
    format_reduced_summary,
)


def _r(size: int, duration_ms: float, ok: bool = True) -> TimingResult:
    return TimingResult(
        size=size,
        command="echo test",
        returncode=0 if ok else 1,
        duration=duration_ms / 1000.0,
        stdout="",
        stderr="",
    )


def test_available_strategies_contains_expected():
    for s in ("mean", "median", "min", "max"):
        assert s in AVAILABLE_STRATEGIES


def test_reduce_results_returns_one_row_per_size():
    results = [_r(10, 100), _r(10, 200), _r(20, 300)]
    reduced = reduce_results(results)
    assert len(reduced) == 2
    assert {r.size for r in reduced} == {10, 20}


def test_reduce_results_sorted_by_size():
    results = [_r(30, 100), _r(10, 200), _r(20, 150)]
    reduced = reduce_results(results)
    assert [r.size for r in reduced] == [10, 20, 30]


def test_reduce_mean_strategy():
    results = [_r(10, 100), _r(10, 200)]
    reduced = reduce_results(results, strategy="mean")
    assert len(reduced) == 1
    assert reduced[0].duration == pytest.approx(0.150, rel=1e-6)


def test_reduce_min_strategy():
    results = [_r(10, 100), _r(10, 200), _r(10, 50)]
    reduced = reduce_results(results, strategy="min")
    assert reduced[0].duration == pytest.approx(0.050, rel=1e-6)


def test_reduce_max_strategy():
    results = [_r(10, 100), _r(10, 200), _r(10, 50)]
    reduced = reduce_results(results, strategy="max")
    assert reduced[0].duration == pytest.approx(0.200, rel=1e-6)


def test_reduce_median_strategy_odd():
    results = [_r(10, 100), _r(10, 300), _r(10, 200)]
    reduced = reduce_results(results, strategy="median")
    assert reduced[0].duration == pytest.approx(0.200, rel=1e-6)


def test_reduce_counts_runs():
    results = [_r(10, 100), _r(10, 200), _r(10, 150, ok=False)]
    reduced = reduce_results(results)
    assert reduced[0].total_runs == 3
    assert reduced[0].successful_runs == 2


def test_reduce_all_failed_returns_none_duration():
    results = [_r(10, 100, ok=False), _r(10, 200, ok=False)]
    reduced = reduce_results(results)
    assert reduced[0].duration is None
    assert not reduced[0].success


def test_reduce_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        reduce_results([_r(10, 100)], strategy="geometric")  # type: ignore


def test_reduce_empty_input_returns_empty():
    assert reduce_results([]) == []


def test_format_reduced_summary_contains_strategy():
    results = [_r(10, 100), _r(20, 200)]
    reduced = reduce_results(results, strategy="min")
    summary = format_reduced_summary(reduced)
    assert "min" in summary


def test_format_reduced_summary_empty():
    assert format_reduced_summary([]) == "No reduced results."
