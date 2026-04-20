"""Tests for batchmark.formatter."""

from __future__ import annotations

import json
from typing import Optional

import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.formatter import (
    AVAILABLE_FORMATS,
    format_csv,
    format_json,
    format_output,
    format_table,
)


def _agg(
    size: int = 100,
    total: int = 5,
    ok: int = 5,
    mean: Optional[float] = 0.123,
    median: Optional[float] = 0.120,
    stdev: Optional[float] = 0.005,
    mn: Optional[float] = 0.110,
    mx: Optional[float] = 0.135,
) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        total_runs=total,
        successful_runs=ok,
        mean=mean,
        median=median,
        stdev=stdev,
        min_duration=mn,
        max_duration=mx,
    )


def test_available_formats_contains_expected():
    assert "table" in AVAILABLE_FORMATS
    assert "json" in AVAILABLE_FORMATS
    assert "csv" in AVAILABLE_FORMATS


def test_format_table_has_header():
    output = format_table([_agg()])
    assert "Size" in output
    assert "Mean" in output
    assert "Median" in output


def test_format_table_contains_size():
    output = format_table([_agg(size=256)])
    assert "256" in output


def test_format_table_none_shows_na():
    output = format_table([_agg(mean=None, stdev=None)])
    assert "N/A" in output


def test_format_json_is_valid_json():
    output = format_json([_agg(size=64)])
    data = json.loads(output)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["size"] == 64


def test_format_json_multiple_rows():
    output = format_json([_agg(size=10), _agg(size=20)])
    data = json.loads(output)
    assert len(data) == 2
    sizes = {row["size"] for row in data}
    assert sizes == {10, 20}


def test_format_csv_header():
    output = format_csv([_agg()])
    first_line = output.splitlines()[0]
    assert "size" in first_line
    assert "mean_s" in first_line


def test_format_csv_row_count():
    output = format_csv([_agg(size=1), _agg(size=2), _agg(size=3)])
    lines = output.splitlines()
    assert len(lines) == 4  # header + 3 rows


def test_format_output_dispatches_table():
    result = format_output([_agg()], "table")
    assert "Size" in result


def test_format_output_dispatches_json():
    result = format_output([_agg()], "json")
    json.loads(result)  # must not raise


def test_format_output_dispatches_csv():
    result = format_output([_agg()], "csv")
    assert result.startswith("size,")


def test_format_output_unknown_raises():
    with pytest.raises(ValueError, match="Unknown format"):
        format_output([_agg()], "xml")  # type: ignore[arg-type]
