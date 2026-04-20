"""Human-readable reporting for checkpoint state."""

from __future__ import annotations

from typing import List

from batchmark.checkpoint import CheckpointEntry


def format_checkpoint_header() -> str:
    return f"{'Size':>10}  {'Run':>6}  {'Duration(ms)':>14}  {'RC':>4}  Status"


def _status(returncode: int) -> str:
    return "OK" if returncode == 0 else "FAIL"


def format_checkpoint_row(entry: CheckpointEntry) -> str:
    dur_ms = entry.duration * 1000
    status = _status(entry.returncode)
    return (
        f"{entry.size:>10}  {entry.run_index:>6}  "
        f"{dur_ms:>14.2f}  {entry.returncode:>4}  {status}"
    )


def format_checkpoint_summary(entries: List[CheckpointEntry]) -> str:
    total = len(entries)
    ok = sum(1 for e in entries if e.returncode == 0)
    sizes = len({e.size for e in entries})
    return (
        f"Checkpoint: {total} run(s) across {sizes} size(s) — "
        f"{ok} OK, {total - ok} failed"
    )


def print_checkpoint_report(
    entries: List[CheckpointEntry], print_fn=print
) -> None:
    if not entries:
        print_fn("No checkpoint data.")
        return
    print_fn(format_checkpoint_header())
    print_fn("-" * 52)
    for entry in sorted(entries, key=lambda e: (e.size, e.run_index)):
        print_fn(format_checkpoint_row(entry))
    print_fn("-" * 52)
    print_fn(format_checkpoint_summary(entries))
