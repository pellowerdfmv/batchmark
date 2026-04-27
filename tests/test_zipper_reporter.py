"""Tests for batchmark.zipper_reporter and zipper_exporter."""

from __future__ import annotations

import io
import sys

from batchmark.timer import TimingResult
from batchmark.zipper import ZipConfig, zip_results
from batchmark.zipper_exporter import zipped_to_csv
from batchmark.zipper_reporter import (
    format_zip_header,
    format_zip_row,
    print_zip_report,
)


def _r(size: int, duration: float, ok: bool = True) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=0 if ok else 1,
        stdout="",
        stderr="",
    )


def test_format_zip_header_contains_columns():
    cfg = ZipConfig(left_label="run1", right_label="run2")
    header = format_zip_header(cfg)
    assert "size" in header
    assert "run1" in header
    assert "run2" in header
    assert "delta" in header


def test_format_zip_row_shows_duration():
    pairs = zip_results([_r(10, 0.123)], [_r(10, 0.456)])
    row = format_zip_row(pairs[0])
    assert "123.00 ms" in row
    assert "456.00 ms" in row


def test_format_zip_row_shows_na_for_missing():
    pairs = zip_results([_r(10, 0.1), _r(10, 0.2)], [_r(10, 0.3)])
    row = format_zip_row(pairs[1])
    assert "N/A" in row


def test_format_zip_row_shows_delta():
    pairs = zip_results([_r(10, 0.1)], [_r(10, 0.2)])
    row = format_zip_row(pairs[0])
    assert "+100.00 ms" in row


def test_print_zip_report_outputs_header(capsys):
    pairs = zip_results([_r(10, 0.1)], [_r(10, 0.2)])
    print_zip_report(pairs)
    captured = capsys.readouterr()
    assert "size" in captured.out
    assert "delta" in captured.out


def test_zipped_to_csv_has_header():
    pairs = zip_results([_r(10, 0.1)], [_r(10, 0.2)])
    csv_text = zipped_to_csv(pairs)
    first_line = csv_text.splitlines()[0]
    assert "size" in first_line
    assert "delta" in first_line


def test_zipped_to_csv_row_count():
    left = [_r(10, 0.1), _r(20, 0.2)]
    right = [_r(10, 0.15), _r(20, 0.25)]
    pairs = zip_results(left, right)
    lines = [l for l in zipped_to_csv(pairs).splitlines() if l.strip()]
    assert len(lines) == 3  # header + 2 data rows


def test_zipped_to_csv_custom_labels():
    pairs = zip_results([_r(10, 0.1)], [_r(10, 0.2)])
    cfg = ZipConfig(left_label="alpha", right_label="beta")
    csv_text = zipped_to_csv(pairs, cfg)
    assert "alpha" in csv_text
    assert "beta" in csv_text
