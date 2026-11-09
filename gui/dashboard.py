from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from scheduling.ai_advisor import AIAdvisor
from scheduling.algorithms import run_algorithm
from scheduling.models import Workload
from scheduling.workloads import WorkloadGenerator, WorkloadPattern
from utils.reporting import export_simulation_pdf


class Dashboard(ctk.CTk):
    """Interactive, local-first disk scheduling lab."""

    def __init__(self) -> None:
        super().__init__()
        self.title("OSInsight-AI | Advanced Disk Scheduling Simulator")
        self.geometry("1180x760")
        self.minsize(1000, 660)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.advisor = AIAdvisor()
        self._build()
        self.generate_workload()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="OSInsight-AI", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(20, 0))
        ctk.CTkLabel(self, text="Advanced Disk Scheduling Simulator · Explainable AI policy selection", text_color="#9CA3AF").pack(pady=(0, 14))
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(0, 18))
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        controls = ctk.CTkFrame(content, width=310)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        controls.grid_propagate(False)
        ctk.CTkLabel(controls, text="Workload controls", font=ctk.CTkFont(size=19, weight="bold")).pack(anchor="w", padx=20, pady=(20, 14))
        self.head = self._entry(controls, "Initial head", "53")
        self.disk_size = self._entry(controls, "Disk cylinders", "200")
        self.requests = self._entry(controls, "Request queue (comma-separated)", "98, 183, 37, 122, 14, 124, 65, 67")
        self.direction = ctk.CTkSegmentedButton(controls, values=["up", "down"])
        ctk.CTkLabel(controls, text="Sweep direction").pack(anchor="w", padx=20, pady=(10, 2))
        self.direction.set("up")
        self.direction.pack(fill="x", padx=20)
        self.preference = ctk.CTkOptionMenu(controls, values=["Balanced", "Performance", "Fairness"])
        ctk.CTkLabel(controls, text="AI objective").pack(anchor="w", padx=20, pady=(12, 2))
        self.preference.pack(fill="x", padx=20)
        self.pattern_menu = ctk.CTkOptionMenu(
            controls,
            values=["Realistic Mixed", "Uniform", "Localized", "Sequential", "Database OLTP", "Ping-Pong"],
        )
        ctk.CTkLabel(controls, text="Workload pattern").pack(anchor="w", padx=20, pady=(8, 2))
        self.pattern_menu.pack(fill="x", padx=20)
        ctk.CTkButton(controls, text="Run AI recommendation", command=self.run_simulation).pack(fill="x", padx=20, pady=(16, 6))
        ctk.CTkButton(controls, text="Generate workload", fg_color="#334155", command=self.generate_workload).pack(fill="x", padx=20, pady=4)
        ctk.CTkButton(controls, text="Export simulation report", fg_color="#334155", command=self.export_report).pack(fill="x", padx=20, pady=4)

        workspace = ctk.CTkFrame(content)
        workspace.grid(row=0, column=1, sticky="nsew")
        self.recommendation = ctk.CTkLabel(workspace, text="Preparing simulation...", justify="left", anchor="w", font=ctk.CTkFont(size=16, weight="bold"))
        self.recommendation.pack(fill="x", padx=22, pady=(20, 5))
        self.insights = ctk.CTkLabel(workspace, text="", text_color="#94A3B8", anchor="w")
        self.insights.pack(fill="x", padx=22, pady=(0, 14))
        self.table = tk.Text(workspace, height=19, bg="#111827", fg="#E5E7EB", insertbackground="white", relief="flat", font=("Cascadia Mono", 11), padx=14, pady=14)
        self.table.pack(fill="both", expand=True, padx=22, pady=(0, 12))
        self.path = ctk.CTkLabel(workspace, text="", justify="left", wraplength=760, anchor="w", text_color="#CBD5E1")
        self.path.pack(fill="x", padx=22, pady=(0, 18))

    def _entry(self, parent: ctk.CTkFrame, label: str, value: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label).pack(anchor="w", padx=20, pady=(10, 2))
        entry = ctk.CTkEntry(parent)
        entry.insert(0, value)
        entry.pack(fill="x", padx=20)
        return entry

    def _read_workload(self) -> Workload:
        disk_size = int(self.disk_size.get())
        values = [int(part.strip()) for part in self.requests.get().split(",") if part.strip()]
        return Workload.from_cylinders(values, head=int(self.head.get()), disk_size=disk_size, direction=self.direction.get())

    def generate_workload(self) -> None:
        disk_size = int(self.disk_size.get()) if self.disk_size.get().isdigit() else 200
        pattern_choice = self.pattern_menu.get()
        gen = WorkloadGenerator()

        pattern_mapping = {
            "Uniform": WorkloadPattern.UNIFORM,
            "Localized": WorkloadPattern.LOCALIZED,
            "Sequential": WorkloadPattern.SEQUENTIAL,
            "Database OLTP": WorkloadPattern.DATABASE_OLTP,
            "Ping-Pong": WorkloadPattern.PING_PONG,
        }

        if pattern_choice in pattern_mapping:
            wl = gen.generate(pattern_mapping[pattern_choice], count=16, disk_size=disk_size)
            head = wl.head
            queue = [req.cylinder for req in wl.requests]
        else:
            head = random.randint(60, 140)
            center = random.randint(35, 165)
            queue = [max(0, min(disk_size - 1, int(random.gauss(center, 20)))) for _ in range(14)]
            queue += [random.randrange(disk_size) for _ in range(4)]

        for entry, value in ((self.head, str(head)), (self.disk_size, str(disk_size)), (self.requests, ", ".join(map(str, queue)))):
            entry.delete(0, "end")
            entry.insert(0, value)
        self.run_simulation()

    def run_simulation(self) -> None:
        try:
            workload = self._read_workload()
            recommendation = self.advisor.recommend(workload, self.preference.get())
        except ValueError as error:
            messagebox.showerror("Check the workload", str(error))
            return
        self.current_workload, self.current_recommendation = workload, recommendation
        selected = run_algorithm(recommendation.algorithm, workload)
        self.recommendation.configure(text=f"AI recommends {recommendation.algorithm}  ·  {recommendation.confidence:.1f}% confidence\n{recommendation.explanation}")
        self.insights.configure(text=self.advisor.workload_insights(workload))
        self.table.delete("1.0", "end")
        header = f"{'ALGORITHM':<12} {'TOTAL SEEK':>10} {'AVG SEEK':>9} {'FAIRNESS':>9} {'AVG WAIT':>9} {'MAX WAIT':>9} {'STD DEV':>8} {'THROUGHPUT':>11}\n"
        self.table.insert("end", header)
        self.table.insert("end", "─" * (len(header) - 1) + "\n")
        for result in recommendation.candidates:
            marker = " ← AI choice" if result.algorithm == recommendation.algorithm else ""
            row = f"{result.algorithm:<12} {result.total_seek:>10} {result.average_seek:>9.2f} {result.fairness:>9.3f} {result.turnaround_estimate:>9.2f} {result.max_wait:>9.2f} {result.seek_stddev:>8.2f} {result.throughput:>11.4f}{marker}\n"
            self.table.insert("end", row)
        self.path.configure(text=f"Selected service path: {' → '.join(map(str, selected.path))}")

    def export_report(self) -> None:
        if not hasattr(self, "current_recommendation"):
            return
        path = export_simulation_pdf(self.current_workload, self.current_recommendation, "reports/disk_scheduling_report.pdf")
        messagebox.showinfo("Export complete", f"Saved {path}")
