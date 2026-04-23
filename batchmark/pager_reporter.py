"""Console reporter for paginated results."""

from __future__ import annotations

from typing import List

from batchmark.pager import PageResult, format_page_summary
from batchmark.reporter import format_header, format_row


def print_page_report(pr: PageResult) -> None:
    """Print a paginated table of timing results to stdout."""
    print(format_header())
    for result in pr.items:
        print(format_row(result))
    print()
    print(format_page_summary(pr))
    nav: List[str] = []
    if pr.has_prev:
        nav.append(f"  prev: page {pr.page - 1}")
    if pr.has_next:
        nav.append(f"  next: page {pr.page + 1}")
    if nav:
        print("\n".join(nav))
