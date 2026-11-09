import pytest
from scheduling.workloads import WorkloadGenerator, WorkloadPattern


def test_generator_uniform() -> None:
    gen = WorkloadGenerator(seed=42)
    wl = gen.generate_uniform(count=20, disk_size=200, head=50)
    assert wl.request_count == 20
    assert wl.head == 50
    assert wl.cylinders == 200
    assert all(0 <= c < 200 for c in wl.cylinder_values)


def test_generator_localized() -> None:
    gen = WorkloadGenerator(seed=42)
    wl = gen.generate_localized(count=25, disk_size=300, cluster_center=150, cluster_std=10.0, head=100)
    assert wl.request_count == 25
    assert wl.head == 100
    # Mean should be close to cluster_center
    mean_val = sum(wl.cylinder_values) / len(wl.cylinder_values)
    assert abs(mean_val - 150) < 15


def test_generator_sequential() -> None:
    gen = WorkloadGenerator(seed=42)
    wl = gen.generate_sequential(count=10, disk_size=200, start=30, stride=5, head=20)
    assert wl.cylinder_values == tuple(range(30, 80, 5))


def test_generator_database_oltp() -> None:
    gen = WorkloadGenerator(seed=42)
    wl = gen.generate_database_oltp(count=20, disk_size=200, head=60)
    assert wl.request_count == 20
    assert wl.head == 60


def test_generator_ping_pong() -> None:
    gen = WorkloadGenerator(seed=42)
    wl = gen.generate_ping_pong(count=12, disk_size=200, head=100)
    assert wl.request_count == 12
    # Even requests should be low cylinder, odd high cylinder
    low_reqs = [wl.cylinder_values[i] for i in range(0, 12, 2)]
    high_reqs = [wl.cylinder_values[i] for i in range(1, 12, 2)]
    assert max(low_reqs) < min(high_reqs)


def test_generator_dispatch() -> None:
    gen = WorkloadGenerator(seed=42)
    for pattern in WorkloadPattern:
        wl = gen.generate(pattern, count=15, disk_size=200)
        assert wl.request_count == 15

    with pytest.raises(ValueError, match="Unknown workload pattern"):
        gen.generate("invalid_pattern")
