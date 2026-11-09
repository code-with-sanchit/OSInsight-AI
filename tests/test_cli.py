import io
import sys
from scheduling.cli import build_parser, format_results_table, main
from scheduling.algorithms import run_algorithm
from scheduling.models import Workload


def test_cli_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args([])
    assert args.head == 53
    assert args.cylinders == 200
    assert args.direction == "up"
    assert args.algorithm == "ALL"
    assert args.objective == "Balanced"


def test_cli_format_results_table() -> None:
    wl = Workload.from_cylinders([10, 50, 90], head=20, disk_size=100)
    res = [run_algorithm("FCFS", wl), run_algorithm("SSTF", wl)]
    table = format_results_table(res, recommended="SSTF")
    assert "FCFS" in table
    assert "SSTF" in table
    assert "[AI Choice]" in table


def test_cli_main_execution() -> None:
    code = main(["--requests", "20,40,60", "--head", "30", "--cylinders", "100", "--algorithm", "FCFS"])
    assert code == 0


def test_cli_main_pattern_and_visualize() -> None:
    code = main(["--pattern", "sequential", "--count", "8", "--cylinders", "100", "--visualize"])
    assert code == 0


def test_cli_main_benchmark() -> None:
    code = main(["--benchmark", "--cylinders", "100", "--count", "8"])
    assert code == 0
