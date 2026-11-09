from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean, pstdev

from .algorithms import ALGORITHMS, run_algorithm
from .models import ScheduleResult, Workload


@dataclass(frozen=True)
class Recommendation:
    algorithm: str
    confidence: float
    explanation: str
    candidates: tuple[ScheduleResult, ...]


class AIAdvisor:
    """Explainable multi-objective policy selector.

    It extracts workload locality and queue balance, evaluates each algorithm, then
    ranks policies using seek cost, fairness and latency. This is intentionally
    transparent: every recommendation can be reproduced from the displayed scores.
    """

    DEFAULT_PROFILES: dict[str, tuple[float, float, float, float]] = {
        "Performance": (0.60, 0.10, 0.20, 0.10),
        "Fairness": (0.20, 0.50, 0.15, 0.15),
        "Balanced": (0.40, 0.25, 0.20, 0.15),
    }

    def __init__(self, profiles: dict[str, tuple[float, float, float, float]] | None = None) -> None:
        self.profiles = dict(self.DEFAULT_PROFILES)
        if profiles:
            self.profiles.update(profiles)

    def register_profile(
        self, name: str, seek_w: float, fairness_w: float, latency_w: float, starvation_w: float
    ) -> None:
        """Register or override a custom multi-objective weighting profile."""
        total = seek_w + fairness_w + latency_w + starvation_w
        if total <= 0:
            raise ValueError("Total weights must sum to a positive value.")
        normalized = (seek_w / total, fairness_w / total, latency_w / total, starvation_w / total)
        self.profiles[name.title()] = normalized

    def recommend(self, workload: Workload, preference: str = "Balanced") -> Recommendation:
        candidates = tuple(run_algorithm(name, workload) for name in ALGORITHMS)
        preference_title = preference.title()
        seek_weight, fairness_weight, latency_weight, starvation_weight = self.profiles.get(
            preference_title, self.DEFAULT_PROFILES["Balanced"]
        )
        max_seek = max(result.total_seek for result in candidates) or 1
        max_latency = max(result.turnaround_estimate for result in candidates) or 1
        max_wait_all = max(result.max_wait for result in candidates) or 1

        def score(result: ScheduleResult) -> float:
            return (
                seek_weight * (1 - result.total_seek / max_seek)
                + fairness_weight * result.fairness
                + latency_weight * (1 - result.turnaround_estimate / max_latency)
                + starvation_weight * (1 - result.max_wait / max_wait_all)
            )

        ranked = sorted(candidates, key=lambda item: (score(item), item.fairness), reverse=True)
        winner, runner_up = ranked[0], ranked[1]
        positions = [request.cylinder for request in workload.requests]
        spread = pstdev(positions) if len(positions) > 1 else 0
        locality = "high locality" if spread < workload.cylinders * 0.18 else "a widely spread queue"
        margin = score(winner) - score(runner_up)
        confidence = min(0.97, 0.56 + margin * 2.4 + len(positions) / 250)
        explanation = (
            f"Detected {locality}. For {preference.lower()} mode, {winner.algorithm} minimizes the "
            f"combined seek/latency cost while retaining a fairness score of {winner.fairness:.3f}."
        )
        return Recommendation(winner.algorithm, round(confidence * 100, 1), explanation, tuple(ranked))

    @staticmethod
    def workload_insights(workload: Workload) -> str:
        positions = [request.cylinder for request in workload.requests]
        return (
            f"{len(positions)} requests | mean cylinder {fmean(positions):.1f} | "
            f"spread {pstdev(positions) if len(positions) > 1 else 0:.1f} | head {workload.head}"
        )

    @classmethod
    def classify_workload(cls, workload: Workload) -> dict[str, str | float | bool]:
        """Profile workload geometry, spatial distribution, and clustering characteristics."""
        positions = [req.cylinder for req in workload.requests]
        mean_pos = fmean(positions)
        spread = pstdev(positions) if len(positions) > 1 else 0.0
        normalized_spread = spread / workload.cylinders

        if normalized_spread < 0.12:
            locality_label = "Highly Clustered"
        elif normalized_spread < 0.25:
            locality_label = "Moderately Clustered"
        else:
            locality_label = "Uniform / Dispersed"

        mid = workload.cylinders / 2
        direction_bias = "Upper Disk" if mean_pos > mid * 1.15 else ("Lower Disk" if mean_pos < mid * 0.85 else "Centered")
        outliers = any(abs(pos - mean_pos) > 2.0 * max(spread, 1.0) for pos in positions)

        return {
            "locality": locality_label,
            "direction_bias": direction_bias,
            "mean_cylinder": round(mean_pos, 1),
            "spread": round(spread, 2),
            "normalized_spread": round(normalized_spread, 3),
            "has_outliers": outliers,
        }
