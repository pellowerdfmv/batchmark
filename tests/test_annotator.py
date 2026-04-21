"""Tests for batchmark.annotator."""

from batchmark.annotator import (
    AnnotateConfig,
    AnnotatedResult,
    annotate_results,
    get_annotation,
)
from batchmark.timer import TimingResult


def _r(size: int, duration: float = 0.1, returncode: int = 0) -> TimingResult:
    return TimingResult(size=size, duration=duration, returncode=returncode, output="")


def test_annotate_results_empty_input():
    assert annotate_results([]) == []


def test_annotate_results_no_config_gives_empty_annotations():
    results = [_r(100), _r(200)]
    annotated = annotate_results(results)
    assert all(ar.annotations == {} for ar in annotated)


def test_annotate_results_static_applied_to_all():
    config = AnnotateConfig(static={"env": "ci", "version": "1.0"})
    annotated = annotate_results([_r(100), _r(200)], config)
    for ar in annotated:
        assert ar.annotations["env"] == "ci"
        assert ar.annotations["version"] == "1.0"


def test_annotate_results_size_override_merges():
    config = AnnotateConfig(
        static={"env": "ci"},
        size_annotations={200: {"note": "large", "env": "staging"}},
    )
    annotated = annotate_results([_r(100), _r(200)], config)
    small = next(a for a in annotated if a.size == 100)
    large = next(a for a in annotated if a.size == 200)
    assert small.annotations == {"env": "ci"}
    assert large.annotations == {"env": "staging", "note": "large"}


def test_annotate_results_preserves_result_reference():
    r = _r(100)
    annotated = annotate_results([r])
    assert annotated[0].result is r


def test_annotated_result_size_and_duration_delegate():
    r = _r(512, duration=0.25)
    ar = AnnotatedResult(result=r, annotations={})
    assert ar.size == 512
    assert ar.duration == 0.25


def test_annotated_result_success_true_for_zero_returncode():
    ar = AnnotatedResult(result=_r(100, returncode=0), annotations={})
    assert ar.success is True


def test_annotated_result_success_false_for_nonzero_returncode():
    ar = AnnotatedResult(result=_r(100, returncode=1), annotations={})
    assert ar.success is False


def test_get_annotation_returns_value():
    ar = AnnotatedResult(result=_r(100), annotations={"tier": "gold"})
    assert get_annotation(ar, "tier") == "gold"


def test_get_annotation_returns_default_for_missing_key():
    ar = AnnotatedResult(result=_r(100), annotations={})
    assert get_annotation(ar, "missing", default="n/a") == "n/a"


def test_get_annotation_none_default_when_not_provided():
    ar = AnnotatedResult(result=_r(100), annotations={})
    assert get_annotation(ar, "missing") is None
