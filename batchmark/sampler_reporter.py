"""Console reporter for sampled timing results."""

from __future__ import annotations

from typing import List

from batchmark.timer import TimingResult
from batchmark.sampler import SamplerConfig, sample_results, format_sample_summary

_COL_W = 10
_SEPARATOR_WIDTH = 76


def _fmt_ms(value: float) -> str:
    return f"{value * 1000:.2f} ms"


def _status(result: TimingResult) -> str:
    return "OK" if result.returncode == 0 else "FAIL"


def format_sample_header() -> str:
    cols = ["Size", "Duration", "Status", "Command"]
    widths = [_COL_W, 14, 6, 40]
    return "  ".join(c.ljust(w) for c, w in zip(cols, widths))


def format_sample_row(result: TimingResult) -> str:
    widths = [_COL_W, 14, 6, 40]
    values = [
        str(result.size),
        _fmt_ms(result.duration),
        _status(result),
        (result.command or "")[:40],
    ]
    return "  ".join(v.ljust(w) for v, w in zip(values, widths))


def count_failures(results: List[TimingResult]) -> int:
    """Return the number of results with a non-zero return code."""
    return sum(1 for r in results if r.returncode != 0)


def print_sample_report(
    results: List[TimingResult],
    config: SamplerConfig,
    *,
    verbose: bool = False,
) -> List[TimingResult]:
    """Print a sampling report and return the sampled results."""
    sampled = sample_results(results, config)

    print(format_sample_header())
    print("-" * _SEPARATOR_WIDTH)
    for r in sampled:
        print(format_sample_row(r))

    print()
    print(format_sample_summary(results, sampled))

    failures = count_failures(sampled)
    if failures:
        print(f"Failures: {failures} of {len(sampled)} sampled results did not exit cleanly.")

    if verbose:
        sizes = sorted({r.size for r in sampled})
        print(f"Sizes represented: {', '.join(str(s) for s in sizes)}")

    return sampled
