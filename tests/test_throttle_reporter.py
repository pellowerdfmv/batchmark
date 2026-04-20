"""Tests for batchmark.throttle_reporter."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

from batchmark.throttle import ThrottleConfig, ThrottleState
from batchmark.throttle_reporter import (
    format_throttle_header,
    format_throttle_row,
    print_throttle_report,
)


def test_format_throttle_header_contains_columns() -> None:
    header = format_throttle_header()
    assert "Delays Applied" in header
    assert "Delay Each" in header
    assert "Total Wait" in header


def test_format_throttle_row_shows_values() -> None:
    config = ThrottleConfig(delay_seconds=0.25)
    state = ThrottleState(delays_applied=4, total_delay_seconds=1.0)
    row = format_throttle_row(config, state)
    assert "4" in row
    assert "0.250" in row
    assert "1.000" in row


def test_format_throttle_row_disabled_shows_disabled() -> None:
    config = ThrottleConfig(delay_seconds=1.0, enabled=False)
    state = ThrottleState()
    row = format_throttle_row(config, state)
    assert "disabled" in row


def test_print_throttle_report_no_delays(capsys) -> None:
    config = ThrottleConfig(delay_seconds=0.5)
    state = ThrottleState()
    print_throttle_report(config, state)
    captured = capsys.readouterr()
    assert "No throttle delays" in captured.out


def test_print_throttle_report_with_delays(capsys) -> None:
    config = ThrottleConfig(delay_seconds=0.1)
    state = ThrottleState(delays_applied=5, total_delay_seconds=0.5)
    print_throttle_report(config, state)
    captured = capsys.readouterr()
    assert "0.500" in captured.out
    assert "5" in captured.out
