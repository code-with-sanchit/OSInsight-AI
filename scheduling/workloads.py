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

    def generate_uniform(
        self,
        count: int = 16,
        disk_size: int = 200,
        head: int | None = None,
        direction: str = "up",
    ) -> Workload:
        """Generate requests drawn uniformly across the entire disk geometry."""
        h = head if head is not None else self.rng.randint(0, disk_size - 1)
        cylinders = [self.rng.randint(0, disk_size - 1) for _ in range(count)]
        return Workload.from_cylinders(cylinders, head=h, disk_size=disk_size, direction=direction)
