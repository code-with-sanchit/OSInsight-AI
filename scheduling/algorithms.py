from __future__ import annotations

from collections.abc import Callable
from statistics import pstdev

from .models import ScheduleResult, Workload

ALGORITHMS = ("FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK")


def compute_travel_waits(service_order: list[int], path: list[int]) -> list[float]:
    """Compute seek distance elapsed before each request in service_order is reached."""
    travelled, path_index = 0, 0
    waits: list[float] = []
    for target in service_order:
        waits.append(float(travelled))
        while path_index < len(path) - 1:
            travelled += abs(path[path_index + 1] - path[path_index])
            path_index += 1
            if path[path_index] == target:
                break
    return waits


def compute_jains_fairness(waits: list[float]) -> float:
    """Calculate Jain's fairness index over individual request wait values."""
    if not waits:
        return 1.0
    squared_sum = sum(wait * wait for wait in waits)
    if squared_sum == 0:
        return 1.0
    return (sum(waits) ** 2) / (len(waits) * squared_sum)


def _result(name: str, workload: Workload, service_order: list[int], path: list[int]) -> ScheduleResult:
    seek_steps = [abs(right - left) for left, right in zip(path, path[1:])]
    total_seek = sum(seek_steps)
    waits = compute_travel_waits(service_order, path)
    fairness = compute_jains_fairness(waits)
    stddev = round(pstdev(seek_steps), 2) if len(seek_steps) > 1 else 0.0
    maximum_wait = round(max(waits), 2) if waits else 0.0
    return ScheduleResult(
        algorithm=name,
        service_order=tuple(service_order),
        path=tuple(path),
        total_seek=total_seek,
        average_seek=round(total_seek / len(service_order), 2),
        fairness=round(fairness, 3),
        turnaround_estimate=round(sum(waits) / len(waits), 2) if waits else 0.0,
        seek_stddev=stddev,
        max_wait=maximum_wait,
    )


def _fcfs(workload: Workload) -> tuple[list[int], list[int]]:
    order = [request.cylinder for request in workload.requests]
    return order, [workload.head, *order]


def _sstf(workload: Workload) -> tuple[list[int], list[int]]:
    remaining = [request.cylinder for request in workload.requests]
    current, order = workload.head, []
    while remaining:
        target = min(remaining, key=lambda cylinder: (abs(cylinder - current), cylinder))
        remaining.remove(target)
        order.append(target)
        current = target
    return order, [workload.head, *order]


def _sweep(workload: Workload, *, circular: bool, look: bool) -> tuple[list[int], list[int]]:
    values = sorted(request.cylinder for request in workload.requests)
    lower = [value for value in values if value < workload.head]
    upper = [value for value in values if value >= workload.head]
    moving_up = workload.direction == "up"
    first, second = (upper, lower[::-1]) if moving_up else (lower[::-1], upper)
    order = first + second
    path = [workload.head, *first]
    if second:
        if circular:
            edge, restart = (workload.cylinders - 1, 0) if moving_up else (0, workload.cylinders - 1)
            if not look:
                path.append(edge)
            path.append(restart)
        elif not look:
            path.append(workload.cylinders - 1 if moving_up else 0)
        path.extend(second)
    return order, path


def _n_step_scan(workload: Workload, step_size: int = 4) -> tuple[list[int], list[int]]:
    """Segment queue into groups of size N and service each segment using SCAN."""
    all_requests = [req.cylinder for req in workload.requests]
    current_head = workload.head
    overall_order: list[int] = []
    overall_path: list[int] = [current_head]

    for i in range(0, len(all_requests), step_size):
        chunk = all_requests[i : i + step_size]
        lower = sorted(c for c in chunk if c < current_head)
        upper = sorted(c for c in chunk if c >= current_head)
        moving_up = workload.direction == "up"
        first, second = (upper, lower[::-1]) if moving_up else (lower[::-1], upper)
        batch_order = first + second
        for cylinder in batch_order:
            overall_order.append(cylinder)
            overall_path.append(cylinder)
        if batch_order:
            current_head = batch_order[-1]

    return overall_order, overall_path


def _f_scan(workload: Workload) -> tuple[list[int], list[int]]:
    """F-SCAN: Two queues; freezes active queue while servicing, then processes deferred queue."""
    all_requests = [req.cylinder for req in workload.requests]
    if len(all_requests) <= 2:
        return _sweep(workload, circular=False, look=True)

    mid = max(1, len(all_requests) // 2)
    q1 = all_requests[:mid]
    q2 = all_requests[mid:]

    current_head = workload.head
    overall_order: list[int] = []
    overall_path: list[int] = [current_head]

    for q in (q1, q2):
        lower = sorted(c for c in q if c < current_head)
        upper = sorted(c for c in q if c >= current_head)
        moving_up = workload.direction == "up"
        first, second = (upper, lower[::-1]) if moving_up else (lower[::-1], upper)
        batch = first + second
        for c in batch:
            overall_order.append(c)
            overall_path.append(c)
        if batch:
            current_head = batch[-1]

    return overall_order, overall_path


def run_algorithm(name: str, workload: Workload) -> ScheduleResult:
    """Run a deterministic scheduling policy against one immutable workload."""
    normalized = name.upper()
    runners: dict[str, Callable[[Workload], tuple[list[int], list[int]]]] = {
        "FCFS": _fcfs,
        "SSTF": _sstf,
        "SCAN": lambda item: _sweep(item, circular=False, look=False),
        "C-SCAN": lambda item: _sweep(item, circular=True, look=False),
        "LOOK": lambda item: _sweep(item, circular=False, look=True),
        "C-LOOK": lambda item: _sweep(item, circular=True, look=True),
    }
    if normalized not in runners:
        raise ValueError(f"Unknown algorithm: {name}. Choose one of {', '.join(ALGORITHMS)}.")
    order, path = runners[normalized](workload)
    return _result(normalized, workload, order, path)
