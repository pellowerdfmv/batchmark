"""Console reporter for tagged benchmark results."""

from __future__ import annotations

from typing import List, Optional

from batchmark.tagger import TaggedResult, unique_tag_values

_COL_WIDTHS = {
    "size": 10,
    "tag": 18,
    "duration": 14,
    "status": 8,
}


def _fmt_duration(duration: Optional[float]) -> str:
    if duration is None:
        return "N/A"
    return f"{duration * 1000:.2f} ms"


def _status(success: bool) -> str:
    return "OK" if success else "FAIL"


def format_tag_header(tag_key: str) -> str:
    """Return a formatted header line that includes the tag key column."""
    size_h = "Size".ljust(_COL_WIDTHS["size"])
    tag_h = tag_key.capitalize().ljust(_COL_WIDTHS["tag"])
    dur_h = "Duration".ljust(_COL_WIDTHS["duration"])
    status_h = "Status".ljust(_COL_WIDTHS["status"])
    return f"{size_h}{tag_h}{dur_h}{status_h}"


def format_tag_row(tagged: TaggedResult, tag_key: str) -> str:
    """Return a single formatted result row."""
    size_s = str(tagged.size).ljust(_COL_WIDTHS["size"])
    tag_val = tagged.tags.get(tag_key, "").ljust(_COL_WIDTHS["tag"])
    dur_s = _fmt_duration(tagged.duration).ljust(_COL_WIDTHS["duration"])
    status_s = _status(tagged.success).ljust(_COL_WIDTHS["status"])
    return f"{size_s}{tag_val}{dur_s}{status_s}"


def format_tag_summary(tagged: List[TaggedResult], tag_key: str) -> str:
    """Return a short summary line per unique tag value."""
    lines: List[str] = []
    for val in unique_tag_values(tagged, tag_key):
        group = [t for t in tagged if t.tags.get(tag_key) == val]
        total = len(group)
        ok = sum(1 for t in group if t.success)
        lines.append(f"  {tag_key}={val!r}: {ok}/{total} succeeded")
    return "\n".join(lines) if lines else "  (no tagged results)"


def print_tag_results(
    tagged: List[TaggedResult],
    tag_key: str,
    *,
    show_summary: bool = True,
) -> None:
    """Print a full tagged-results table to stdout."""
    header = format_tag_header(tag_key)
    separator = "-" * len(header)
    print(header)
    print(separator)
    for t in tagged:
        print(format_tag_row(t, tag_key))
    if show_summary:
        print(separator)
        print("Summary by tag:")
        print(format_tag_summary(tagged, tag_key))
