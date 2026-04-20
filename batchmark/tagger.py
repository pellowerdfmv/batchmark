"""Tag timing results with arbitrary key-value metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class TaggedResult:
    """A TimingResult decorated with a metadata tag dictionary."""

    result: TimingResult
    tags: Dict[str, str] = field(default_factory=dict)

    # Convenience pass-throughs so callers can treat TaggedResult like TimingResult.
    @property
    def size(self) -> int:
        return self.result.size

    @property
    def duration(self) -> Optional[float]:
        return self.result.duration

    @property
    def success(self) -> bool:
        return self.result.returncode == 0


@dataclass
class TagConfig:
    """Mapping from size (int) to a tag dictionary."""

    size_tags: Dict[int, Dict[str, str]] = field(default_factory=dict)
    default_tags: Dict[str, str] = field(default_factory=dict)


def tag_results(
    results: List[TimingResult],
    config: TagConfig,
) -> List[TaggedResult]:
    """Return a TaggedResult for every TimingResult in *results*.

    Tags are resolved by looking up ``result.size`` in *config.size_tags*;
    if no entry exists the *config.default_tags* dict is used instead.
    The resolved dict is **copied** so mutations do not affect the config.
    """
    tagged: List[TaggedResult] = []
    for result in results:
        tags = dict(
            config.size_tags.get(result.size, config.default_tags)
        )
        tagged.append(TaggedResult(result=result, tags=tags))
    return tagged


def filter_by_tag(
    tagged: List[TaggedResult],
    key: str,
    value: str,
) -> List[TaggedResult]:
    """Return only those TaggedResults whose tags[key] == value."""
    return [t for t in tagged if t.tags.get(key) == value]


def unique_tag_values(
    tagged: List[TaggedResult],
    key: str,
) -> List[str]:
    """Return sorted unique values for *key* across all tagged results."""
    return sorted({t.tags[key] for t in tagged if key in t.tags})
