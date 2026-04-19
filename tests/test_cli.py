"""Tests for the CLI module."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from batchmark.cli import parse_args, main
from batchmark.timer import TimingResult


def _make_result(size=10, run=1, elapsed=0.5, returncode=0):
    return TimingResult(size=size, run=run, elapsed=elapsed, returncode=returncode, stdout="", stderr="")


def test_parse_args_required_fields():
    args = parse_args(["echo {size}", "--sizes", "10", "20"])
    assert args.command == "echo {size}"
    assert args.sizes == [10, 20]


def test_parse_args_defaults():
    args = parse_args(["echo", "--sizes", "5"])
    assert args.runs == 3
    assert args.timeout is None
    assert args.output is None
    assert args.quiet is False


def test_parse_args_all_options():
    args = parse_args(["cmd", "--sizes", "1", "2", "--runs", "5", "--timeout", "10.0", "--output", "out.csv", "--quiet"])
    assert args.runs == 5
    assert args.timeout == 10.0
    assert args.output == Path("out.csv")
    assert args.quiet is True


def test_main_returns_zero_on_success():
    results = [_make_result(returncode=0)]
    with patch("batchmark.cli.run_batch", return_value=results):
        code = main(["echo {size}", "--sizes", "10", "--quiet"])
    assert code == 0


def test_main_returns_one_on_failure():
    results = [_make_result(returncode=1)]
    with patch("batchmark.cli.run_batch", return_value=results):
        code = main(["false", "--sizes", "10", "--quiet"])
    assert code == 1


def test_main_writes_csv_when_output_given(tmp_path):
    out = tmp_path / "results.csv"
    results = [_make_result()]
    with patch("batchmark.cli.run_batch", return_value=results):
        main(["echo {size}", "--sizes", "10", "--quiet", "--output", str(out)])
    assert out.exists()


def test_main_passes_runs_and_timeout():
    results = [_make_result()]
    with patch("batchmark.cli.run_batch", return_value=results) as mock_run:
        main(["echo", "--sizes", "5", "--runs", "7", "--timeout", "2.5", "--quiet"])
    mock_run.assert_called_once_with("echo", sizes=[5], runs=7, timeout=2.5)
