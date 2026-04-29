"""Tests for batchmark.rotator."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.rotator import RotatedResult, RotatorConfig, rotate_results, format_rotate_summary


def _r(size: int = 100, duration: float = 0.5, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


# ---------------------------------------------------------------------------
# RotatorConfig
# ---------------------------------------------------------------------------

def test_rotator_config_default_slots():
    cfg = RotatorConfig()
    assert cfg.slots == ["run-1", "run-2", "run-3"]


def test_rotator_config_empty_slots_raises():
    with pytest.raises(ValueError):
        RotatorConfig(slots=[])


# ---------------------------------------------------------------------------
# rotate_results
# ---------------------------------------------------------------------------

def test_rotate_results_returns_one_per_input():
    results = [_r() for _ in range(5)]
    rotated = rotate_results(results)
    assert len(rotated) == 5


def test_rotate_results_empty_input():
    assert rotate_results([]) == []


def test_rotate_results_slot_cycles():
    cfg = RotatorConfig(slots=["a", "b", "c"])
    results = [_r() for _ in range(7)]
    rotated = rotate_results(results, cfg)
    slots = [r.slot for r in rotated]
    assert slots == ["a", "b", "c", "a", "b", "c", "a"]


def test_rotate_results_slot_index_correct():
    cfg = RotatorConfig(slots=["x", "y"])
    results = [_r() for _ in range(4)]
    rotated = rotate_results(results, cfg)
    assert [r.slot_index for r in rotated] == [0, 1, 0, 1]


def test_rotate_results_single_slot():
    cfg = RotatorConfig(slots=["only"])
    results = [_r() for _ in range(3)]
    rotated = rotate_results(results, cfg)
    assert all(r.slot == "only" for r in rotated)


def test_rotate_results_preserves_result_reference():
    r = _r(size=42)
    rotated = rotate_results([r])
    assert rotated[0].result is r


def test_rotate_results_size_and_duration_proxies():
    r = _r(size=256, duration=1.23)
    rotated = rotate_results([r])
    assert rotated[0].size == 256
    assert rotated[0].duration == pytest.approx(1.23)


def test_rotate_results_success_proxy_ok():
    assert rotate_results([_r(returncode=0)])[0].success is True


def test_rotate_results_success_proxy_fail():
    assert rotate_results([_r(returncode=1)])[0].success is False


# ---------------------------------------------------------------------------
# format_rotate_summary
# ---------------------------------------------------------------------------

def test_format_rotate_summary_empty():
    assert format_rotate_summary([]) == "No results to rotate."


def test_format_rotate_summary_contains_slot_names():
    cfg = RotatorConfig(slots=["alpha", "beta"])
    rotated = rotate_results([_r() for _ in range(4)], cfg)
    summary = format_rotate_summary(rotated)
    assert "alpha" in summary
    assert "beta" in summary


def test_format_rotate_summary_counts():
    cfg = RotatorConfig(slots=["s1", "s2"])
    rotated = rotate_results([_r() for _ in range(3)], cfg)
    summary = format_rotate_summary(rotated)
    # s1 gets 2 results, s2 gets 1
    assert "s1: 2" in summary
    assert "s2: 1" in summary
