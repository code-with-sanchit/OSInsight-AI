# Development Guide

## Environment Setup

1. Create a Python 3.12+ virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install development dependencies:
   ```powershell
   pip install -r requirements-dev.txt
   ```
3. Run the automated test suite:
   ```powershell
   python -m pytest -q
   ```

## Architectural Guidelines

- **Separation of Concerns**: Keep disk scheduling algorithms and AI advisor logic cleanly decoupled from user-interface (CustomTkinter) and reporting code.
- **Determinism**: Every scheduling policy must be completely deterministic for identical inputs.
- **Data Immutability**: All request and workload models use frozen dataclasses to eliminate accidental side effects during path computation.
- **Test Coverage**: Any new scheduling policy, workload generator, or AI decision rule must include unit tests verifying request completeness and invariant preservation.
