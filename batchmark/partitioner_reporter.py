"""Console reporter for partitioned results."""

from __future__ import annotations

from typing import List, Sequence

from batchmark.partitioner import PartitionedResult


def _fmt_ms(seconds: float | None) -> str:
    if seconds is None:
        return "N/A"
    return f"{seconds * 1000:.1f} ms"


def _status(pr: PartitionedResult) -> str:
    return "OK" if pr.success else "FAIL"


def format_partition_header() -> str:
    return f"{'Size':>8}  {'Duration':>12}  {'Status':>6}  {'Partition'}"


def format_partition_row(pr: PartitionedResult) -> str:
    partition_label = pr.partition if pr.partition is not None else "-"
    return (
        f"{pr.size:>8}  "
        f"{_fmt_ms(pr.duration):>12}  "
        f"{_status(pr):>6}  "
        f"{partition_label}"
    )


def format_partition_summary(partitioned: Sequence[PartitionedResult]) -> str:
    counts: dict[str, int] = {}
    failed = 0
    for pr in partitioned:
        if pr.partition is None:
            failed += 1
        else:
            counts[pr.partition] = counts.get(pr.partition, 0) + 1
    lines = ["\nPartition summary:"]
    for label, n in counts.items():
        lines.append(f"  {label}: {n}")
    if failed:
        lines.append(f"  failed (unpartitioned): {failed}")
    return "\n".join(lines)


def print_partition_report(partitioned: List[PartitionedResult]) -> None:
    print(format_partition_header())
    print("-" * 44)
    for pr in partitioned:
        print(format_partition_row(pr))
    print(format_partition_summary(partitioned))
