from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from scheduling.ai_advisor import Recommendation
from scheduling.models import Workload


def export_simulation_pdf(workload: Workload, recommendation: Recommendation, destination: str | Path) -> Path:
    """Create a compact, shareable local report for the current simulation."""
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path), pagesize=A4)
    _, height = A4
    y = height - 54
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(48, y, "OSInsight-AI: Disk Scheduling Report")
    y -= 30
    pdf.setFont("Helvetica", 10)
    lines = [
        f"Disk geometry: {workload.cylinders} cylinders | Initial head: {workload.head} | Direction: {workload.direction}",
        f"Queue: {', '.join(str(item.cylinder) for item in workload.requests)}",
        f"AI recommendation: {recommendation.algorithm} ({recommendation.confidence:.1f}% confidence)",
        recommendation.explanation,
        "",
        "Algorithm       Total seek    Avg seek    Fairness    Avg wait",
    ]
    for result in recommendation.candidates:
        lines.append(f"{result.algorithm:<14} {result.total_seek:<13} {result.average_seek:<11.2f} {result.fairness:<11.3f} {result.turnaround_estimate:.2f}")
    for line in lines:
        pdf.drawString(48, y, line[:115])
        y -= 18
    pdf.save()
    return path
