"""Tests for batchmark.budget."""

from __future__ import annotations

import pytest

from batchmark.budget import BudgetConfig, BudgetState, apply_budget
from batchmark.timer import TimingResult


def _r(duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(
        command="echo hi",
        size=1,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


# ---------------------------------------------------------------------------
# BudgetState
# ---------------------------------------------------------------------------

def test_budget_state_no_limit_never_exceeded():
    state = BudgetState(config=BudgetConfig(max_total_seconds=None))
    for _ in range(100):
        state.record(_r(1000.0))
    assert not state.is_exceeded()


def test_budget_state_remaining_none_when_no_limit():
    state = BudgetState(config=BudgetConfig(max_total_seconds=None))
    assert state.remaining() is None


def test_budget_state_tracks_elapsed():
    state = BudgetState(config=BudgetConfig(max_total_seconds=10.0))
    state.record(_r(3.0))
    state.record(_r(4.0))
    assert state.elapsed == pytest.approx(7.0)


def test_budget_state_exceeded_after_limit():
    state = BudgetState(config=BudgetConfig(max_total_seconds=5.0))
    state.record(_r(3.0))
    assert not state.is_exceeded()
    state.record(_r(3.0))
    assert state.is_exceeded()


def test_budget_state_remaining_decreases():
    state = BudgetState(config=BudgetConfig(max_total_seconds=10.0))
    state.record(_r(4.0))
    assert state.remaining() == pytest.approx(6.0)


def test_budget_state_remaining_floored_at_zero():
    state = BudgetState(config=BudgetConfig(max_total_seconds=2.0))
    state.record(_r(5.0))
    assert state.remaining() == pytest.approx(0.0)


def test_budget_state_ignores_failed_results():
    state = BudgetState(config=BudgetConfig(max_total_seconds=5.0))
    state.record(_r(-1.0, returncode=1))  # timeout / failure
    assert state.elapsed == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# apply_budget
# ---------------------------------------------------------------------------

def test_apply_budget_no_limit_returns_all():
    results = [_r(1.0), _r(2.0), _r(3.0)]
    assert apply_budget(results, BudgetConfig()) == results


def test_apply_budget_keeps_results_within_limit():
    results = [_r(1.0), _r(1.0), _r(1.0)]
    kept = apply_budget(results, BudgetConfig(max_total_seconds=2.5))
    assert len(kept) == 2


def test_apply_budget_includes_result_that_exceeds():
    # The result that pushes over the limit is still included.
    results = [_r(1.0), _r(1.0), _r(5.0), _r(1.0)]
    kept = apply_budget(results, BudgetConfig(max_total_seconds=4.0))
    assert len(kept) == 3
    assert kept[-1].duration == pytest.approx(5.0)


def test_apply_budget_empty_input():
    assert apply_budget([], BudgetConfig(max_total_seconds=10.0)) == []


def test_apply_budget_does_not_mutate_input():
    results = [_r(1.0), _r(1.0), _r(1.0)]
    original = list(results)
    apply_budget(results, BudgetConfig(max_total_seconds=1.5))
    assert results == original
