"""Tests for batchmark.profiler and batchmark.profile_reporter."""

from __future__ import annotations

import pytest

from batchmark.profiler import ProfiledResult, profile_command
from batchmark.profile_reporter import (
    format_profile_header,
    format_profile_row,
    format_profile_summary,
)
from batchmark.timer import TimingResult


def _make_profiled(cmd="echo hi", size=10, duration=0.1, returncode=0,
                   max_rss_kb=1024, user_time_s=0.05, sys_time_s=0.01):
    timing = TimingResult(
        command=cmd, size=size, duration=duration,
        returncode=returncode, stdout=b"", stderr=b""
    )
    return ProfiledResult(
        timing=timing,
        max_rss_kb=max_rss_kb,
        user_time_s=user_time_s,
        sys_time_s=sys_time_s,
    )


def test_profile_command_success():
    result = profile_command("echo hello", capture_output=True)
    assert result.timing.returncode == 0
    assert result.timing.duration >= 0
    assert result.success is True


def test_profile_command_failure():
    result = profile_command("exit 1", capture_output=True)
    assert result.timing.returncode != 0
    assert result.success is False


def test_profile_command_timeout():
    result = profile_command("sleep 10", timeout=0.1)
    assert result.timing.returncode == -1
    assert result.success is False


def test_profiled_result_success_flag():
    ok = _make_profiled(returncode=0)
    fail = _make_profiled(returncode=1)
    assert ok.success is True
    assert fail.success is False


def test_format_profile_header_contains_columns():
    header = format_profile_header()
    for col in ["command", "size", "duration_s", "max_rss_kb", "user_s", "sys_s", "status"]:
        assert col in header


def test_format_profile_row_ok():
    row = format_profile_row(_make_profiled(returncode=0))
    assert "OK" in row
    assert "0.1000" in row


def test_format_profile_row_fail():
    row = format_profile_row(_make_profiled(returncode=2))
    assert "FAIL" in row


def test_format_profile_summary_counts():
    results = [_make_profiled(returncode=0), _make_profiled(returncode=1)]
    summary = format_profile_summary(results)
    assert "Runs: 2" in summary
    assert "OK: 1" in summary
    assert "FAIL: 1" in summary


def test_format_profile_summary_empty():
    assert "No profiled" in format_profile_summary([])
