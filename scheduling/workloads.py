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

    def generate_localized(
        self,
        count: int = 16,
        disk_size: int = 200,
        cluster_center: int | None = None,
        cluster_std: float = 15.0,
        head: int | None = None,
        direction: str = "up",
    ) -> Workload:
        """Generate requests exhibiting high spatial locality clustered around a cylinder hotspot."""
        h = head if head is not None else self.rng.randint(0, disk_size - 1)
        center = cluster_center if cluster_center is not None else self.rng.randint(int(disk_size * 0.2), int(disk_size * 0.8))
        cylinders = [
            max(0, min(disk_size - 1, int(self.rng.gauss(center, cluster_std))))
            for _ in range(count)
        ]
        return Workload.from_cylinders(cylinders, head=h, disk_size=disk_size, direction=direction)

    def generate_sequential(
        self,
        count: int = 16,
        disk_size: int = 200,
        start: int | None = None,
        stride: int = 2,
        head: int | None = None,
        direction: str = "up",
    ) -> Workload:
        """Generate contiguous or strided sequential requests typical of file streaming/logging."""
        h = head if head is not None else self.rng.randint(0, disk_size - 1)
        base = start if start is not None else self.rng.randint(0, max(1, disk_size - (count * stride)))
        cylinders = [(base + i * stride) % disk_size for i in range(count)]
        return Workload.from_cylinders(cylinders, head=h, disk_size=disk_size, direction=direction)
