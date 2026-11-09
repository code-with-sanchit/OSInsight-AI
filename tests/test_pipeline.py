from pathlib import Path
import tempfile

from scheduling.ai_advisor import AIAdvisor
from scheduling.models import Workload
from scheduling.visualizer import DiskVisualizer
from scheduling.workloads import WorkloadGenerator, WorkloadPattern
from utils.reporting import export_simulation_pdf


def test_end_to_end_simulation_pipeline() -> None:
    # 1. Generate workload
    gen = WorkloadGenerator(seed=999)
    wl = gen.generate(WorkloadPattern.DATABASE_OLTP, count=16, disk_size=200, head=50)
    assert wl.request_count == 16

    # 2. Run AI Advisor
    advisor = AIAdvisor()
    rec = advisor.recommend(wl, preference="Balanced")
    assert rec.algorithm in [c.algorithm for c in rec.candidates]
    assert len(rec.candidates) == 8

    # 3. Render Visualizations
    steps_render = DiskVisualizer.render_path_steps(rec.candidates[0], disk_size=200)
    assert len(steps_render) > 0
    cmap_render = DiskVisualizer.render_cylinder_map(wl)
    assert "Cylinder Map" in cmap_render
    bars_render = DiskVisualizer.render_comparison_bars(list(rec.candidates))
    assert "Total Seek Comparison" in bars_render

    # 4. Export PDF Report
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = Path(tmp_dir) / "test_report.pdf"
        saved = export_simulation_pdf(wl, rec, pdf_path)
        assert saved.exists()
        assert saved.stat().st_size > 500
