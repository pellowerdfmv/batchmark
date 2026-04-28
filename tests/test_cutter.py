"""Tests for batchmark.cutter."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.cutter import CutConfig, Chunk, cut_results, format_cut_summary


def _r(size: int, ok: bool = True) -> TimingResult:
    return TimingResult(
        command=f"echo {size}",
        size=size,
        duration=0.1,
        returncode=0 if ok else 1,
        stdout="",
        stderr="",
    )


# ---------------------------------------------------------------------------
# CutConfig validation
# ---------------------------------------------------------------------------

def test_cut_config_default_chunk_size():
    cfg = CutConfig()
    assert cfg.chunk_size == 10


def test_cut_config_invalid_chunk_size_raises():
    with pytest.raises(ValueError):
        CutConfig(chunk_size=0)


# ---------------------------------------------------------------------------
# cut_results – basic behaviour
# ---------------------------------------------------------------------------

def test_cut_results_empty_input_returns_no_chunks():
    assert cut_results([]) == []


def test_cut_results_returns_correct_number_of_chunks():
    results = [_r(i) for i in range(10)]
    chunks = cut_results(results, CutConfig(chunk_size=3))
    # 3 full chunks of 3, 1 remainder chunk of 1
    assert len(chunks) == 4


def test_cut_results_chunk_size_equals_total_gives_one_chunk():
    results = [_r(i) for i in range(5)]
    chunks = cut_results(results, CutConfig(chunk_size=5))
    assert len(chunks) == 1
    assert chunks[0].size == 5


def test_cut_results_indices_are_sequential():
    results = [_r(i) for i in range(7)]
    chunks = cut_results(results, CutConfig(chunk_size=3))
    assert [c.index for c in chunks] == list(range(len(chunks)))


def test_cut_results_drop_remainder_omits_partial_chunk():
    results = [_r(i) for i in range(7)]
    chunks = cut_results(results, CutConfig(chunk_size=3, drop_remainder=True))
    assert len(chunks) == 2
    assert all(c.size == 3 for c in chunks)


def test_cut_results_no_remainder_no_extra_chunk():
    results = [_r(i) for i in range(6)]
    chunks = cut_results(results, CutConfig(chunk_size=3))
    assert len(chunks) == 2


# ---------------------------------------------------------------------------
# Chunk properties
# ---------------------------------------------------------------------------

def test_chunk_successful_counts_ok_results():
    results = [_r(1, ok=True), _r(2, ok=False), _r(3, ok=True)]
    chunk = Chunk(index=0, results=results)
    assert chunk.successful == 2
    assert chunk.failed == 1


# ---------------------------------------------------------------------------
# format_cut_summary
# ---------------------------------------------------------------------------

def test_format_cut_summary_contains_chunk_count():
    results = [_r(i) for i in range(5)]
    chunks = cut_results(results, CutConfig(chunk_size=2))
    summary = format_cut_summary(chunks)
    assert "chunk" in summary


def test_format_cut_summary_contains_result_count():
    results = [_r(i) for i in range(4)]
    chunks = cut_results(results, CutConfig(chunk_size=4))
    summary = format_cut_summary(chunks)
    assert "4" in summary
