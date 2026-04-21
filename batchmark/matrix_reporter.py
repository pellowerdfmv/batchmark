"""Reporter for matrix benchmark results."""

from typing import Dict, List, Optional, Tuple

from batchmark.matrix import MatrixCell


_COL_WIDTH = 12


def _fmt_ms(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.1f}ms"


def _mean_duration(cells: List[MatrixCell]) -> Optional[float]:
    durations = [c.result.duration for c in cells if c.result.returncode == 0]
    if not durations:
        return None
    return sum(durations) / len(durations)


def format_matrix_table(cells: List[MatrixCell]) -> str:
    """Format a pivot table: rows=sizes, columns=variants."""
    sizes = sorted({c.size for c in cells})
    variants = sorted({c.variant for c in cells})

    header_parts = [f"{'size':>{_COL_WIDTH}}"] + [
        f"{v:>{_COL_WIDTH}}" for v in variants
    ]
    lines = ["  ".join(header_parts)]
    lines.append("-" * len(lines[0]))

    for size in sizes:
        row_parts = [f"{size:>{_COL_WIDTH}}"]
        for variant in variants:
            matching = [c for c in cells if c.size == size and c.variant == variant]
            mean = _mean_duration(matching)
            row_parts.append(f"{_fmt_ms(mean):>{_COL_WIDTH}}")
        lines.append("  ".join(row_parts))

    return "\n".join(lines)


def format_matrix_summary(cells: List[MatrixCell]) -> str:
    total = len(cells)
    ok = sum(1 for c in cells if c.result.returncode == 0)
    failed = total - ok
    return f"Matrix: {total} runs total, {ok} succeeded, {failed} failed."


def print_matrix_report(cells: List[MatrixCell]) -> None:
    print(format_matrix_table(cells))
    print()
    print(format_matrix_summary(cells))
