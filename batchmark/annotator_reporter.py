"""Console reporter for annotated benchmark results."""

from typing import List

from batchmark.annotator import AnnotatedResult

_COL_SIZE = 10
_COL_DUR = 12
_COL_STATUS = 8
_COL_ANN = 30


def format_annotated_header() -> str:
    return (
        f"{'Size':>{_COL_SIZE}}  "
        f"{'Duration(ms)':>{_COL_DUR}}  "
        f"{'Status':<{_COL_STATUS}}  "
        f"{'Annotations':<{_COL_ANN}}"
    )


def _fmt_annotations(ann: dict) -> str:
    if not ann:
        return "(none)"
    return ", ".join(f"{k}={v}" for k, v in sorted(ann.items()))


def format_annotated_row(ar: AnnotatedResult) -> str:
    status = "OK" if ar.success else "FAIL"
    dur_ms = ar.duration * 1_000
    return (
        f"{ar.size:>{_COL_SIZE}}  "
        f"{dur_ms:>{_COL_DUR}.2f}  "
        f"{status:<{_COL_STATUS}}  "
        f"{_fmt_annotations(ar.annotations):<{_COL_ANN}}"
    )


def format_annotated_summary(results: List[AnnotatedResult]) -> str:
    total = len(results)
    ok = sum(1 for r in results if r.success)
    all_keys: set = set()
    for r in results:
        all_keys.update(r.annotations.keys())
    key_list = ", ".join(sorted(all_keys)) if all_keys else "(none)"
    return (
        f"Total: {total}  OK: {ok}  Failed: {total - ok}  "
        f"Annotation keys: {key_list}"
    )


def print_annotated_report(results: List[AnnotatedResult]) -> None:
    print(format_annotated_header())
    print("-" * (_COL_SIZE + _COL_DUR + _COL_STATUS + _COL_ANN + 6))
    for ar in results:
        print(format_annotated_row(ar))
    print()
    print(format_annotated_summary(results))
