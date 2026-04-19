"""Tests for batchmark.timer."""

import pytest
from batchmark.timer import time_command, TimingResult


def test_successful_command_returns_zero_returncode():
    result = time_command("echo hello", input_size=10)
    assert result.returncode == 0
    assert result.success is True
    assert result.elapsed_seconds >= 0
    assert result.input_size == 10


def test_failed_command_returns_nonzero_returncode():
    result = time_command("exit 1", input_size=0)
    assert result.returncode != 0
    assert result.success is False


def test_capture_output():
    result = time_command("echo captured", input_size=5, capture_output=True)
    assert result.stdout is not None
    assert "captured" in result.stdout


def test_timeout_returns_negative_returncode():
    result = time_command("sleep 10", input_size=0, timeout=0.1)
    assert result.returncode == -1
    assert result.stderr == "TimeoutExpired"


def test_timing_result_fields():
    r = TimingResult(command="ls", input_size=100, elapsed_seconds=0.05, returncode=0)
    assert r.command == "ls"
    assert r.success is True
