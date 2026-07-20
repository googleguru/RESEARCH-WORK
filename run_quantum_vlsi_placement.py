"""
run_quantum_vlsi_placement.py — Entry point for Quantum VLSI Placement.

Usage:
  # Run with a synthetic, ISPD-inspired benchmark (default):
  python run_quantum_vlsi_placement.py

  # Run with user-provided Bookshelf benchmark files:
  python run_quantum_vlsi_placement.py --benchmark_dir /path/to/ispd2019 \
                                        --name ispd2019_test1 \
                                        --algorithm qaoa

  # Algorithm choices: qaoa | vqe | quantum_annealing
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from quantum_placement_config import QuantumPlacerConfig
from quantum_vlsi_placer import QuantumVLSIPlacer
from ispd2019_benchmark import (
    ISPD2019BenchmarkLoader,
    ISPD2019Evaluator,
    SyntheticISPD2019,
)


def parse_args():
    p = argparse.ArgumentParser(description="Quantum VLSI Placement (synthetic or user-supplied benchmarks)")
    p.add_argument("--benchmark_dir", default=None,
                   help="Optional directory that contains Bookshelf benchmark files")
    p.add_argument("--name", default="ispd2019_test1")
    p.add_argument("--algorithm", default="qaoa",
                   choices=["qaoa", "vqe", "quantum_annealing"])
    p.add_argument("--bits_per_dim", type=int, default=3)
    p.add_argument("--qaoa_depth", type=int, default=2)
    p.add_argument("--vqe_depth", type=int, default=3)
    p.add_argument("--qa_sweeps", type=int, default=200)
    p.add_argument("--refinement_iterations", type=int, default=3)
    p.add_argument("--num_cells", type=int, default=None,
                   help="Override cell count for synthetic benchmarks")
    p.add_argument("--seed", type=int, default=42,
                   help="Random seed for reproducible runs")
    return p.parse_args()


def main():
    args = parse_args()

    # ---- Load benchmark ----
    if args.benchmark_dir and os.path.isdir(args.benchmark_dir):
        print(f"Loading benchmark files from {args.benchmark_dir}: {args.name}")
        try:
            netlist, die_w, die_h, init_pl = ISPD2019BenchmarkLoader.load(
                args.benchmark_dir, args.name)
        except FileNotFoundError as exc:
            print(f"  {exc}")
            print("Falling back to a synthetic, ISPD-inspired benchmark.")
            gen = SyntheticISPD2019(seed=args.seed)
            netlist, die_w, die_h, init_pl = gen.generate(
                args.name, num_cells=args.num_cells)
    else:
        print(f"Generating synthetic, ISPD-inspired benchmark: {args.name}")
        gen = SyntheticISPD2019(seed=args.seed)
        netlist, die_w, die_h, init_pl = gen.generate(
            args.name, num_cells=args.num_cells)

    # ---- Configure ----
    cfg = QuantumPlacerConfig(
        algorithm=args.algorithm,
        bits_per_dim=args.bits_per_dim,
        qaoa_depth=args.qaoa_depth,
        vqe_depth=args.vqe_depth,
        qa_sweeps=args.qa_sweeps,
        refinement_iterations=args.refinement_iterations,
    )

    # ---- Place ----
    placer = QuantumVLSIPlacer(netlist, die_w, die_h, cfg, seed=args.seed)
    final_placement = placer.run()

    # ---- Evaluate ----
    evaluator = ISPD2019Evaluator(netlist, die_w, die_h)
    evaluator.print_report(final_placement, ref=init_pl)


if __name__ == "__main__":
    main()
