"""Tests for batchmark.runner."""

import pytest

from batchmark.runner import build_command, run_batch
from batchmark.timer import TimingResult


# ---------------------------------------------------------------------------
# build_command
# ---------------------------------------------------------------------------

def test_build_command_substitutes_size():
    assert build_command("echo {size}", 42) == "echo 42"


def test_build_command_no_placeholder():
    """Commands without {size} are returned unchanged."""
    assert build_command("echo hello", 99) == "echo hello"


def test_build_command_unknown_placeholder_raises():
    with pytest.raises(KeyError):
        build_command("echo {unknown}", 1)


# ---------------------------------------------------------------------------
# run_batch
# ---------------------------------------------------------------------------

def test_run_batch_returns_timing_results():
    results = run_batch("echo {size}", sizes=[1, 2, 3])
    assert len(results) == 3
    assert all(isinstance(r, TimingResult) for r in results)


def test_run_batch_multiple_runs():
    results = run_batch("echo {size}", sizes=[10, 20], runs=3)
    # 2 sizes * 3 runs = 6 results
    assert len(results) == 6


def test_run_batch_sizes_reflected_in_commands():
    """Ensure each result carries the correct command string."""
    results = run_batch("echo {size}", sizes=[5, 10], runs=1)
    assert results[0].command == "echo 5"
    assert results[1].command == "echo 10"


def test_run_batch_successful_exit_codes():
    results = run_batch("true", sizes=[1, 2])
    assert all(r.returncode == 0 for r in results)


def test_run_batch_failed_exit_codes():
    results = run_batch("false", sizes=[1])
    assert results[0].returncode != 0


def test_run_batch_invalid_runs_raises():
    with pytest.raises(ValueError, match="runs must be >= 1"):
        run_batch("echo {size}", sizes=[1], runs=0)


def test_run_batch_empty_sizes_returns_empty():
    results = run_batch("echo {size}", sizes=[])
    assert results == []
