"""Console reporter for ranked benchmark results."""

from __future__ import annotations

from typing import List

from batchmark.ranker import RankedResult, format_ranked

_TIER_SYMBOLS = {
    "fast": "✓",
    "medium": "~",
    "slow": "✗",
}


def _tier_symbol(tier: str) -> str:
    return _TIER_SYMBOLS.get(tier, "?")


def format_rank_header() -> str:
    return f"{'#':<4} {'Size':>10} {'Mean (ms)':>12} {'Successful':>12} {'Tier':<8} {'':>2}"


def format_rank_row(r: RankedResult) -> str:
    mean_str = f"{r.mean:.2f}" if r.mean is not None else "N/A"
    sym = _tier_symbol(r.tier)
    return (
        f"{r.rank:<4} {r.size:>10} {mean_str:>12}"
        f" {r.aggregated.successful:>12} {r.tier:<8} {sym:>2}"
    )


def format_rank_summary(ranked: List[RankedResult]) -> str:
    total = len(ranked)
    fast = sum(1 for r in ranked if r.tier == "fast")
    medium = sum(1 for r in ranked if r.tier == "medium")
    slow = sum(1 for r in ranked if r.tier == "slow")
    return (
        f"Total sizes: {total} | "
        f"Fast: {fast} | Medium: {medium} | Slow: {slow}"
    )


def print_rank_report(ranked: List[RankedResult]) -> None:
    """Print a full ranking report to stdout."""
    if not ranked:
        print("No results to rank.")
        return
    print(format_rank_header())
    print("-" * 52)
    for r in ranked:
        print(format_rank_row(r))
    print("-" * 52)
    print(format_rank_summary(ranked))
