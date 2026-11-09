# OSInsight-AI — Advanced Disk Scheduling Simulator

OSInsight-AI is a polished, local-first simulator for studying disk-arm scheduling and I/O optimization. It compares eight classic and modern operating-system policies on the same queue and uses an explainable AI decision layer to recommend the most appropriate policy for the selected goal.

## Key Features

- **8 Scheduling Algorithms**: Implements FCFS, SSTF, SCAN, C-SCAN, LOOK, C-LOOK, N-Step-SCAN, and F-SCAN with deterministic, reproducible behavior.
- **Explainable AI Policy Selector**: Profiles queue locality, spread, and directional bias, then ranks policies against Performance, Fairness, or Balanced objectives.
- **Multi-Metric Evaluation**: Compares total head movement, average seek, estimated average wait, maximum wait (starvation indicator), seek standard deviation, throughput, and Jain's fairness index.
- **5 Synthetic Workload Generators**: Uniform random, Localized cluster, Sequential streaming, Database OLTP (clustered writes + WAL flushes), and Ping-Pong worst-case stress test.
- **Dual Interface Modes**:
  - **Desktop GUI**: Interactive CustomTkinter dashboard with real-time head path visualization, cylinder map, and workload generator.
  - **Headless CLI**: Full-featured terminal runner with ASCII platter trajectory charts and automated multi-workload benchmark suite.
- **Lab & Viva Artifacts**: Generates compact PDF reports with ReportLab for academic lab assessments.

## Quick Start

### 1. Desktop GUI

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### 2. Headless CLI

Run all algorithms against a custom queue:
```powershell
python -m scheduling.cli --requests "98,183,37,122,14,124,65,67" --head 53 --cylinders 200 --visualize
```

Run comprehensive empirical benchmark across all 5 workload patterns:
```powershell
python -m scheduling.cli --benchmark
```

## AI Recommendation Model

The AI layer is deliberately explainable rather than an opaque black box. It extracts workload spread (locality), executes every valid policy, normalizes their seek cost, wait times, and starvation risk, then computes an interpretable multi-objective score:

$$\text{Score} = w_{\text{seek}} \cdot \left(1 - \frac{\text{Seek}}{\text{MaxSeek}}\right) + w_{\text{fair}} \cdot \text{Fairness} + w_{\text{lat}} \cdot \left(1 - \frac{\text{Wait}}{\text{MaxWait}}\right) + w_{\text{starv}} \cdot \left(1 - \frac{\text{MaxWait}}{\text{WorstWait}}\right)$$

This allows students to defend and reproduce the recommendation during examinations.

## Project Structure

```text
scheduling/          Core algorithms, workload models, AI advisor, visualizer, and CLI
gui/                 CustomTkinter interactive simulator dashboard
utils/               ReportLab PDF exporter
tests/               Automated test suite (pytest)
documentation/       Theory, viva study guide, benchmarks, and architecture guides
```

## Documentation & Viva Resources

- [Algorithm Theory & Complexity Matrix](file:///documentation/ALGORITHMS.md)
- [Benchmark Methodology & Workload Profiles](file:///documentation/BENCHMARKS.md)
- [OS Lab Viva & Oral Examination Study Guide](file:///documentation/VIVA_QUESTIONS.md)
- [Project Architecture Diagram](file:///diagrams/disk_scheduler_architecture.mmd)

## Verification

```powershell
python -m pytest -q
```

## Technology Stack

Python 3.12+, CustomTkinter, ReportLab, and pytest. The simulator runs entirely locally and never uploads request data.
