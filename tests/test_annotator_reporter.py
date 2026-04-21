"""Tests for batchmark.annotator_reporter."""

import io
from unittest.mock import patch

from batchmark.annotator import AnnotatedResult
from batchmark.annotator_reporter import (
    format_annotated_header,
    format_annotated_row,
    format_annotated_summary,
    print_annotated_report,
)
from batchmark.timer import TimingResult


def _ar(
    size: int,
    duration: float = 0.1,
    returncode: int = 0,
    annotations: dict | None = None,
) -> AnnotatedResult:
    r = TimingResult(size=size, duration=duration, returncode=returncode, output="")
    return AnnotatedResult(result=r, annotations=annotations or {})


def test_format_annotated_header_contains_columns():
    header = format_annotated_header()
    assert "Size" in header
    assert "Duration" in header
    assert "Status" in header
    assert "Annotations" in header


def test_format_annotated_row_ok():
    row = format_annotated_row(_ar(100, duration=0.5, annotations={"env": "ci"}))
    assert "OK" in row
    assert "500.00" in row
    assert "env=ci" in row


def test_format_annotated_row_fail():
    row = format_annotated_row(_ar(200, returncode=1))
    assert "FAIL" in row


def test_format_annotated_row_no_annotations_shows_none():
    row = format_annotated_row(_ar(100))
    assert "(none)" in row


def test_format_annotated_summary_counts():
    results = [_ar(100), _ar(200, returncode=1), _ar(300)]
    summary = format_annotated_summary(results)
    assert "Total: 3" in summary
    assert "OK: 2" in summary
    assert "Failed: 1" in summary


def test_format_annotated_summary_lists_annotation_keys():
    results = [
        _ar(100, annotations={"env": "ci"}),
        _ar(200, annotations={"tier": "gold"}),
    ]
    summary = format_annotated_summary(results)
    assert "env" in summary
    assert "tier" in summary


def test_format_annotated_summary_no_keys():
    summary = format_annotated_summary([_ar(100)])
    assert "(none)" in summary


def test_print_annotated_report_outputs_header_and_rows(capsys):
    results = [_ar(100, annotations={"env": "ci"}), _ar(200, returncode=1)]
    print_annotated_report(results)
    captured = capsys.readouterr().out
    assert "Size" in captured
    assert "OK" in captured
    assert "FAIL" in captured
    assert "env=ci" in captured
