"""Tests for batchmark.dispatcher."""

from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.dispatcher import (
    DispatchConfig,
    DispatchedResult,
    dispatch_results,
    group_by_handler,
    format_dispatch_summary,
)


def _r(size: int, rc: int = 0, dur: float = 0.1) -> TimingResult:
    return TimingResult(size=size, returncode=rc, duration=dur, stdout="", stderr="")


# --- dispatch_results ---------------------------------------------------------

def test_dispatch_results_returns_one_per_input():
    results = [_r(10), _r(20), _r(30)]
    dispatched = dispatch_results(results)
    assert len(dispatched) == 3


def test_dispatch_default_handler_when_no_rules():
    dr = dispatch_results([_r(100)])[0]
    assert dr.handler == "default"


def test_dispatch_custom_default_handler():
    cfg = DispatchConfig(default_handler="fallback")
    dr = dispatch_results([_r(50)], cfg)[0]
    assert dr.handler == "fallback"


def test_dispatch_matches_rule_by_size():
    cfg = DispatchConfig(rules=[(1, 100, "small"), (101, 500, "large")])
    results = [_r(50), _r(200)]
    dispatched = dispatch_results(results, cfg)
    assert dispatched[0].handler == "small"
    assert dispatched[1].handler == "large"


def test_dispatch_boundary_inclusive():
    cfg = DispatchConfig(rules=[(100, 100, "exact")])
    dr = dispatch_results([_r(100)], cfg)[0]
    assert dr.handler == "exact"


def test_dispatch_unmatched_uses_default():
    cfg = DispatchConfig(rules=[(1, 10, "tiny")], default_handler="other")
    dr = dispatch_results([_r(999)], cfg)[0]
    assert dr.handler == "other"


def test_dispatched_result_preserves_reference():
    r = _r(42)
    dr = dispatch_results([r])[0]
    assert dr.result is r


def test_dispatched_result_success_flag():
    ok = dispatch_results([_r(1, rc=0)])[0]
    fail = dispatch_results([_r(1, rc=1)])[0]
    assert ok.success is True
    assert fail.success is False


# --- group_by_handler ---------------------------------------------------------

def test_group_by_handler_keys():
    cfg = DispatchConfig(rules=[(1, 50, "small"), (51, 200, "large")])
    dispatched = dispatch_results([_r(10), _r(20), _r(100)], cfg)
    groups = group_by_handler(dispatched)
    assert set(groups.keys()) == {"small", "large"}


def test_group_by_handler_counts():
    cfg = DispatchConfig(rules=[(1, 50, "small")])
    dispatched = dispatch_results([_r(10), _r(20), _r(30)], cfg)
    groups = group_by_handler(dispatched)
    assert len(groups["small"]) == 3


# --- format_dispatch_summary --------------------------------------------------

def test_format_dispatch_summary_contains_handler():
    cfg = DispatchConfig(rules=[(1, 100, "myhandler")])
    dispatched = dispatch_results([_r(50)], cfg)
    summary = format_dispatch_summary(dispatched)
    assert "myhandler" in summary


def test_format_dispatch_summary_contains_count():
    dispatched = dispatch_results([_r(1), _r(2), _r(3)])
    summary = format_dispatch_summary(dispatched)
    assert "3" in summary
