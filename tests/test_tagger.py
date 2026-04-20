"""Tests for batchmark.tagger."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.tagger import (
    TagConfig,
    TaggedResult,
    filter_by_tag,
    tag_results,
    unique_tag_values,
)


def _r(size: int, duration: float = 1.0, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, stdout="", stderr="")


# ---------------------------------------------------------------------------
# tag_results
# ---------------------------------------------------------------------------

def test_tag_results_applies_size_tags():
    results = [_r(10), _r(20)]
    config = TagConfig(
        size_tags={10: {"env": "small"}, 20: {"env": "large"}},
    )
    tagged = tag_results(results, config)
    assert tagged[0].tags == {"env": "small"}
    assert tagged[1].tags == {"env": "large"}


def test_tag_results_uses_default_for_unknown_size():
    results = [_r(99)]
    config = TagConfig(
        size_tags={10: {"env": "small"}},
        default_tags={"env": "unknown"},
    )
    tagged = tag_results(results, config)
    assert tagged[0].tags == {"env": "unknown"}


def test_tag_results_empty_input():
    tagged = tag_results([], TagConfig())
    assert tagged == []


def test_tag_results_preserves_result_reference():
    r = _r(10)
    config = TagConfig(size_tags={10: {"x": "1"}})
    tagged = tag_results([r], config)
    assert tagged[0].result is r


def test_tag_results_copies_tag_dict():
    """Mutating the returned tags must not affect the config."""
    config = TagConfig(size_tags={10: {"env": "small"}})
    tagged = tag_results([_r(10)], config)
    tagged[0].tags["extra"] = "yes"
    assert "extra" not in config.size_tags[10]


# ---------------------------------------------------------------------------
# TaggedResult convenience properties
# ---------------------------------------------------------------------------

def test_tagged_result_size_passthrough():
    t = TaggedResult(result=_r(42))
    assert t.size == 42


def test_tagged_result_duration_passthrough():
    t = TaggedResult(result=_r(10, duration=3.14))
    assert t.duration == 3.14


def test_tagged_result_success_true():
    t = TaggedResult(result=_r(10, returncode=0))
    assert t.success is True


def test_tagged_result_success_false():
    t = TaggedResult(result=_r(10, returncode=1))
    assert t.success is False


# ---------------------------------------------------------------------------
# filter_by_tag
# ---------------------------------------------------------------------------

def test_filter_by_tag_keeps_matching():
    config = TagConfig(size_tags={10: {"env": "ci"}, 20: {"env": "local"}})
    tagged = tag_results([_r(10), _r(20)], config)
    result = filter_by_tag(tagged, "env", "ci")
    assert len(result) == 1
    assert result[0].size == 10


def test_filter_by_tag_no_match_returns_empty():
    config = TagConfig(default_tags={"env": "local"})
    tagged = tag_results([_r(10)], config)
    assert filter_by_tag(tagged, "env", "ci") == []


def test_filter_by_tag_missing_key_excluded():
    tagged = [TaggedResult(result=_r(10), tags={})]
    assert filter_by_tag(tagged, "env", "ci") == []


# ---------------------------------------------------------------------------
# unique_tag_values
# ---------------------------------------------------------------------------

def test_unique_tag_values_returns_sorted():
    tagged = [
        TaggedResult(result=_r(10), tags={"env": "ci"}),
        TaggedResult(result=_r(20), tags={"env": "local"}),
        TaggedResult(result=_r(30), tags={"env": "ci"}),
    ]
    assert unique_tag_values(tagged, "env") == ["ci", "local"]


def test_unique_tag_values_missing_key_ignored():
    tagged = [
        TaggedResult(result=_r(10), tags={"env": "ci"}),
        TaggedResult(result=_r(20), tags={}),
    ]
    assert unique_tag_values(tagged, "env") == ["ci"]


def test_unique_tag_values_empty_list():
    assert unique_tag_values([], "env") == []
