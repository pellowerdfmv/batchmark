"""Tests for batchmark.clamper."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.clamper import (
    ClamperConfig,
    ClampedResult,
    clamp_results,
    format_clamp_summary,
)


def _r(size: int, duration: float, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        duration=duration,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_clamp_results_returns_one_per_input():
    results = [_r(10, 1.0), _r(20, 2.0)]
    out = clamp_results(results)
    assert len(out) == 2


def test_clamp_results_no_config_passes_through():
    results = [_r(10, 1.5)]
    out = clamp_results(results)
    assert out[0].duration == 1.5
    assert not out[0].clamped


def test_clamp_floor_raises_low_value():
    config = ClamperConfig(floor=1.0)
    out = clamp_results([_r(10, 0.3)], config)
    assert out[0].clamped
    assert out[0].duration == 1.0
    assert out[0].clamp_reason == "floor"


def test_clamp_floor_does_not_affect_value_above_floor():
    config = ClamperConfig(floor=0.5)
    out = clamp_results([_r(10, 1.2)], config)
    assert not out[0].clamped
    assert out[0].duration == 1.2


def test_clamp_ceiling_lowers_high_value():
    config = ClamperConfig(ceiling=2.0)
    out = clamp_results([_r(10, 5.0)], config)
    assert out[0].clamped
    assert out[0].duration == 2.0
    assert out[0].clamp_reason == "ceiling"


def test_clamp_ceiling_does_not_affect_value_below_ceiling():
    config = ClamperConfig(ceiling=10.0)
    out = clamp_results([_r(10, 3.0)], config)
    assert not out[0].clamped
    assert out[0].duration == 3.0


def test_clamp_floor_and_ceiling_together():
    config = ClamperConfig(floor=1.0, ceiling=5.0)
    results = [_r(10, 0.1), _r(20, 3.0), _r(30, 9.9)]
    out = clamp_results(results, config)
    assert out[0].duration == 1.0
    assert out[1].duration == 3.0
    assert out[2].duration == 5.0


def test_clamp_failures_skipped_by_default():
    config = ClamperConfig(floor=2.0)
    out = clamp_results([_r(10, 0.1, returncode=1)], config)
    assert not out[0].clamped
    assert out[0].duration == 0.1


def test_clamp_failures_applied_when_enabled():
    config = ClamperConfig(floor=2.0, clamp_failures=True)
    out = clamp_results([_r(10, 0.1, returncode=1)], config)
    assert out[0].clamped
    assert out[0].duration == 2.0


def test_original_duration_preserved():
    config = ClamperConfig(ceiling=1.0)
    out = clamp_results([_r(10, 4.5)], config)
    assert out[0].original_duration == 4.5
    assert out[0].clamped_duration == 1.0


def test_format_clamp_summary_counts():
    config = ClamperConfig(floor=1.0, ceiling=3.0)
    results = [_r(10, 0.1), _r(20, 2.0), _r(30, 9.0)]
    out = clamp_results(results, config)
    summary = format_clamp_summary(out)
    assert "2/3" in summary
    assert "floor=1" in summary
    assert "ceiling=1" in summary
