"""Tests for batchmark.sampler_reporter."""

from __future__ import annotations

import io
import sys
from typing import List

from batchmark.timer import TimingResult
from batchmark.sampler import SamplerConfig
from batchmark.sampler_reporter import (
    format_sample_header,
    format_sample_row,
    print_sample_report,
)


def _r(size: int, rc: int = 0, dur: float = 0.25) -> TimingResult:
    return TimingResult(size=size, duration=dur, returncode=rc, command="sleep 0.1")


def test_format_sample_header_contains_columns():
    header = format_sample_header()
    for col in ("Size", "Duration", "Status", "Command"):
        assert col in header


def test_format_sample_row_ok():
    row = format_sample_row(_r(100, rc=0, dur=0.123))
    assert "100" in row
    assert "OK" in row
    assert "123.00 ms" in row


def test_format_sample_row_fail():
    row = format_sample_row(_r(200, rc=1, dur=0.05))
    assert "FAIL" in row
    assert "200" in row


def test_print_sample_report_returns_sampled(capsys):
    results = [_r(10)] * 6 + [_r(20)] * 6
    cfg = SamplerConfig(fraction=0.5, seed=0)
    sampled = print_sample_report(results, cfg)
    assert len(sampled) <= len(results)
    captured = capsys.readouterr()
    assert "Sampled" in captured.out


def test_print_sample_report_verbose_shows_sizes(capsys):
    results = [_r(10)] * 4 + [_r(20)] * 4
    cfg = SamplerConfig(fraction=1.0, seed=1)
    print_sample_report(results, cfg, verbose=True)
    captured = capsys.readouterr()
    assert "Sizes represented" in captured.out


def test_print_sample_report_empty_input(capsys):
    cfg = SamplerConfig(fraction=1.0)
    sampled = print_sample_report([], cfg)
    assert sampled == []
    captured = capsys.readouterr()
    assert "0/0" in captured.out
