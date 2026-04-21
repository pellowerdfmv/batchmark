"""Tests for batchmark.deduplicator."""

import pytest
from batchmark.timer import TimingResult
from batchmark.deduplicator import (
    DeduplicatorConfig,
    deduplicate,
    format_dedup_summary,
)


def _r(size: int, run_index: int, duration: float = 1.0, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        run_index=run_index,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_deduplicate_no_duplicates_returns_all():
    results = [_r(10, 0), _r(10, 1), _r(20, 0)]
    out = deduplicate(results)
    assert len(out) == 3


def test_deduplicate_removes_exact_duplicates_keep_first():
    r1 = _r(10, 0, duration=2.0)
    r2 = _r(10, 0, duration=5.0)
    config = DeduplicatorConfig(keep="first")
    out = deduplicate([r1, r2], config)
    assert len(out) == 1
    assert out[0].duration == 2.0


def test_deduplicate_keep_last():
    r1 = _r(10, 0, duration=2.0)
    r2 = _r(10, 0, duration=5.0)
    config = DeduplicatorConfig(keep="last")
    out = deduplicate([r1, r2], config)
    assert len(out) == 1
    assert out[0].duration == 5.0


def test_deduplicate_keep_fastest_picks_min_duration():
    r1 = _r(10, 0, duration=3.0)
    r2 = _r(10, 0, duration=1.5)
    r3 = _r(10, 0, duration=4.0)
    config = DeduplicatorConfig(keep="fastest")
    out = deduplicate([r1, r2, r3], config)
    assert len(out) == 1
    assert out[0].duration == 1.5


def test_deduplicate_fastest_prefers_successful_over_failed():
    r1 = _r(10, 0, duration=0.5, returncode=1)  # fast but failed
    r2 = _r(10, 0, duration=2.0, returncode=0)  # slower but ok
    config = DeduplicatorConfig(keep="fastest")
    out = deduplicate([r1, r2], config)
    assert out[0].returncode == 0
    assert out[0].duration == 2.0


def test_deduplicate_preserves_order_of_first_occurrence():
    results = [_r(30, 0), _r(10, 0), _r(20, 0), _r(10, 0)]
    out = deduplicate(results)
    sizes = [r.size for r in out]
    assert sizes == [30, 10, 20]


def test_deduplicate_empty_input():
    assert deduplicate([]) == []


def test_deduplicate_default_config_is_first():
    r1 = _r(10, 0, duration=1.0)
    r2 = _r(10, 0, duration=9.0)
    out = deduplicate([r1, r2])
    assert out[0].duration == 1.0


def test_format_dedup_summary_shows_counts():
    summary = format_dedup_summary(before=10, after=7)
    assert "10" in summary
    assert "7" in summary
    assert "3" in summary


def test_format_dedup_summary_no_duplicates():
    summary = format_dedup_summary(before=5, after=5)
    assert "0" in summary
