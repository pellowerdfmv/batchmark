"""Reporter for outlier detection results."""

from typing import List, Optional
from batchmark.outlier import OutlierResult


def _fmt_ms(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value * 1000:.2f}ms"


def _status(result: OutlierResult) -> str:
    if not result.success:
        return "FAIL"
    if result.is_outlier:
        return "OUTLIER"
    return "ok"


def format_outlier_header() -> str:
    return f"{'Size':>10}  {'Duration':>12}  {'Lower Fence':>14}  {'Upper Fence':>14}  {'Status':>10}"


def format_outlier_row(result: OutlierResult) -> str:
    return (
        f"{result.size:>10}  "
        f"{_fmt_ms(result.duration):>12}  "
        f"{_fmt_ms(result.lower_fence):>14}  "
        f"{_fmt_ms(result.upper_fence):>14}  "
        f"{_status(result):>10}"
    )


def format_outlier_summary(results: List[OutlierResult]) -> str:
    total = len(results)
    outliers = sum(1 for r in results if r.is_outlier)
    failures = sum(1 for r in results if not r.success)
    return (
        f"Total: {total}  Outliers: {outliers}  Failures: {failures}  "
        f"Clean: {total - outliers - failures}"
    )


def print_outlier_report(results: List[OutlierResult]) -> None:
    print(format_outlier_header())
    print("-" * 68)
    for r in results:
        print(format_outlier_row(r))
    print("-" * 68)
    print(format_outlier_summary(results))
