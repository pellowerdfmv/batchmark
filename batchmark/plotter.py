"""ASCII sparkline and summary plotter for aggregated benchmark results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.aggregator import AggregatedResult

_SPARKS = " ▁▂▃▄▅▆▇█"


@dataclass
class PlotConfig:
    width: int = 40
    show_axis: bool = True
    label: str = "duration (ms)"


def _sparkline(values: List[Optional[float]], width: int) -> str:
    """Return a unicode sparkline string for *values* (None treated as 0)."""
    clean = [v if v is not None else 0.0 for v in values]
    if not clean:
        return ""
    lo, hi = min(clean), max(clean)
    span = hi - lo or 1.0
    buckets = len(_SPARKS) - 1
    chars = []
    for v in clean:
        idx = int((v - lo) / span * buckets)
        chars.append(_SPARKS[min(idx, buckets)])
    line = "".join(chars)
    # Pad or truncate to requested width
    if len(line) > width:
        step = len(line) / width
        line = "".join(line[int(i * step)] for i in range(width))
    return line


def format_plot(results: List[AggregatedResult], cfg: Optional[PlotConfig] = None) -> str:
    """Return a multi-line ASCII plot of mean durations by size."""
    if cfg is None:
        cfg = PlotConfig()

    if not results:
        return "(no data to plot)"

    sorted_results = sorted(results, key=lambda r: r.size)
    sizes = [r.size for r in sorted_results]
    means: List[Optional[float]] = [
        r.mean_ms if r.successful > 0 else None for r in sorted_results
    ]

    spark = _sparkline(means, cfg.width)
    lines: List[str] = []

    if cfg.show_axis:
        valid = [m for m in means if m is not None]
        lo = min(valid) if valid else 0.0
        hi = max(valid) if valid else 0.0
        lines.append(f"  {cfg.label}  min={lo:.1f}  max={hi:.1f}")
        lines.append("  " + spark)
        size_labels = "  ".join(str(s) for s in sizes)
        lines.append(f"  sizes: {size_labels}")
    else:
        lines.append(spark)

    return "\n".join(lines)


def print_plot(results: List[AggregatedResult], cfg: Optional[PlotConfig] = None) -> None:
    """Print the ASCII plot to stdout."""
    print(format_plot(results, cfg))
