"""Console reporter for classified timing results."""
from __future__ import annotations

from typing import List

from batchmark.classifier import ClassifiedResult, format_classification_summary

_COL_SIZE = 10
_COL_DURATION = 14
_COL_STATUS = 8
_COL_CLASS = 10


def format_classified_header() -> str:
    return (
        f"{'Size':>{_COL_SIZE}}  "
        f"{'Duration(s)':>{_COL_DURATION}}  "
        f"{'Status':<{_COL_STATUS}}  "
        f"{'Class':<{_COL_CLASS}}"
    )


def _fmt_duration(d) -> str:
    return f"{d:.6f}" if d is not None else "N/A"


def _status(cr: ClassifiedResult) -> str:
    return "OK" if cr.success else "FAIL"


def format_classified_row(cr: ClassifiedResult) -> str:
    return (
        f"{cr.size:>{_COL_SIZE}}  "
        f"{_fmt_duration(cr.duration):>{_COL_DURATION}}  "
        f"{_status(cr):<{_COL_STATUS}}  "
        f"{cr.classification:<{_COL_CLASS}}"
    )


def print_classified_report(
    classified: List[ClassifiedResult],
    *,
    verbose: bool = False,
) -> None:
    print(format_classified_header())
    print("-" * (_COL_SIZE + _COL_DURATION + _COL_STATUS + _COL_CLASS + 6))
    for cr in classified:
        print(format_classified_row(cr))
    print()
    print(format_classification_summary(classified))
