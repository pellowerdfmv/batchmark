"""Tests for batchmark.exporter."""

import csv
import io
import tempfile
from pathlib import Path

import pytest
from batchmark.timer import TimingResult
from batchmark.exporter import results_to_csv, FIELDS


def _make_results():
    return [
        TimingResult(command="echo hi", input_size=10, elapsed_seconds=0.012, returncode=0),
        TimingResult(command="sleep 0", input_size=50, elapsed_seconds=0.003, returncode=0),
        TimingResult(command="exit 1", input_size=20, elapsed_seconds=0.001, returncode=1),
    ]


def test_csv_has_header():
    csv_str = results_to_csv(_make_results())
    reader = csv.DictReader(io.StringIO(csv_str))
    assert reader.fieldnames == FIELDS


def test_csv_row_count():
    results = _make_results()
    csv_str = results_to_csv(results)
    rows = list(csv.DictReader(io.StringIO(csv_str)))
    assert len(rows) == len(results)


def test_csv_values():
    results = _make_results()
    csv_str = results_to_csv(results)
    rows = list(csv.DictReader(io.StringIO(csv_str)))
    assert rows[0]["command"] == "echo hi"
    assert rows[2]["success"] == "False"


def test_csv_writes_to_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "results.csv"
        results_to_csv(_make_results(), dest=dest)
        assert dest.exists()
        content = dest.read_text()
        assert "command" in content
