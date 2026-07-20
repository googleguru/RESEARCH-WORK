"""Generate paper-style result tables from experiment CSV logs."""

import csv
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))


def load_rows(path: str):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def summarize(rows, metric: str):
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["benchmark_name"], row["algorithm"], row["seed"])].append(float(row[metric]))
    return grouped


def write_quality_table(rows, out_path: str):
    by_benchmark = defaultdict(list)
    for row in rows:
        by_benchmark[row["benchmark_name"]].append(row)

    lines = []
    lines.append("\\begin{table}[t]")
    lines.append("\\centering")
    lines.append("\\caption{Representative quality results from the synthetic benchmark harness.}")
    lines.append("\\label{tab:quality}")
    lines.append("\\begin{tabular}{lrr}")
    lines.append("\\toprule")
    lines.append("Benchmark & HPWL & Overflow \\")
    lines.append("\\midrule")
    for benchmark in sorted(by_benchmark):
        bench_rows = by_benchmark[benchmark]
        hpwl = sum(float(r["hpwl"]) for r in bench_rows) / max(1, len(bench_rows))
        ov = sum(float(r["density_overflow"]) for r in bench_rows) / max(1, len(bench_rows))
        lines.append(f"{benchmark} & {hpwl:.2f} & {ov:.2f} \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def main():
    input_path = "experiments_demo/experiments.csv"
    if not os.path.exists(input_path):
        print("No experiment log found; run python run_experiment_suite.py first.")
        return
    rows = load_rows(input_path)
    out_dir = "docs"
    os.makedirs(out_dir, exist_ok=True)
    write_quality_table(rows, os.path.join(out_dir, "quality_table.tex"))
    print(f"Wrote {os.path.join(out_dir, 'quality_table.tex')}")


if __name__ == "__main__":
    main()
