from scheduling.algorithms import run_algorithm
from scheduling.models import Workload
from scheduling.visualizer import DiskVisualizer


def test_visualizer_render_path_steps() -> None:
    wl = Workload.from_cylinders([10, 50, 90], head=20, disk_size=100)
    res = run_algorithm("FCFS", wl)
    chart = DiskVisualizer.render_path_steps(res, disk_size=100, width=30)
    assert "FCFS Head Trajectory" in chart
    assert "Total Seek:" in chart
    assert "Step  0" in chart
    assert "[HEAD]" in chart


def test_visualizer_render_cylinder_map() -> None:
    wl = Workload.from_cylinders([10, 50, 90], head=20, disk_size=100)
    cmap = DiskVisualizer.render_cylinder_map(wl, width=30)
    assert "[0]|" in cmap
    assert "|[99]" in cmap
    assert "H" in cmap
    assert "x" in cmap


def test_visualizer_render_comparison_bars() -> None:
    wl = Workload.from_cylinders([10, 50, 90], head=20, disk_size=100)
    r1 = run_algorithm("FCFS", wl)
    r2 = run_algorithm("SSTF", wl)
    bars = DiskVisualizer.render_comparison_bars([r1, r2], width=20)
    assert "=== Total Seek Comparison" in bars
    assert "FCFS" in bars
    assert "SSTF" in bars
