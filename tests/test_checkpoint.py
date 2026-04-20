"""Tests for batchmark.checkpoint."""

import json
import os
import tempfile

import pytest

from batchmark.checkpoint import (
    CheckpointEntry,
    already_run,
    append_entry,
    load_checkpoint,
    results_from_checkpoint,
    save_checkpoint,
)
from batchmark.timer import TimingResult


def _result(duration=0.5, returncode=0, stdout="", stderr=""):
    return TimingResult(duration=duration, returncode=returncode, stdout=stdout, stderr=stderr)


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "cp.json")
    entries = [
        CheckpointEntry(size=100, run_index=0, duration=0.1, returncode=0, stdout="", stderr=""),
        CheckpointEntry(size=200, run_index=0, duration=0.2, returncode=1, stdout="", stderr="err"),
    ]
    save_checkpoint(path, entries)
    loaded = load_checkpoint(path)
    assert len(loaded) == 2
    assert loaded[0].size == 100
    assert loaded[1].returncode == 1


def test_load_checkpoint_missing_file(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    result = load_checkpoint(path)
    assert result == []


def test_already_run_true():
    entries = [CheckpointEntry(size=50, run_index=2, duration=0.3, returncode=0, stdout="", stderr="")]
    assert already_run(entries, 50, 2) is True


def test_already_run_false():
    entries = [CheckpointEntry(size=50, run_index=2, duration=0.3, returncode=0, stdout="", stderr="")]
    assert already_run(entries, 50, 3) is False
    assert already_run(entries, 99, 2) is False


def test_results_from_checkpoint_ordered():
    entries = [
        CheckpointEntry(size=100, run_index=1, duration=0.2, returncode=0, stdout="", stderr=""),
        CheckpointEntry(size=100, run_index=0, duration=0.1, returncode=0, stdout="", stderr=""),
    ]
    results = results_from_checkpoint(entries, 100)
    assert len(results) == 2
    assert results[0].duration == pytest.approx(0.1)
    assert results[1].duration == pytest.approx(0.2)


def test_results_from_checkpoint_filters_by_size():
    entries = [
        CheckpointEntry(size=100, run_index=0, duration=0.1, returncode=0, stdout="", stderr=""),
        CheckpointEntry(size=200, run_index=0, duration=0.9, returncode=0, stdout="", stderr=""),
    ]
    results = results_from_checkpoint(entries, 100)
    assert len(results) == 1
    assert results[0].duration == pytest.approx(0.1)


def test_append_entry_persists(tmp_path):
    path = str(tmp_path / "cp.json")
    entries = []
    entries = append_entry(path, entries, 100, 0, _result(0.3))
    assert len(entries) == 1
    loaded = load_checkpoint(path)
    assert len(loaded) == 1
    assert loaded[0].size == 100
    assert loaded[0].run_index == 0
    assert loaded[0].duration == pytest.approx(0.3)
