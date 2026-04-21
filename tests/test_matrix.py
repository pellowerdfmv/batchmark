"""Tests for batchmark.matrix."""

import pytest
from unittest.mock import patch, call

from batchmark.matrix import (
    MatrixConfig,
    MatrixCell,
    _build_matrix_command,
    run_matrix,
)
from batchmark.timer import TimingResult


def _ok(duration=0.1):
    return TimingResult(duration=duration, returncode=0, stdout="", stderr="")


# ── _build_matrix_command ────────────────────────────────────────────────────

def test_build_matrix_command_substitutes_both():
    cmd = _build_matrix_command("run {size} {variant}", 10, "fast", "{size}", "{variant}")
    assert cmd == "run 10 fast"


def test_build_matrix_command_only_size():
    cmd = _build_matrix_command("run {size}", 42, "ignored", "{size}", "{variant}")
    assert cmd == "run 42"


def test_build_matrix_command_missing_placeholders_raises():
    with pytest.raises(ValueError):
        _build_matrix_command("echo hello", 1, "x", "{size}", "{variant}")


# ── run_matrix ───────────────────────────────────────────────────────────────

def test_run_matrix_returns_correct_cell_count():
    cfg = MatrixConfig(
        command_template="echo {size} {variant}",
        sizes=[10, 20],
        variants={"a": "alpha", "b": "beta"},
        runs=1,
    )
    with patch("batchmark.matrix.time_command", return_value=_ok()) as mock_tc:
        cells = run_matrix(cfg)
    # 2 sizes × 2 variants × 1 run = 4
    assert len(cells) == 4


def test_run_matrix_respects_runs():
    cfg = MatrixConfig(
        command_template="echo {size} {variant}",
        sizes=[5],
        variants={"v": "val"},
        runs=3,
    )
    with patch("batchmark.matrix.time_command", return_value=_ok()) as mock_tc:
        cells = run_matrix(cfg)
    assert len(cells) == 3


def test_run_matrix_cell_fields():
    cfg = MatrixConfig(
        command_template="echo {size} {variant}",
        sizes=[7],
        variants={"myvar": "val"},
        runs=1,
    )
    result = _ok(0.05)
    with patch("batchmark.matrix.time_command", return_value=result):
        cells = run_matrix(cfg)
    assert cells[0].size == 7
    assert cells[0].variant == "myvar"
    assert cells[0].result is result


def test_run_matrix_passes_timeout():
    cfg = MatrixConfig(
        command_template="echo {size} {variant}",
        sizes=[1],
        variants={"v": "x"},
        runs=1,
        timeout=5.0,
    )
    with patch("batchmark.matrix.time_command", return_value=_ok()) as mock_tc:
        run_matrix(cfg)
    mock_tc.assert_called_once()
    _, kwargs = mock_tc.call_args
    assert kwargs.get("timeout") == 5.0
