"""Tests for batchmark.throttle."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from batchmark.throttle import (
    ThrottleConfig,
    ThrottleState,
    apply_delay,
    format_throttle_summary,
    throttle_results,
)
from batchmark.timer import TimingResult


def _r(size: int = 10, duration: float = 0.1, rc: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=rc, stdout="", stderr="")


def test_apply_delay_calls_sleep() -> None:
    config = ThrottleConfig(delay_seconds=0.5)
    state = ThrottleState()
    sleep = MagicMock()
    apply_delay(config, state, _sleep=sleep)
    sleep.assert_called_once_with(0.5)


def test_apply_delay_updates_state() -> None:
    config = ThrottleConfig(delay_seconds=0.25)
    state = ThrottleState()
    apply_delay(config, state, _sleep=lambda _: None)
    assert state.delays_applied == 1
    assert state.total_delay_seconds == pytest.approx(0.25)


def test_apply_delay_skips_when_disabled() -> None:
    config = ThrottleConfig(delay_seconds=1.0, enabled=False)
    state = ThrottleState()
    sleep = MagicMock()
    apply_delay(config, state, _sleep=sleep)
    sleep.assert_not_called()
    assert state.delays_applied == 0


def test_apply_delay_skips_when_zero_delay() -> None:
    config = ThrottleConfig(delay_seconds=0.0)
    state = ThrottleState()
    sleep = MagicMock()
    apply_delay(config, state, _sleep=sleep)
    sleep.assert_not_called()


def test_throttle_results_applies_delay_between_items() -> None:
    results = [_r(10), _r(20), _r(30)]
    config = ThrottleConfig(delay_seconds=0.1)
    state = ThrottleState()
    sleep = MagicMock()
    out = throttle_results(results, config, state, _sleep=sleep)
    assert out is results
    assert sleep.call_count == 2  # between 3 items => 2 gaps


def test_throttle_results_single_item_no_delay() -> None:
    results = [_r(10)]
    config = ThrottleConfig(delay_seconds=0.5)
    state = ThrottleState()
    sleep = MagicMock()
    throttle_results(results, config, state, _sleep=sleep)
    sleep.assert_not_called()


def test_throttle_results_empty_list() -> None:
    config = ThrottleConfig(delay_seconds=0.5)
    state = ThrottleState()
    sleep = MagicMock()
    out = throttle_results([], config, state, _sleep=sleep)
    assert out == []
    sleep.assert_not_called()


def test_format_throttle_summary_no_delays() -> None:
    state = ThrottleState()
    summary = format_throttle_summary(state)
    assert "no delays" in summary.lower()


def test_format_throttle_summary_with_delays() -> None:
    state = ThrottleState(delays_applied=3, total_delay_seconds=1.5)
    summary = format_throttle_summary(state)
    assert "3" in summary
    assert "1.500" in summary
