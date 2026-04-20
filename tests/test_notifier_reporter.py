"""Tests for batchmark.notifier_reporter."""

import io
from contextlib import redirect_stdout

from batchmark.notifier import Notification
from batchmark.notifier_reporter import (
    format_notification,
    format_notification_summary,
    print_notification_report,
)


def _n(level: str, size: int = 10, msg: str = "test message") -> Notification:
    return Notification(level=level, size=size, message=msg)


def test_format_notification_warn_contains_label():
    line = format_notification(_n("warn"))
    assert "WARN" in line


def test_format_notification_fail_contains_label():
    line = format_notification(_n("fail"))
    assert "FAIL" in line


def test_format_notification_contains_message():
    line = format_notification(_n("warn", msg="something slow"))
    assert "something slow" in line


def test_format_summary_no_notifications():
    summary = format_notification_summary([])
    assert "none" in summary.lower()


def test_format_summary_counts_warns_and_fails():
    notes = [_n("warn"), _n("fail"), _n("fail")]
    summary = format_notification_summary(notes)
    assert "2 fail" in summary
    assert "1 warn" in summary


def test_format_summary_only_fails():
    notes = [_n("fail"), _n("fail")]
    summary = format_notification_summary(notes)
    assert "fail" in summary
    assert "warn" not in summary


def test_print_notification_report_prints_lines(capsys):
    notes = [_n("warn", msg="size=10: mean 600.0 ms exceeds warn threshold 500.0 ms")]
    print_notification_report(notes)
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "600" in captured.out


def test_print_notification_report_empty_no_output_by_default(capsys):
    print_notification_report([])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_print_notification_report_empty_verbose(capsys):
    print_notification_report([], verbose=True)
    captured = capsys.readouterr()
    assert "No threshold" in captured.out
