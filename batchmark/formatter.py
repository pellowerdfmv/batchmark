"""Output formatters for batchmark results (table, json, csv-like summary)."""

from __future__ import annotations

import json
from typing import List, Literal

from batchmark.aggregator import AggregatedResult

OutputFormat = Literal["table", "json", "csv"]

AVAILABLE_FORMATS: List[OutputFormat] = ["table", "json", "csv"]


def _fmt_ms(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.2f} ms"


def format_table(results: List[AggregatedResult]) -> str:
    """Render aggregated results as a fixed-width table string."""
    header = f"{'Size':>10}  {'Runs':>5}  {'OK':>5}  {'Mean':>12}  {'Median':>12}  {'Stdev':>12}  {'Min':>12}  {'Max':>12}"
    separator = "-" * len(header)
    rows = [header, separator]
    for r in results:
        row = (
            f"{r.size:>10}  "
            f"{r.total_runs:>5}  "
            f"{r.successful_runs:>5}  "
            f"{_fmt_ms(r.mean):>12}  "
            f"{_fmt_ms(r.median):>12}  "
            f"{_fmt_ms(r.stdev):>12}  "
            f"{_fmt_ms(r.min_duration):>12}  "
            f"{_fmt_ms(r.max_duration):>12}"
        )
        rows.append(row)
    return "\n".join(rows)


def format_json(results: List[AggregatedResult]) -> str:
    """Render aggregated results as a JSON string."""
    data = [
        {
            "size": r.size,
            "total_runs": r.total_runs,
            "successful_runs": r.successful_runs,
            "mean_s": r.mean,
            "median_s": r.median,
            "stdev_s": r.stdev,
            "min_s": r.min_duration,
            "max_s": r.max_duration,
        }
        for r in results
    ]
    return json.dumps(data, indent=2)


def format_csv(results: List[AggregatedResult]) -> str:
    """Render aggregated results as CSV text."""
    lines = ["size,total_runs,successful_runs,mean_s,median_s,stdev_s,min_s,max_s"]
    for r in results:
        lines.append(
            f"{r.size},{r.total_runs},{r.successful_runs},"
            f"{r.mean},{r.median},{r.stdev},{r.min_duration},{r.max_duration}"
        )
    return "\n".join(lines)


def format_output(results: List[AggregatedResult], fmt: OutputFormat) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "table":
        return format_table(results)
    if fmt == "json":
        return format_json(results)
    if fmt == "csv":
        return format_csv(results)
    raise ValueError(f"Unknown format: {fmt!r}. Choose from {AVAILABLE_FORMATS}")
