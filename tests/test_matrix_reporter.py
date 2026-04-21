"""Tests for batchmark.matrix_reporter."""

from batchmark.matrix import MatrixCell
from batchmark.matrix_reporter import (
    format_matrix_table,
    format_matrix_summary,
)
from batchmark.timer import TimingResult


def _cell(size, variant, duration=0.1, returncode=0):
    r = TimingResult(duration=duration, returncode=returncode, stdout="", stderr="")
    return MatrixCell(size=size, variant=variant, result=r)


# ── format_matrix_table ──────────────────────────────────────────────────────

def test_format_matrix_table_contains_variant_names():
    cells = [_cell(10, "fast"), _cell(10, "slow")]
    table = format_matrix_table(cells)
    assert "fast" in table
    assert "slow" in table


def test_format_matrix_table_contains_size():
    cells = [_cell(100, "v1")]
    table = format_matrix_table(cells)
    assert "100" in table


def test_format_matrix_table_shows_na_for_all_failed():
    cells = [_cell(10, "v1", returncode=1)]
    table = format_matrix_table(cells)
    assert "N/A" in table


def test_format_matrix_table_shows_duration():
    cells = [_cell(10, "v1", duration=0.5)]
    table = format_matrix_table(cells)
    assert "500.0ms" in table


def test_format_matrix_table_multiple_sizes():
    cells = [
        _cell(10, "v1", duration=0.1),
        _cell(20, "v1", duration=0.2),
    ]
    table = format_matrix_table(cells)
    lines = [l for l in table.splitlines() if l.strip()]
    # header + separator + 2 size rows
    assert len(lines) >= 4


# ── format_matrix_summary ────────────────────────────────────────────────────

def test_format_matrix_summary_counts_total():
    cells = [_cell(1, "v"), _cell(2, "v"), _cell(3, "v", returncode=1)]
    summary = format_matrix_summary(cells)
    assert "3" in summary


def test_format_matrix_summary_counts_failures():
    cells = [_cell(1, "v", returncode=1), _cell(2, "v")]
    summary = format_matrix_summary(cells)
    assert "1 failed" in summary


def test_format_matrix_summary_all_ok():
    cells = [_cell(1, "v"), _cell(2, "v")]
    summary = format_matrix_summary(cells)
    assert "0 failed" in summary
