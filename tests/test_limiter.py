"""Tests for batchmark.limiter."""

from __future__ import annotations

from typing import List
from unittest.mock import MagicMock

import pytest

from batchmark.limiter import (
    LimiterConfig,
    _RateState,
    apply_delay,
    run_with_limit,
)
from batchmark.timer import TimingResult


def _r(size: int = 1, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


# ---------------------------------------------------------------------------
# _RateState
# ---------------------------------------------------------------------------

class TestRateState:
    def test_record_and_count(self):
        state = _RateState()
        state.record(0.0)
        state.record(30.0)
        assert state.count_in_window(60.0) == 2

    def test_old_timestamps_pruned(self):
        state = _RateState()
        state.record(0.0)   # older than 60 s from now=70
        state.record(20.0)  # also older
        state.record(50.0)  # within window
        assert state.count_in_window(70.0) == 1

    def test_empty_state_returns_zero(self):
        state = _RateState()
        assert state.count_in_window(100.0) == 0


# ---------------------------------------------------------------------------
# apply_delay
# ---------------------------------------------------------------------------

class TestApplyDelay:
    def test_fixed_delay_is_applied(self):
        slept: List[float] = []
        config = LimiterConfig(delay_seconds=0.5)
        state = _RateState()
        apply_delay(config, state, sleep_fn=slept.append, now_fn=lambda: 1.0, random_fn=lambda: 0.0)
        assert slept == [0.5]

    def test_no_delay_when_zero(self):
        slept: List[float] = []
        config = LimiterConfig(delay_seconds=0.0)
        state = _RateState()
        apply_delay(config, state, sleep_fn=slept.append, now_fn=lambda: 1.0, random_fn=lambda: 0.0)
        assert slept == [0.0]

    def test_jitter_added_to_delay(self):
        slept: List[float] = []
        config = LimiterConfig(delay_seconds=0.2, jitter_seconds=0.4)
        state = _RateState()
        # random_fn returns 0.5 → jitter = 0.5 * 0.4 = 0.2 → total = 0.4
        apply_delay(config, state, sleep_fn=slept.append, now_fn=lambda: 1.0, random_fn=lambda: 0.5)
        assert abs(slept[-1] - 0.4) < 1e-9

    def test_rate_limit_blocks_until_window_clears(self):
        slept: List[float] = []
        tick = [0.0]

        def now_fn() -> float:
            return tick[0]

        def sleep_fn(s: float) -> None:
            slept.append(s)
            tick[0] += s + 1.0  # advance simulated clock

        state = _RateState()
        # Fill the window: 2 runs already happened in the last 60 s
        state.record(0.0)
        state.record(5.0)
        tick[0] = 10.0

        config = LimiterConfig(max_runs_per_minute=2, delay_seconds=0.0)
        apply_delay(config, state, sleep_fn=sleep_fn, now_fn=now_fn, random_fn=lambda: 0.0)
        # At least one throttle sleep of 0.1 must have occurred
        assert any(s == pytest.approx(0.1) for s in slept)


# ---------------------------------------------------------------------------
# run_with_limit
# ---------------------------------------------------------------------------

class TestRunWithLimit:
    def test_returns_all_results(self):
        results = [_r(size=i) for i in range(5)]
        config = LimiterConfig(delay_seconds=0.0)
        out = run_with_limit(results, config, sleep_fn=lambda _: None, now_fn=lambda: 0.0)
        assert out == results

    def test_no_delay_before_first_run(self):
        slept: List[float] = []
        results = [_r()]
        config = LimiterConfig(delay_seconds=1.0)
        run_with_limit(results, config, sleep_fn=slept.append, now_fn=lambda: 0.0)
        assert slept == []  # first run: no sleep called

    def test_delay_applied_between_runs(self):
        slept: List[float] = []
        results = [_r(size=i) for i in range(3)]
        config = LimiterConfig(delay_seconds=0.25)
        run_with_limit(results, config, sleep_fn=slept.append, now_fn=lambda: 0.0)
        # delay applied before run 1 and run 2 (not before run 0)
        assert len([s for s in slept if s == pytest.approx(0.25)]) == 2

    def test_empty_results_returns_empty(self):
        config = LimiterConfig()
        out = run_with_limit([], config, sleep_fn=lambda _: None, now_fn=lambda: 0.0)
        assert out == []
