from __future__ import annotations

from collections.abc import Callable

from .models import ScheduleResult, Workload

ALGORITHMS = ("FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK")


def _result(name: str, workload: Workload, service_order: list[int], path: list[int]) -> ScheduleResult:
    seek_steps = [abs(right - left) for left, right in zip(path, path[1:])]
    total_seek = sum(seek_steps)
    # Per-request wait is movement completed before its service. The service path can
    # contain a sweep boundary or circular wrap, so map each request to its actual stop.
    travelled, path_index = 0, 0
    waits: list[float] = []
    for target in service_order:
        waits.append(travelled)
        while path_index < len(path) - 1:
            travelled += abs(path[path_index + 1] - path[path_index])
            path_index += 1
            if path[path_index] == target:
                break
    squared_sum = sum(wait * wait for wait in waits)
    fairness = (sum(waits) ** 2) / (len(waits) * squared_sum) if squared_sum else 1.0
    return ScheduleResult(
        algorithm=name,
        service_order=tuple(service_order),
        path=tuple(path),
        total_seek=total_seek,
        average_seek=round(total_seek / len(service_order), 2),
        fairness=round(fairness, 3),
        turnaround_estimate=round(sum(waits) / len(waits), 2) if waits else 0.0,
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
