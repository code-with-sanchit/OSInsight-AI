import pytest

from scheduling.ai_advisor import AIAdvisor
from scheduling.algorithms import ALGORITHMS, run_algorithm
from scheduling.models import Workload


def workload() -> Workload:
    return Workload.from_cylinders([98, 183, 37, 122, 14, 124, 65, 67], head=53, disk_size=200)


def test_every_algorithm_services_every_request() -> None:
    for algorithm in ALGORITHMS:
        result = run_algorithm(algorithm, workload())
        assert sorted(result.service_order) == sorted(request.cylinder for request in workload().requests)
        assert result.total_seek >= 0


def test_sstf_outperforms_fcfs_for_known_workload() -> None:
    assert run_algorithm("SSTF", workload()).total_seek < run_algorithm("FCFS", workload()).total_seek


def test_ai_recommendation_is_explainable() -> None:
    recommendation = AIAdvisor().recommend(workload(), "Balanced")
    assert recommendation.algorithm in ALGORITHMS
    assert 0 < recommendation.confidence <= 100
    assert "fairness" in recommendation.explanation


def test_metrics_max_wait_and_variance() -> None:
    res = run_algorithm("FCFS", workload())
    assert res.max_wait >= res.turnaround_estimate
    assert res.seek_stddev >= 0.0
    assert res.wait_ratio >= 1.0


def test_compute_travel_waits_and_fairness() -> None:
    from scheduling.algorithms import compute_jains_fairness, compute_travel_waits

    waits = compute_travel_waits([10, 20], [0, 10, 20])
    assert waits == [0.0, 10.0]
    fairness = compute_jains_fairness([10.0, 10.0, 10.0])
    assert pytest.approx(fairness, 0.01) == 1.0


def test_n_step_scan_chunking() -> None:
    wl = Workload.from_cylinders([10, 90, 20, 80, 30, 70], head=50, disk_size=100, direction="up")
    res = run_algorithm("N-STEP-SCAN", wl)
    assert len(res.service_order) == 6
    assert set(res.service_order) == {10, 90, 20, 80, 30, 70}
    # First chunk [10, 90, 20, 80]: from 50 moving up -> 80, 90 then 20, 10
    first_chunk_serviced = res.service_order[:4]
    assert first_chunk_serviced == (80, 90, 20, 10)


def test_f_scan_two_stage_execution() -> None:
    wl = Workload.from_cylinders([10, 90, 20, 80], head=50, disk_size=100, direction="up")
    res = run_algorithm("F-SCAN", wl)
    assert len(res.service_order) == 4
    # Queue 1 is [10, 90]: from 50 moving up -> 90 then 10
    assert res.service_order[:2] == (90, 10)
    # Queue 2 is [20, 80]: from 10 moving up -> 20, 80
    assert res.service_order[2:] == (20, 80)


def test_custom_profile_and_classifier() -> None:
    advisor = AIAdvisor()
    advisor.register_profile("ThroughputFocus", seek_w=0.8, fairness_w=0.05, latency_w=0.1, starvation_w=0.05)
    rec = advisor.recommend(workload(), preference="ThroughputFocus")
    assert rec.algorithm in ALGORITHMS

    classification = AIAdvisor.classify_workload(workload())
    assert "locality" in classification
    assert "direction_bias" in classification
    assert classification["mean_cylinder"] > 0

    with pytest.raises(ValueError, match="Total weights must sum to a positive value"):
        advisor.register_profile("Bad", 0, 0, 0, 0)
