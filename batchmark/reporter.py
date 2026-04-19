"""Console reporter for batch benchmark results."""

from typing import List
from batchmark.timer import TimingResult


COLUMNS = {
    "size": 8,
    "run": 5,
    "elapsed": 12,
    "returncode": 12,
    "status": 8,
}


def _status(result: TimingResult) -> str:
    return "OK" if result.returncode == 0 else "FAIL"


def format_header() -> str:
    return (
        f"{'size':>{COLUMNS['size']}}"
        f"  {'run':>{COLUMNS['run']}}"
        f"  {'elapsed(s)':>{COLUMNS['elapsed']}}"
        f"  {'returncode':>{COLUMNS['returncode']}}"
        f"  {'status':<{COLUMNS['status']}}"
    )


def format_row(result: TimingResult) -> str:
    return (
        f"{result.size:>{COLUMNS['size']}}"
        f"  {result.run:>{COLUMNS['run']}}"
        f"  {result.elapsed:>{COLUMNS['elapsed']}.4f}"
        f"  {result.returncode:>{COLUMNS['returncode']}}"
        f"  {_status(result):<{COLUMNS['status']}}"
    )


def format_summary(results: List[TimingResult]) -> str:
    if not results:
        return "No results."
    successful = [r for r in results if r.returncode == 0]
    elapsed_values = [r.elapsed for r in successful]
    total = sum(elapsed_values)
    avg = total / len(elapsed_values) if elapsed_values else 0.0
    min_e = min(elapsed_values) if elapsed_values else 0.0
    max_e = max(elapsed_values) if elapsed_values else 0.0
    lines = [
        "",
        f"Summary: {len(successful)}/{len(results)} successful runs",
        f"  total elapsed : {total:.4f}s",
        f"  avg elapsed   : {avg:.4f}s",
        f"  min elapsed   : {min_e:.4f}s",
        f"  max elapsed   : {max_e:.4f}s",
    ]
    return "\n".join(lines)


def print_results(results: List[TimingResult], file=None) -> None:
    import sys
    out = file or sys.stdout
    print(format_header(), file=out)
    print("-" * 55, file=out)
    for r in results:
        print(format_row(r), file=out)
    print(format_summary(results), file=out)
