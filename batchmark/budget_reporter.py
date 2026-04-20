"""Human-readable reporting for budget consumption."""

from __future__ import annotations

from typing import List, Optional

from batchmark.budget import BudgetConfig, BudgetState
from batchmark.timer import TimingResult

_COL_WIDTH = 14


def _fmt(seconds: float) -> str:
    """Format a duration in seconds to a tidy string."""
    ms = seconds * 1_000
    if ms < 1_000:
        return f"{ms:.1f} ms"
    return f"{seconds:.3f} s"


def format_budget_header() -> str:
    cols = ["budget", "used", "remaining", "status"]
    return "  ".join(c.ljust(_COL_WIDTH) for c in cols).rstrip()


def format_budget_row(
    config: BudgetConfig,
    state: BudgetState,
) -> str:
    limit = config.max_total_seconds
    if limit is None:
        budget_str = "unlimited"
        remaining_str = "—"
        status = "OK"
    else:
        budget_str = _fmt(limit)
        rem = state.remaining()
        remaining_str = _fmt(rem) if rem is not None else "—"
        status = "EXCEEDED" if state.is_exceeded() else "OK"

    used_str = _fmt(state.elapsed)

    cols = [budget_str, used_str, remaining_str, status]
    return "  ".join(c.ljust(_COL_WIDTH) for c in cols).rstrip()


def format_budget_summary(
    config: BudgetConfig,
    state: BudgetState,
    total_results: int,
    kept_results: int,
) -> str:
    lines = [
        f"Budget summary:",
        f"  Total results : {total_results}",
        f"  Kept results  : {kept_results}",
        f"  Dropped       : {total_results - kept_results}",
        f"  Elapsed       : {_fmt(state.elapsed)}",
    ]
    if config.max_total_seconds is not None:
        lines.append(f"  Budget        : {_fmt(config.max_total_seconds)}")
        lines.append(
            f"  Status        : {'EXCEEDED' if state.is_exceeded() else 'OK'}"
        )
    else:
        lines.append("  Budget        : unlimited")
    return "\n".join(lines)


def print_budget_report(
    config: BudgetConfig,
    results: List[TimingResult],
    kept: List[TimingResult],
) -> None:
    """Print a budget consumption report to stdout."""
    state = BudgetState(config=config)
    for r in kept:
        state.record(r)

    print(format_budget_header())
    print(format_budget_row(config, state))
    print()
    print(format_budget_summary(config, state, len(results), len(kept)))
