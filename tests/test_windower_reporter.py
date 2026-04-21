"""Tests for batchmark.windower_reporter."""

from batchmark.timer import TimingResult
from batchmark.windower import WindowConfig, compute_windows
from batchmark.windower_reporter import (
    format_window_header,
    format_window_row,
    format_window_summary,
    print_window_report,
)


def _r(size: int, duration: float, rc: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=rc, output="")


RESULTS = [_r(s, float(s * 10)) for s in [1, 2, 3, 4, 5]]


def _windows():
    return compute_windows(RESULTS, WindowConfig(size=3, step=1))


def test_format_window_header_contains_columns():
    header = format_window_header()
    for col in ["WIN", "SIZES", "COUNT", "OK", "MEAN", "STDEV", "MIN", "MAX"]:
        assert col in header


def test_format_window_row_contains_index():
    windows = _windows()
    row = format_window_row(windows[0])
    assert "0" in row


def test_format_window_row_contains_sizes():
    windows = _windows()
    row = format_window_row(windows[0])
    # first window covers sizes 1,2,3
    assert "1" in row and "2" in row and "3" in row


def test_format_window_row_shows_na_for_none_mean():
    from batchmark.windower import WindowResult
    w = WindowResult(
        window_index=0, sizes=[1], count=1, successful=0,
        mean_ms=None, stdev_ms=None, min_ms=None, max_ms=None,
    )
    row = format_window_row(w)
    assert "N/A" in row


def test_format_window_summary_no_windows():
    summary = format_window_summary([])
    assert "No windows" in summary


def test_format_window_summary_shows_window_count():
    windows = _windows()
    summary = format_window_summary(windows)
    assert str(len(windows)) in summary


def test_print_window_report_runs_without_error(capsys):
    windows = _windows()
    print_window_report(windows)
    captured = capsys.readouterr()
    assert "WIN" in captured.out
    assert "Windows:" in captured.out


def test_print_window_report_empty(capsys):
    print_window_report([])
    captured = capsys.readouterr()
    assert "No windows" in captured.out
