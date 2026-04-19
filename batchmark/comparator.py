"""Compare benchmark results across two result sets."""

from dataclasses import dataclass
from typing import Dict, List, Optional

from batchmark.stats import mean
from batchmark.timer import TimingResult


@dataclass
class ComparisonRow:
    size: int
    mean_a: Optional[float]
    mean_b: Optional[float]
    delta: Optional[float]
    ratio: Optional[float]


def _mean_by_size(results: List[TimingResult]) -> Dict[int, Optional[float]]:
    sizes = sorted({r.size for r in results})
    out: Dict[int, Optional[float]] = {}
    for size in sizes:
        subset = [r for r in results if r.size == size]
        out[size] = mean(subset)
    return out


def compare(
    results_a: List[TimingResult],
    results_b: List[TimingResult],
) -> List[ComparisonRow]:
    """Return per-size comparison between two result sets."""
    means_a = _mean_by_size(results_a)
    means_b = _mean_by_size(results_b)
    sizes = sorted(set(means_a) | set(means_b))
    rows: List[ComparisonRow] = []
    for size in sizes:
        ma = means_a.get(size)
        mb = means_b.get(size)
        if ma is not None and mb is not None:
            delta: Optional[float] = mb - ma
            ratio: Optional[float] = mb / ma if ma != 0 else None
        else:
            delta = None
            ratio = None
        rows.append(ComparisonRow(size=size, mean_a=ma, mean_b=mb, delta=delta, ratio=ratio))
    return rows


def format_comparison(rows: List[ComparisonRow]) -> str:
    """Format comparison rows as a human-readable table."""
    header = f"{'Size':>10}  {'Mean A (s)':>12}  {'Mean B (s)':>12}  {'Delta (s)':>12}  {'Ratio':>8}"
    sep = "-" * len(header)
    lines = [header, sep]
    for row in rows:
        ma = f"{row.mean_a:.4f}" if row.mean_a is not None else "N/A"
        mb = f"{row.mean_b:.4f}" if row.mean_b is not None else "N/A"
        delta = f"{row.delta:+.4f}" if row.delta is not None else "N/A"
        ratio = f"{row.ratio:.3f}x" if row.ratio is not None else "N/A"
        lines.append(f"{row.size:>10}  {ma:>12}  {mb:>12}  {delta:>12}  {ratio:>8}")
    return "\n".join(lines)
