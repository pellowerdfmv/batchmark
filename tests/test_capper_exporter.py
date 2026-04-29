"""Tests for batchmark.capper_exporter."""

from __future__ import annotations

import csv
import io
import os
import tempfile

import pytest

from batchmark.capper import CappedResult
from batchmark.timer import TimingResult
from batchmark.capper_exporter import capped_to_csv, capped_to_csv_file


def _r(
    size: int,
    duration: float,
    capped_duration: float,
    was_capped: bool,
    success: bool = True,
) -> CappedResult:
    inner = TimingResult(command="echo", size=size, duration=duration, returncode=0 if success else 1, stdout="", stderr="")
    return CappedResult(
        result=inner,
        capped_duration=capped_duration,
        was_capped=was_capped,
    )


def _parse(csv_text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def test_csv_has_expected_header():
    rows = _parse(capped_to_csv([]))
    assert rows == []
    # parse header separately
    header = capped_to_csv([]).splitlines()[0].split(",")
    assert "size" in header
    assert "was_capped" in header
    assert "capped_duration_ms" in header


def test_csv_row_count_matches_input():
    results = [
        _r(100, 0.1, 0.1, False),
        _r(200, 0.5, 0.2, True),
        _r(300, 0.05, 0.05, False),
    ]
    rows = _parse(capped_to_csv(results))
    assert len(rows) == 3


def test_csv_was_capped_true():
    r = _r(100, 0.5, 0.2, was_capped=True)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["was_capped"] == "True"


def test_csv_was_capped_false():
    r = _r(100, 0.1, 0.1, was_capped=False)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["was_capped"] == "False"


def test_csv_duration_ms_formatted():
    r = _r(100, 0.123456, 0.1, was_capped=True)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["duration_ms"] == "123.456"


def test_csv_capped_duration_ms_formatted():
    r = _r(100, 0.5, 0.2, was_capped=True)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["capped_duration_ms"] == "200.000"


def test_csv_size_field():
    r = _r(512, 0.1, 0.1, was_capped=False)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["size"] == "512"


def test_capped_to_csv_file_writes_file():
    results = [_r(10, 0.01, 0.01, False), _r(20, 0.5, 0.3, True)]
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "out.csv")
        capped_to_csv_file(results, path)
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        rows = _parse(content)
        assert len(rows) == 2
