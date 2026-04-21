"""Tests for batchmark.capper."""

from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.capper import CapperConfig, CappedResult, cap_results, format_cap_summary


def _r(size: int, duration_ms: float, returncode: int = 0) -> TimingResult:
    return TimingResult(
        size=size,
        command="echo test",
        duration=duration_ms / 1000.0,
        returncode=returncode,
        stdout="",
        stderr="",
    )


def test_cap_results_no_cap_passes_through():
    results = [_r(100, 500), _r(200, 1500)]
    config = CapperConfig(max_ms=None)
    out = cap_results(results, config)
    assert len(out) == 2
    assert all(not c.capped for c in out)
    assert out[0].duration == pytest.approx(0.5)
    assert out[1].duration == pytest.approx(1.5)


def test_cap_results_clamps_exceeding_duration():
    results = [_r(100, 2000)]
    config = CapperConfig(max_ms=1000)
    out = cap_results(results, config)
    assert out[0].capped is True
    assert out[0].duration == pytest.approx(1.0)
    assert out[0].original_duration == pytest.approx(2.0)


def test_cap_results_does_not_clamp_within_limit():
    results = [_r(100, 500)]
    config = CapperConfig(max_ms=1000)
    out = cap_results(results, config)
    assert out[0].capped is False
    assert out[0].duration == pytest.approx(0.5)


def test_cap_results_does_not_clamp_failed_results():
    results = [_r(100, 5000, returncode=1)]
    config = CapperConfig(max_ms=1000)
    out = cap_results(results, config)
    assert out[0].capped is False
    assert out[0].duration == pytest.approx(5.0)


def test_cap_results_preserves_order():
    results = [_r(10, 100), _r(20, 3000), _r(30, 200)]
    config = CapperConfig(max_ms=1000)
    out = cap_results(results, config)
    assert [c.size for c in out] == [10, 20, 30]
    assert out[1].capped is True


def test_cap_results_zero_max_ms_disables_cap():
    results = [_r(100, 9999)]
    config = CapperConfig(max_ms=0)
    out = cap_results(results, config)
    assert out[0].capped is False


def test_capped_result_proxies_size_and_success():
    r = _r(256, 500)
    config = CapperConfig(max_ms=1000)
    out = cap_results([r], config)
    assert out[0].size == 256
    assert out[0].success is True


def test_format_cap_summary_disabled():
    config = CapperConfig(max_ms=None)
    out = cap_results([], config)
    summary = format_cap_summary(out, config)
    assert "disabled" in summary.lower()


def test_format_cap_summary_shows_counts():
    results = [_r(10, 500), _r(20, 2000), _r(30, 3000)]
    config = CapperConfig(max_ms=1000)
    out = cap_results(results, config)
    summary = format_cap_summary(out, config)
    assert "2/3" in summary
    assert "1000" in summary
