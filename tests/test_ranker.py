"""Tests for batchmark.ranker."""

from __future__ import annotations

from batchmark.aggregator import AggregatedResult
from batchmark.ranker import RankedResult, _tier, rank_results, format_ranked


def _agg(
    size: int,
    mean: float | None = 100.0,
    successful: int = 3,
    runs: int = 3,
) -> AggregatedResult:
    return AggregatedResult(
        size=size,
        runs=runs,
        successful=successful,
        mean=mean,
        median=mean,
        stdev=0.0,
        min_duration=mean,
        max_duration=mean,
    )


# ---------------------------------------------------------------------------
# _tier
# ---------------------------------------------------------------------------

def test_tier_only_one_result():
    assert _tier(1, 1) == "fast"


def test_tier_first_of_three_is_fast():
    assert _tier(1, 3) == "fast"


def test_tier_middle_of_three_is_medium():
    assert _tier(2, 3) == "medium"


def test_tier_last_of_three_is_slow():
    assert _tier(3, 3) == "slow"


# ---------------------------------------------------------------------------
# rank_results
# ---------------------------------------------------------------------------

def test_rank_results_returns_one_per_input():
    aggs = [_agg(100, 200.0), _agg(200, 100.0), _agg(300, 150.0)]
    ranked = rank_results(aggs)
    assert len(ranked) == 3


def test_rank_results_sorted_by_mean_ascending():
    aggs = [_agg(100, 300.0), _agg(200, 100.0), _agg(300, 200.0)]
    ranked = rank_results(aggs)
    assert [r.size for r in ranked] == [200, 300, 100]


def test_rank_results_rank_numbers_start_at_one():
    aggs = [_agg(100, 50.0), _agg(200, 80.0)]
    ranked = rank_results(aggs)
    assert ranked[0].rank == 1
    assert ranked[1].rank == 2


def test_rank_results_none_mean_placed_last():
    aggs = [_agg(100, None, successful=0), _agg(200, 50.0)]
    ranked = rank_results(aggs)
    assert ranked[-1].size == 100
    assert ranked[-1].tier == "slow"


def test_rank_results_empty_input():
    assert rank_results([]) == []


def test_rank_results_tier_assigned():
    aggs = [_agg(i * 100, float(i * 50)) for i in range(1, 4)]
    ranked = rank_results(aggs)
    tiers = [r.tier for r in ranked]
    assert "fast" in tiers
    assert "slow" in tiers


# ---------------------------------------------------------------------------
# format_ranked
# ---------------------------------------------------------------------------

def test_format_ranked_contains_size():
    ranked = rank_results([_agg(512, 120.5)])
    output = format_ranked(ranked)
    assert "512" in output


def test_format_ranked_contains_mean():
    ranked = rank_results([_agg(512, 120.5)])
    output = format_ranked(ranked)
    assert "120.50" in output


def test_format_ranked_na_for_no_mean():
    ranked = rank_results([_agg(512, None, successful=0)])
    output = format_ranked(ranked)
    assert "N/A" in output
