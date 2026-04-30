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


def _r(size: int, duration: float, success: bool = True,
       was_capped: bool = False, cap_limit_ms: float = None) -> CappedResult:
    tr = TimingResult(returncode=0 if success else 1, duration=duration, output="")
    return CappedResult(
        result=tr,
        size=size,
        was_capped=was_capped,
        cap_limit_ms=cap_limit_ms,
    )


def _parse(csv_text: str) -> List[dict]:
    reader = csv.DictReader(io.StringIO(csv_text))
    return list(reader)


def test_csv_has_expected_header():
    rows = _parse(capped_to_csv([]))
    assert rows == []
    # Check header by inspecting raw first line
    first_line = capped_to_csv([]).split("\n")[0]
    assert "size" in first_line
    assert "duration_ms" in first_line
    assert "was_capped" in first_line
    assert "cap_limit_ms" in first_line


def test_csv_row_count_matches_input():
    results = [_r(10, 1.5), _r(20, 2.5), _r(30, 3.5)]
    rows = _parse(capped_to_csv(results))
    assert len(rows) == 3


def test_csv_was_capped_true():
    r = _r(100, 5.0, was_capped=True, cap_limit_ms=4.0)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["was_capped"] == "1"


def test_csv_was_capped_false():
    r = _r(100, 3.0, was_capped=False, cap_limit_ms=4.0)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["was_capped"] == "0"


def test_csv_cap_limit_ms_present():
    r = _r(50, 2.0, was_capped=True, cap_limit_ms=1.5)
    rows = _parse(capped_to_csv([r]))
    assert float(rows[0]["cap_limit_ms"]) == pytest.approx(1.5, abs=1e-3)


def test_csv_cap_limit_ms_empty_when_none():
    r = _r(50, 2.0, was_capped=False, cap_limit_ms=None)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["cap_limit_ms"] == ""


def test_csv_failed_result_success_zero():
    r = _r(10, 0.5, success=False)
    rows = _parse(capped_to_csv([r]))
    assert rows[0]["success"] == "0"


def test_capped_to_csv_file_writes_correctly():
    results = [_r(10, 1.0), _r(20, 2.0)]
    with tempfile.NamedTemporaryFile(mode="r", suffix=".csv",
                                     delete=False) as fh:
        path = fh.name
    try:
        capped_to_csv_file(results, path)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        rows = _parse(content)
        assert len(rows) == 2
    finally:
        os.unlink(path)
