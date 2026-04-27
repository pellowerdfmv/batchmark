"""Tests for batchmark.stacker."""
from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.stacker import (
    StackConfig,
    StackedRow,
    stack_results,
    format_stack_summary,
)


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


def test_stack_results_returns_one_row_per_result():
    sets = [[_r(10), _r(20)], [_r(10), _r(20)]]
    rows = stack_results(sets)
    assert len(rows) == 4


def test_stack_assigns_labels_from_config():
    sets = [[_r(10)], [_r(10)]]
    cfg = StackConfig(labels=["baseline", "candidate"])
    rows = stack_results(sets, cfg)
    assert rows[0].label == "baseline"
    assert rows[1].label == "candidate"


def test_stack_uses_default_label_when_no_config():
    rows = stack_results([[_r(10)]])
    assert rows[0].label == "unlabeled"


def test_stack_uses_default_label_for_extra_sets():
    sets = [[_r(10)], [_r(10)], [_r(10)]]
    cfg = StackConfig(labels=["a"], default_label="other")
    rows = stack_results(sets, cfg)
    assert rows[0].label == "a"
    assert rows[1].label == "other"
    assert rows[2].label == "other"


def test_stack_run_index_increments_per_size():
    sets = [[_r(10), _r(10), _r(20)]]
    rows = stack_results(sets)
    size10 = [r for r in rows if r.size == 10]
    assert size10[0].run_index == 0
    assert size10[1].run_index == 1
    size20 = [r for r in rows if r.size == 20]
    assert size20[0].run_index == 0


def test_stack_run_index_resets_across_sets():
    sets = [[_r(10), _r(10)], [_r(10)]]
    rows = stack_results(sets)
    # second set should restart index at 0 for size 10
    second_set_row = rows[2]
    assert second_set_row.run_index == 0


def test_stack_failed_result_has_none_duration():
    sets = [[_r(10, returncode=1)]]
    rows = stack_results(sets)
    assert rows[0].duration is None
    assert rows[0].success is False


def test_stack_successful_result_has_duration():
    sets = [[_r(10, duration=0.25)]]
    rows = stack_results(sets)
    assert rows[0].duration == 0.25
    assert rows[0].success is True


def test_stack_empty_input_returns_empty():
    rows = stack_results([])
    assert rows == []


def test_format_stack_summary_no_results():
    assert format_stack_summary([]) == "No stacked results."


def test_format_stack_summary_contains_label_and_size():
    sets = [[_r(100)], [_r(200)]]
    cfg = StackConfig(labels=["a", "b"])
    rows = stack_results(sets, cfg)
    summary = format_stack_summary(rows)
    assert "a" in summary
    assert "b" in summary
    assert "100" in summary
    assert "200" in summary
