"""Tests for batchmark.warmup."""

from unittest.mock import MagicMock, patch

import pytest

from batchmark.timer import TimingResult
from batchmark.warmup import WarmupConfig, all_warmups_succeeded, run_warmup


def _make_result(success: bool, duration: float = 0.01) -> TimingResult:
    return TimingResult(
        command="echo hi",
        size=10,
        duration=duration,
        returncode=0 if success else 1,
        stdout="",
        stderr="",
    )


def _patched_time_command(results):
    """Return a side_effect list for time_command mock."""
    return results


@patch("batchmark.warmup.time_command")
def test_run_warmup_calls_time_command_n_times(mock_tc):
    mock_tc.return_value = _make_result(True)
    run_warmup("echo hi", size=10, config=WarmupConfig(runs=3))
    assert mock_tc.call_count == 3


@patch("batchmark.warmup.time_command")
def test_run_warmup_zero_runs(mock_tc):
    results = run_warmup("echo hi", size=10, config=WarmupConfig(runs=0))
    assert results == []
    mock_tc.assert_not_called()


@patch("batchmark.warmup.time_command")
def test_run_warmup_returns_timing_results(mock_tc):
    mock_tc.return_value = _make_result(True)
    results = run_warmup("echo hi", size=5, config=WarmupConfig(runs=2))
    assert len(results) == 2
    assert all(isinstance(r, TimingResult) for r in results)


def test_run_warmup_negative_runs_raises():
    with pytest.raises(ValueError, match=">= 0"):
        run_warmup("echo hi", size=10, config=WarmupConfig(runs=-1))


@patch("batchmark.warmup.time_command")
def test_run_warmup_passes_timeout(mock_tc):
    mock_tc.return_value = _make_result(True)
    run_warmup("echo hi", size=10, config=WarmupConfig(runs=1), timeout=5.0)
    _, kwargs = mock_tc.call_args
    assert kwargs.get("timeout") == 5.0 or mock_tc.call_args[0][-1] == 5.0


def test_all_warmups_succeeded_true():
    results = [_make_result(True), _make_result(True)]
    assert all_warmups_succeeded(results) is True


def test_all_warmups_succeeded_false():
    results = [_make_result(True), _make_result(False)]
    assert all_warmups_succeeded(results) is False


def test_all_warmups_succeeded_empty():
    assert all_warmups_succeeded([]) is True
