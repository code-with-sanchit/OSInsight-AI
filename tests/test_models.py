import pytest
from scheduling.models import DiskRequest, Workload


def test_disk_request_valid() -> None:
    req = DiskRequest(cylinder=42, arrival=1.5, priority=2)
    assert req.cylinder == 42
    assert req.arrival == 1.5
    assert req.priority == 2


def test_disk_request_negative_cylinder_raises() -> None:
    with pytest.raises(ValueError, match="Cylinder index must be non-negative"):
        DiskRequest(cylinder=-1)


def test_disk_request_negative_arrival_raises() -> None:
    with pytest.raises(ValueError, match="Arrival time cannot be negative"):
        DiskRequest(cylinder=10, arrival=-0.5)


def test_disk_request_from_sequence() -> None:
    requests = DiskRequest.from_sequence([10, 20, 30])
    assert len(requests) == 3
    assert tuple(r.cylinder for r in requests) == (10, 20, 30)


def test_workload_validation_errors() -> None:
    # Insufficient cylinders
    with pytest.raises(ValueError, match="A disk needs at least two cylinders"):
        Workload(requests=(DiskRequest(0),), head=0, cylinders=1)

    # Head out of range
    with pytest.raises(ValueError, match="Head position is outside the disk geometry"):
        Workload(requests=(DiskRequest(0),), head=200, cylinders=200)

    # Empty requests
    with pytest.raises(ValueError, match="Add at least one request"):
        Workload(requests=(), head=50, cylinders=200)

    # Request cylinder outside geometry
    with pytest.raises(ValueError, match="Every request must be inside"):
        Workload(requests=(DiskRequest(205),), head=50, cylinders=200)

    # Invalid direction
    with pytest.raises(ValueError, match="Direction must be 'up' or 'down'"):
        Workload.from_cylinders([10, 20], head=50, disk_size=200, direction="sideways")


def test_workload_properties() -> None:
    wl = Workload.from_cylinders([15, 80, 45, 120], head=50, disk_size=200)
    assert wl.cylinder_values == (15, 80, 45, 120)
    assert wl.min_cylinder == 15
    assert wl.max_cylinder == 120
    assert wl.request_count == 4
    assert wl.span == 105
    assert wl.nearest_request_distance == 5  # abs(50 - 45)
    assert wl.contains_cylinder(80) is True
    assert wl.contains_cylinder(99) is False
