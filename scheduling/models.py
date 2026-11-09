from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DiskRequest:
    """A single logical block request in a simulated disk queue."""

    cylinder: int
    arrival: float = 0.0
    priority: int = 0

    def __post_init__(self) -> None:
        if self.cylinder < 0:
            raise ValueError(f"Cylinder index must be non-negative, got {self.cylinder}.")
        if self.arrival < 0:
            raise ValueError(f"Arrival time cannot be negative, got {self.arrival}.")

    @classmethod
    def from_sequence(cls, cylinders: Iterable[int]) -> tuple["DiskRequest", ...]:
        """Convert an iterable of integer cylinder indices into a tuple of DiskRequests."""
        return tuple(cls(int(cylinder)) for cylinder in cylinders)


@dataclass(frozen=True)
class Workload:
    requests: tuple[DiskRequest, ...]
    head: int
    cylinders: int
    direction: str = "up"

    def __post_init__(self) -> None:
        if self.cylinders < 2:
            raise ValueError("A disk needs at least two cylinders.")
        if not 0 <= self.head < self.cylinders:
            raise ValueError("Head position is outside the disk geometry.")
        if self.direction not in {"up", "down"}:
            raise ValueError("Direction must be 'up' or 'down'.")
        if not self.requests:
            raise ValueError("Add at least one request.")
        if any(not 0 <= request.cylinder < self.cylinders for request in self.requests):
            raise ValueError("Every request must be inside the disk geometry.")

    @classmethod
    def from_cylinders(
        cls, cylinders: Iterable[int], *, head: int, disk_size: int, direction: str = "up"
    ) -> "Workload":
        return cls(tuple(DiskRequest(int(value)) for value in cylinders), head, disk_size, direction)


@dataclass(frozen=True)
class ScheduleResult:
    algorithm: str
    service_order: tuple[int, ...]
    path: tuple[int, ...]
    total_seek: int
    average_seek: float
    fairness: float
    turnaround_estimate: float

    @property
    def throughput(self) -> float:
        return len(self.service_order) / max(self.total_seek, 1)
