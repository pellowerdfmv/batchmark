"""Tests for batchmark.snapshotter."""

import json
import os
import pytest

from batchmark.aggregator import AggregatedResult
from batchmark.snapshotter import (
    SnapshotEntry,
    snapshot_from_aggregated,
    save_snapshot,
    load_snapshot,
    lookup_snapshot,
)


def _agg(size: int, mean: float = 100.0) -> AggregatedResult:
    return AggregatedResult(
        size=size, runs=3, successful=3,
        mean=mean, median=mean, stdev=0.0,
        min_duration=mean, max_duration=mean,
    )


def test_snapshot_from_aggregated_returns_one_per_result():
    result = snapshot_from_aggregated([_agg(10), _agg(20)])
    assert len(result) == 2
    assert result[0].size == 10
    assert result[1].size == 20


def test_snapshot_from_aggregated_copies_mean():
    result = snapshot_from_aggregated([_agg(10, mean=42.5)])
    assert result[0].mean == pytest.approx(42.5)


def test_snapshot_from_aggregated_empty():
    assert snapshot_from_aggregated([]) == []


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "snap.json")
    entries = snapshot_from_aggregated([_agg(100, 200.0), _agg(200, 400.0)])
    save_snapshot(entries, path)
    loaded = load_snapshot(path)
    assert len(loaded) == 2
    assert loaded[0].size == 100
    assert loaded[0].mean == pytest.approx(200.0)
    assert loaded[1].size == 200


def test_load_snapshot_missing_file_returns_empty(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    assert load_snapshot(path) == []


def test_save_snapshot_writes_valid_json(tmp_path):
    path = str(tmp_path / "snap.json")
    entries = snapshot_from_aggregated([_agg(50)])
    save_snapshot(entries, path)
    with open(path) as fh:
        data = json.load(fh)
    assert isinstance(data, list)
    assert data[0]["size"] == 50


def test_lookup_snapshot_found():
    entries = snapshot_from_aggregated([_agg(10), _agg(20)])
    found = lookup_snapshot(entries, 20)
    assert found is not None
    assert found.size == 20


def test_lookup_snapshot_not_found():
    entries = snapshot_from_aggregated([_agg(10)])
    assert lookup_snapshot(entries, 99) is None
