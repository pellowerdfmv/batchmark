"""Console reporter for grouped benchmark results."""

from typing import Dict, List

from batchmark.grouper import GroupedResult, results_by_label


def _fmt_ms(seconds: float) -> str:
    return f"{seconds * 1000:.2f} ms"


def format_group_header() -> str:
    return f"{'Label':<20} {'Size':>8} {'Duration':>12} {'Status':>8}"


def format_group_row(g: GroupedResult) -> str:
    status = "OK" if g.success else "FAIL"
    return f"{g.label:<20} {g.size:>8} {_fmt_ms(g.duration):>12} {status:>8}"


def format_group_summary(grouped: List[GroupedResult]) -> str:
    by_label: Dict[str, List[GroupedResult]] = results_by_label(grouped)
    lines = []
    for label, items in sorted(by_label.items()):
        total = len(items)
        ok = sum(1 for g in items if g.success)
        durations = [g.duration for g in items if g.success]
        avg = (sum(durations) / len(durations)) if durations else None
        avg_str = _fmt_ms(avg) if avg is not None else "N/A"
        lines.append(
            f"  {label}: {ok}/{total} ok, avg={avg_str}"
        )
    return "Group summary:\n" + "\n".join(lines)


def print_group_report(grouped: List[GroupedResult]) -> None:
    print(format_group_header())
    print("-" * 52)
    for g in grouped:
        print(format_group_row(g))
    print()
    print(format_group_summary(grouped))
