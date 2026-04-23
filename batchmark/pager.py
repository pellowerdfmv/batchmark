"""Pager: split a flat list of results into pages for display."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class PagerConfig:
    page_size: int = 20
    page: int = 1  # 1-based


@dataclass
class PageResult:
    items: List[TimingResult]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 1
        return max(1, (self.total + self.page_size - 1) // self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


def paginate(
    results: List[TimingResult],
    config: Optional[PagerConfig] = None,
) -> PageResult:
    """Return a single page of results according to *config*."""
    if config is None:
        config = PagerConfig()

    page_size = max(1, config.page_size)
    total = len(results)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(config.page, total_pages))

    start = (page - 1) * page_size
    end = start + page_size
    items = results[start:end]

    return PageResult(items=items, page=page, page_size=page_size, total=total)


def format_page_summary(pr: PageResult) -> str:
    """Return a one-line summary such as 'Page 2/5  (items 21-40 of 100)'."""
    start = (pr.page - 1) * pr.page_size + 1
    end = start + len(pr.items) - 1
    if pr.total == 0:
        return "Page 0/0  (no results)"
    return (
        f"Page {pr.page}/{pr.total_pages}  "
        f"(items {start}-{end} of {pr.total})"
    )
