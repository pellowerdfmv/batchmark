"""Tests for batchmark.repeater."""

from unittest.mock import patch, call

from batchmark.timer import TimingResult
from batchmark.repeater import (
    RepeaterConfig,
    RepeatGroup,
    repeat_command,
    repeat_all,
    format_repeat_summary,
)


def _ok(duration: float = 0.1) -> TimingResult:
    return TimingResult(returncode=0, duration=duration, stdout="", stderr="")


def _fail(duration: float = 0.05) -> TimingResult:
    return TimingResult(returncode=1, duration=duration, stdout="", stderr="err")


def _patched(results):
    return patch("batchmark.repeater.time_command", side_effect=results)


# ---------------------------------------------------------------------------
# RepeatGroup properties
# ---------------------------------------------------------------------------

def test_repeat_group_counts():
    g = RepeatGroup(size=100, command="echo hi", results=[_ok(), _fail(), _ok()])
    assert g.total_runs == 3
    assert g.successful_runs == 2
    assert g.failed_runs == 1


def test_repeat_group_mean_duration_ignores_failures():
    g = RepeatGroup(size=100, command="echo hi", results=[_ok(0.2), _fail(0.05), _ok(0.4)])
    assert g.mean_duration == pytest_approx(0.3)


def test_repeat_group_mean_duration_all_failed():
    g = RepeatGroup(size=100, command="cmd", results=[_fail(), _fail()])
    assert g.mean_duration is None


def test_repeat_group_mean_duration_empty():
    g = RepeatGroup(size=50, command="cmd")
    assert g.mean_duration is None


# ---------------------------------------------------------------------------
# repeat_command
# ---------------------------------------------------------------------------

def test_repeat_command_runs_n_times():
    cfg = RepeaterConfig(repeats=4)
    with _patched([_ok()] * 4) as mock_tc:
        g = repeat_command("echo", 10, cfg)
    assert mock_tc.call_count == 4
    assert g.total_runs == 4


def test_repeat_command_stop_on_failure():
    cfg = RepeaterConfig(repeats=5, stop_on_failure=True)
    with _patched([_ok(), _fail(), _ok()]) as mock_tc:
        g = repeat_command("cmd", 10, cfg)
    # should stop after the first failure
    assert mock_tc.call_count == 2
    assert g.failed_runs == 1


def test_repeat_command_no_stop_on_failure_continues():
    cfg = RepeaterConfig(repeats=3, stop_on_failure=False)
    with _patched([_ok(), _fail(), _ok()]) as mock_tc:
        g = repeat_command("cmd", 10, cfg)
    assert mock_tc.call_count == 3


def test_repeat_command_passes_timeout():
    cfg = RepeaterConfig(repeats=1, timeout=2.5)
    with _patched([_ok()]) as mock_tc:
        repeat_command("cmd", 10, cfg)
    mock_tc.assert_called_once_with("cmd", timeout=2.5)


# ---------------------------------------------------------------------------
# repeat_all
# ---------------------------------------------------------------------------

def test_repeat_all_returns_one_group_per_pair():
    cfg = RepeaterConfig(repeats=2)
    pairs = [("cmd", 10), ("cmd", 20), ("cmd", 30)]
    with _patched([_ok()] * 6):
        groups = repeat_all(pairs, cfg)
    assert len(groups) == 3
    assert [g.size for g in groups] == [10, 20, 30]


# ---------------------------------------------------------------------------
# format_repeat_summary
# ---------------------------------------------------------------------------

def test_format_repeat_summary_contains_header():
    groups = [RepeatGroup(size=100, command="cmd", results=[_ok(0.1)])]
    out = format_repeat_summary(groups)
    assert "Size" in out
    assert "Mean" in out


def test_format_repeat_summary_shows_na_for_all_failed():
    groups = [RepeatGroup(size=50, command="cmd", results=[_fail()])]
    out = format_repeat_summary(groups)
    assert "N/A" in out


# ---------------------------------------------------------------------------
# import helper (pytest.approx alias)
# ---------------------------------------------------------------------------

import pytest
pytest_approx = pytest.approx
