from __future__ import annotations

import random
from enum import Enum

from .models import Workload


class WorkloadPattern(str, Enum):
    """Standard storage workload patterns encountered in operating systems."""

    UNIFORM = "uniform"
    LOCALIZED = "localized"
    SEQUENTIAL = "sequential"
    DATABASE_OLTP = "database_oltp"
    PING_PONG = "ping_pong"


class WorkloadGenerator:
    """Configurable generator producing realistic synthetic disk access workloads."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
