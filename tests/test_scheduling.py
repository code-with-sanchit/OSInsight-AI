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
