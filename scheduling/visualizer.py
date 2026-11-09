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
