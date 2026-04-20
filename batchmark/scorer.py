"""Score benchmark results relative to a baseline using a simple weighted formula."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.aggregator import AggregatedResult


@dataclass
class ScoredResult:
    size: int
    mean: Optional[float]          # ms
    baseline_mean: Optional[float] # ms
    score: Optional[float]         # lower is better; 1.0 == on par with baseline
    delta_pct: Optional[float]     # percentage change vs baseline


def _ratio(value: Optional[float], baseline: Optional[float]) -> Optional[float]:
    if value is None or baseline is None or baseline == 0.0:
        return None
    return value / baseline


def _delta_pct(value: Optional[float], baseline: Optional[float]) -> Optional[float]:
    ratio = _ratio(value, baseline)
    if ratio is None:
        return None
    return (ratio - 1.0) * 100.0


def score_results(
    results: List[AggregatedResult],
    baseline: List[AggregatedResult],
) -> List[ScoredResult]:
    """Pair each result with its baseline by size and compute a score."""
    baseline_by_size = {r.size: r for r in baseline}
    scored: List[ScoredResult] = []
    for r in results:
        base = baseline_by_size.get(r.size)
        base_mean = base.mean if base is not None else None
        ratio = _ratio(r.mean, base_mean)
        scored.append(
            ScoredResult(
                size=r.size,
                mean=r.mean,
                baseline_mean=base_mean,
                score=ratio,
                delta_pct=_delta_pct(r.mean, base_mean),
            )
        )
    return scored


def format_scored(rows: List[ScoredResult]) -> str:
    """Return a human-readable table of scored results."""
    header = f"{'Size':>10}  {'Mean(ms)':>10}  {'Base(ms)':>10}  {'Score':>8}  {'Delta%':>8}"
    sep = "-" * len(header)
    lines = [header, sep]
    for r in rows:
        mean_s = f"{r.mean:.2f}" if r.mean is not None else "N/A"
        base_s = f"{r.baseline_mean:.2f}" if r.baseline_mean is not None else "N/A"
        score_s = f"{r.score:.4f}" if r.score is not None else "N/A"
        delta_s = f"{r.delta_pct:+.1f}%" if r.delta_pct is not None else "N/A"
        lines.append(f"{r.size:>10}  {mean_s:>10}  {base_s:>10}  {score_s:>8}  {delta_s:>8}")
    return "\n".join(lines)
