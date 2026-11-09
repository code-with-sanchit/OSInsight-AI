from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .ai_advisor import AIAdvisor
from .algorithms import ALGORITHMS, run_algorithm
from .models import ScheduleResult, Workload
from .visualizer import DiskVisualizer
from .workloads import WorkloadGenerator, WorkloadPattern


def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser for headless simulation."""
    parser = argparse.ArgumentParser(
        prog="osinsight",
        description="OSInsight-AI: Advanced Disk Scheduling Simulator and Explainable AI Policy Selector",
    )
    parser.add_argument(
        "-r", "--requests",
        type=str,
        default="98,183,37,122,14,124,65,67",
        help="Comma-separated list of cylinder requests (e.g. '98,183,37,122')",
    )
    parser.add_argument(
        "-H", "--head",
        type=int,
        default=53,
        help="Starting disk head cylinder position (default: 53)",
    )
    parser.add_argument(
        "-c", "--cylinders",
        type=int,
        default=200,
        help="Total number of cylinders in the disk geometry (default: 200)",
    )
    parser.add_argument(
        "-d", "--direction",
        type=str,
        choices=["up", "down"],
        default="up",
        help="Initial sweep direction for directional algorithms (default: up)",
    )
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        default="ALL",
        help=f"Algorithm to run or 'ALL' to compare all policies (valid: {', '.join(ALGORITHMS)})",
    )
    parser.add_argument(
        "-o", "--objective",
        type=str,
        choices=["Balanced", "Performance", "Fairness"],
        default="Balanced",
        help="Explainable AI advisor target objective (default: Balanced)",
    )
    parser.add_argument(
        "-p", "--pattern",
        type=str,
        choices=[p.value for p in WorkloadPattern],
        default=None,
        help="Optional synthetic workload pattern generator to use instead of static queue",
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=16,
        help="Number of requests to generate when --pattern is specified (default: 16)",
    )
    parser.add_argument(
        "-v", "--visualize",
        action="store_true",
        help="Render ASCII trajectory steps and track map in output",
    )
    return parser


def format_results_table(results: Sequence[ScheduleResult], recommended: str | None = None) -> str:
    """Format simulation results into a clean terminal table."""
    header = f"{'ALGORITHM':<12} {'TOTAL SEEK':>10} {'AVG SEEK':>9} {'FAIRNESS':>9} {'AVG WAIT':>9} {'MAX WAIT':>9} {'STD DEV':>8} {'THROUGHPUT':>11}"
    lines = ["=" * len(header), header, "-" * len(header)]
    for r in results:
        marker = " <-- [AI Choice]" if r.algorithm == recommended else ""
        row = f"{r.algorithm:<12} {r.total_seek:>10} {r.average_seek:>9.2f} {r.fairness:>9.3f} {r.turnaround_estimate:>9.2f} {r.max_wait:>9.2f} {r.seek_stddev:>8.2f} {r.throughput:>11.4f}{marker}"
        lines.append(row)
    lines.append("=" * len(header))
    return "\n".join(lines)
