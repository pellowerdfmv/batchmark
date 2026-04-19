"""Aggregate TimingResults by size, producing summary statistics per group."""

from dataclasses import dataclass
from typing import Dict, List

from batchmark.stats import mean, median, stdev, min_duration, max_duration
from batchmark.timer import TimingResult


@dataclass
class AggregatedResult:
    size: int
    runs: int
    successful: int
    mean: float
    median: float
    stdev: float
    min: float
    max: float


def _group_by_size(results: List[TimingResult]) -> Dict[int, List[TimingResult]]:
    groups: Dict[int, List[TimingResult]] = {}
    for r in results:
        groups.setdefault(r.size, []).append(r)
    return groups


def aggregate(results: List[TimingResult]) -> List[AggregatedResult]:
    """Return one AggregatedResult per unique size, sorted by size."""
    groups = _group_by_size(results)
    aggregated = []
    for size, group in sorted(groups.items()):
        successful = [r for r in group if r.returncode == 0]
        aggregated.append(
            AggregatedResult(
                size=size,
                runs=len(group),
                successful=len(successful),
                mean=mean(group),
                median=median(group),
                stdev=stdev(group),
                min=min_duration(group),
                max=max_duration(group),
            )
        )
    return aggregated


def format_aggregated(rows: List[AggregatedResult]) -> str:
    """Return a simple table string for the aggregated results."""
    header = f"{'Size':>10}  {'Runs':>5}  {'OK':>5}  {'Mean':>10}  {'Median':>10}  {'Stdev':>10}  {'Min':>10}  {'Max':>10}"
    lines = [header, "-" * len(header)]
    for r in rows:
        lines.append(
            f"{r.size:>10}  {r.runs:>5}  {r.successful:>5}  "
            f"{r.mean:>10.4f}  {r.median:>10.4f}  {r.stdev:>10.4f}  "
            f"{r.min:>10.4f}  {r.max:>10.4f}"
        )
    return "\n".join(lines)
