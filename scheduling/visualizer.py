from __future__ import annotations

from .models import ScheduleResult, Workload


class DiskVisualizer:
    """ASCII and Unicode visualizer for disk head arm movements and track maps."""

    @staticmethod
    def render_path_steps(result: ScheduleResult, disk_size: int = 200, width: int = 50) -> str:
        """Render step-by-step head movement across simulated disk platters."""
        lines: list[str] = [
            f"=== {result.algorithm} Head Trajectory (Disk size: {disk_size} cylinders) ===",
            f"Total Seek: {result.total_seek} | Avg Seek: {result.average_seek:.2f} | Fairness: {result.fairness:.3f}",
            "-" * (width + 24),
        ]
        for step, cylinder in enumerate(result.path):
            pos = int((cylinder / max(1, disk_size - 1)) * (width - 1))
            bar = [" "] * width
            bar[pos] = "H" if step == 0 else "*"
            bar_str = "".join(bar)
            tag = " [HEAD]" if step == 0 else f" (req {cylinder})"
            lines.append(f"Step {step:>2} [cyl {cylinder:>3}]: |{bar_str}|{tag}")
        lines.append("-" * (width + 24))
        return "\n".join(lines)

    @staticmethod
    def render_cylinder_map(workload: Workload, width: int = 50) -> str:
        """Render a single-line snapshot showing head position and requested cylinders."""
        grid = ["-"] * width
        for req in workload.requests:
            p = int((req.cylinder / max(1, workload.cylinders - 1)) * (width - 1))
            grid[p] = "x"
        head_p = int((workload.head / max(1, workload.cylinders - 1)) * (width - 1))
        grid[head_p] = "H"
        return f"Cylinder Map: [0]|{''.join(grid)}|[{workload.cylinders - 1}]  (H=head, x=request)"

    @staticmethod
    def render_comparison_bars(results: list[ScheduleResult], width: int = 35) -> str:
        """Render an ASCII bar chart comparing total seek distance across algorithms."""
        if not results:
            return ""
        max_seek = max(r.total_seek for r in results) or 1
        lines = ["=== Total Seek Comparison (shorter is better) ==="]
        for r in sorted(results, key=lambda x: x.total_seek):
            bar_len = int((r.total_seek / max_seek) * width)
            bar = "#" * max(1, bar_len)
            lines.append(f"{r.algorithm:<11} | {bar:<{width}} | {r.total_seek:>4} cyls (fairness: {r.fairness:.3f})")
        return "\n".join(lines)
