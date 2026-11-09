# OSInsight-AI — Advanced Disk Scheduling Simulator

OSInsight-AI is a polished, local-first simulator for studying disk-arm scheduling. It compares classic operating-system policies on the same queue and uses an explainable AI decision layer to recommend the most appropriate policy for the selected goal.

## What makes it advanced

- Implements FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK with deterministic, testable behavior.
- Simulates configurable disk geometry, starting head, queue, and sweep direction.
- Compares total head movement, average seek, estimated average wait, throughput, and Jain's fairness index.
- Includes an explainable AI selector that profiles queue locality and ranks policies against performance, fairness, or balanced objectives.
- Generates realistic mixed I/O queues: a local workload cluster plus long-distance outliers.
- Exports a compact PDF simulation report for lab records and viva demonstrations.

## Quick start

```powershell
git clone https://github.com/code-with-sanchit/OSInsight-AI.git
cd OSInsight-AI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Enter a comma-separated request queue, select an objective, and choose **Run AI recommendation**. The dashboard shows the ranking of every algorithm and the selected head path.

## AI recommendation model

The AI layer is deliberately explainable rather than a black box. It derives workload spread (locality), runs every valid policy, normalizes their seek cost and wait estimate, then applies a transparent weighted score:

```text
score = objective_seek_weight × efficiency
      + objective_fairness_weight × Jain_fairness
      + objective_latency_weight × low_latency
```

This lets students understand and defend the recommendation: it is a multi-objective policy selector, not an unsupported claim that an opaque model "knows best."

## Layout

```text
scheduling/        Algorithms, workload models, and explainable AI advisor
gui/               CustomTkinter simulator dashboard
utils/             PDF export
tests/             Algorithm and AI recommendation tests
documentation/     Architecture and experiment guide
```

## Verification

```powershell
python -m pytest -q
```

## Technology

Python 3.12+, CustomTkinter, ReportLab, and pytest. The simulator runs entirely locally and never uploads request data.
