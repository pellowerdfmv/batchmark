"""Annotate timing results with arbitrary key-value metadata."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class AnnotatedResult:
    """A TimingResult decorated with a metadata dictionary."""

    result: TimingResult
    annotations: Dict[str, Any] = field(default_factory=dict)

    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> float:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


@dataclass
class AnnotateConfig:
    """Rules for annotating results.

    ``static`` annotations are applied to every result.
    ``size_annotations`` maps an input size to extra key-value pairs that
    are merged on top of the static ones.
    """

    static: Dict[str, Any] = field(default_factory=dict)
    size_annotations: Dict[int, Dict[str, Any]] = field(default_factory=dict)


def annotate_results(
    results: List[TimingResult],
    config: Optional[AnnotateConfig] = None,
) -> List[AnnotatedResult]:
    """Return a list of AnnotatedResult wrapping each TimingResult.

    Annotations are built by merging *static* entries with any per-size
    overrides defined in *config*.  When *config* is ``None`` every result
    receives an empty annotation dict.
    """
    if config is None:
        config = AnnotateConfig()

    annotated: List[AnnotatedResult] = []
    for r in results:
        ann: Dict[str, Any] = dict(config.static)
        if r.size in config.size_annotations:
            ann.update(config.size_annotations[r.size])
        annotated.append(AnnotatedResult(result=r, annotations=ann))
    return annotated


def get_annotation(ar: AnnotatedResult, key: str, default: Any = None) -> Any:
    """Retrieve a single annotation value by key."""
    return ar.annotations.get(key, default)
