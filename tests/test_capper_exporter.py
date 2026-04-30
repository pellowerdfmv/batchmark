"""Tests for batchmark.capper_exporter."""

from __future__ import annotations

import csv
import io
import os
import tempfile
from typing import List

import pytest

from batchmark.capper import CappedResult
from batchmark.timer import TimingResult
from batchmark.capper_exporter import capped_to_csv, capped_to_csv_file


def _r(
    size: int,
    duration: float | None,
    success: bool,
    was_capped: bool,
    original_duration: float | None = None,
) -> CappedResult:
    tr = TimingResult(
        command="echo",
        size=size,
        duration=duration,
        returncode=0 if success else 1,
        stdout="",
        stderr="",
    )
    return CappedResult(
        result=tr,
        was_capped=was_capped,
        original_duration=original_duration if original_duration is not None else duration,
    )


def _parse(csv_text: str) -> List[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def test_csv_has_expected_header():
    rows = _parse(capped_to_csv([]))
    assert rows == []
    # Check header by parsing a single row
    text = capped_to_csv([_r(10, 1.5, True, False)])
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    assert "size" in header
    assert "duration_ms" in header
    assert "was_capped" in header
    assert "original_duration_ms" in header


def test_csv_row_count_matches_input():
    results = [_r(10, 1.0, True, False), _r(20, 2.0, True, True, 3.0), _r(30, None, False, False)]
    rows = _parse(capped_to_csv(results))
    assert len(rows) == 3


def test_csv_was_capped_true():
    rows = _parse(capped_to_csv([_r(10, 2.0, True, True, 5.0)]))
    assert rows[0]["was_capped"] == "1"


def test_csv_was_capped_false():
    rows = _parse(capped_to_csv([_r(10, 2.0, True, False)]))
    assert rows[0]["was_capped"] == "0"


def test_csv_original_duration_preserved():
    rows = _parse(capped_to_csv([_r(10, 2.0, True, True, 9.5)]))
    assert float(rows[0]["original_duration_ms"]) == pytest.approx(9.5, rel=1e-5)


def test_csv_empty_duration_for_failed():
    rows = _parse(capped_to_csv([_r(10, None, False, False, None)]))
    assert rows[0]["duration_ms"] == ""


def test_csv_size_field():
    rows = _parse(capped_to_csv([_r(512, 1.0, True, False)]))
    assert rows[0]["size"] == "512"


def test_capped_to_csv_file_roundtrip():
    results = [_r(10, 1.0, True, False), _r(20, 3.0, True, True, 7.0)]
    with tempfile.NamedTemporaryFile(mode="r", suffix=".csv", delete=False) as fh:
        path = fh.name
    try:
        capped_to_csv_file(results, path)
        with open(path) as fh:
            content = fh.read()
        rows = _parse(content)
        assert len(rows) == 2
        assert rows[1]["was_capped"] == "1"
    finally:
        os.unlink(path)
