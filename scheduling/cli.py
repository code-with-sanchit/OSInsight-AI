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
    return parser
