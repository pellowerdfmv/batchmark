"""Tests for batchmark.pager."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.pager import PagerConfig, PageResult, paginate, format_page_summary


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


def _results(n: int) -> list:
    return [_r(i + 1) for i in range(n)]


def test_paginate_first_page():
    results = _results(50)
    pr = paginate(results, PagerConfig(page_size=20, page=1))
    assert pr.page == 1
    assert len(pr.items) == 20
    assert pr.items[0].size == 1


def test_paginate_second_page():
    results = _results(50)
    pr = paginate(results, PagerConfig(page_size=20, page=2))
    assert pr.page == 2
    assert len(pr.items) == 20
    assert pr.items[0].size == 21


def test_paginate_last_page_partial():
    results = _results(45)
    pr = paginate(results, PagerConfig(page_size=20, page=3))
    assert pr.page == 3
    assert len(pr.items) == 5


def test_total_pages():
    results = _results(45)
    pr = paginate(results, PagerConfig(page_size=20, page=1))
    assert pr.total_pages == 3


def test_has_next_and_prev():
    results = _results(50)
    pr = paginate(results, PagerConfig(page_size=20, page=2))
    assert pr.has_next is True
    assert pr.has_prev is True


def test_first_page_has_no_prev():
    results = _results(50)
    pr = paginate(results, PagerConfig(page_size=20, page=1))
    assert pr.has_prev is False


def test_last_page_has_no_next():
    results = _results(40)
    pr = paginate(results, PagerConfig(page_size=20, page=2))
    assert pr.has_next is False


def test_page_clamps_to_last_when_out_of_range():
    results = _results(10)
    pr = paginate(results, PagerConfig(page_size=5, page=999))
    assert pr.page == 2


def test_empty_results():
    pr = paginate([], PagerConfig(page_size=10, page=1))
    assert pr.items == []
    assert pr.total == 0
    assert pr.total_pages == 1


def test_default_config():
    results = _results(5)
    pr = paginate(results)
    assert pr.page == 1
    assert pr.page_size == 20
    assert len(pr.items) == 5


def test_format_page_summary_contains_page_info():
    results = _results(50)
    pr = paginate(results, PagerConfig(page_size=20, page=2))
    summary = format_page_summary(pr)
    assert "Page 2/3" in summary
    assert "21-40" in summary
    assert "50" in summary


def test_format_page_summary_empty():
    pr = paginate([], PagerConfig(page_size=10, page=1))
    summary = format_page_summary(pr)
    assert "no results" in summary
