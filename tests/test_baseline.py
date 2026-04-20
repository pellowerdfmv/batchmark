"""Tests for batchmark.baseline and batchmark.baseline_reporter."""

from __future__ import annotations

import os
import tempfile

import pytest

from batchmark.baseline import (
    BaselineEntry,
    baseline_from_results,
    load_baseline,
    lookup_baseline,
    save_baseline,
)
from batchmark.baseline_reporter import (
    format_baseline_header,
    format_baseline_row,
    format_baseline_summary,
)
from batchmark.timer import TimingResult


def _r(size: int, duration_ms: float, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration_ms=duration_ms, returncode=returncode, stdout="", stderr="")


# --- baseline_from_results ---

def test_baseline_from_results_basic():
    results = [_r(100, 10.0), _r(100, 20.0), _r(200, 30.0)]
    entries = baseline_from_results(results)
    assert len(entries) == 2
    assert entries[0].size == 100
    assert entries[0].mean_ms == pytest.approx(15.0)
    assert entries[0].runs == 2


def test_baseline_from_results_ignores_failures():
    results = [_r(100, 10.0), _r(100, 50.0, returncode=1)]
    entries = baseline_from_results(results)
    assert entries[0].mean_ms == pytest.approx(10.0)
    assert entries[0].runs == 1


def test_baseline_from_results_empty():
    assert baseline_from_results([]) == []


# --- save / load ---

def test_save_and_load_roundtrip():
    entries = [BaselineEntry(size=100, mean_ms=12.5, runs=3),
               BaselineEntry(size=200, mean_ms=25.0, runs=5)]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
        path = f.name
    try:
        save_baseline(entries, path)
        loaded = load_baseline(path)
        assert len(loaded) == 2
        assert loaded[0].size == 100
        assert loaded[0].mean_ms == pytest.approx(12.5)
        assert loaded[1].runs == 5
    finally:
        os.unlink(path)


def test_load_baseline_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_baseline("/nonexistent/path/baseline.csv")


# --- lookup_baseline ---

def test_lookup_baseline_found():
    entries = [BaselineEntry(100, 10.0, 2), BaselineEntry(200, 20.0, 2)]
    result = lookup_baseline(entries, 200)
    assert result is not None
    assert result.mean_ms == pytest.approx(20.0)


def test_lookup_baseline_not_found():
    entries = [BaselineEntry(100, 10.0, 2)]
    assert lookup_baseline(entries, 999) is None


# --- reporter ---

def test_format_baseline_header_contains_columns():
    header = format_baseline_header()
    assert "SIZE" in header
    assert "CURRENT" in header
    assert "BASELINE" in header
    assert "DELTA" in header


def test_format_baseline_row_with_baseline():
    ref = BaselineEntry(size=100, mean_ms=10.0, runs=3)
    row = format_baseline_row(100, 12.0, ref)
    assert "12.00" in row
    assert "10.00" in row
    assert "+2.0" in row


def test_format_baseline_row_no_baseline():
    row = format_baseline_row(100, 12.0, None)
    assert "n/a" in row


def test_format_baseline_summary_counts():
    current = [BaselineEntry(100, 5.0, 2), BaselineEntry(200, 30.0, 2)]
    baseline = [BaselineEntry(100, 10.0, 2), BaselineEntry(200, 10.0, 2)]
    summary = format_baseline_summary(current, baseline)
    assert "faster=1" in summary
    assert "slower=1" in summary
