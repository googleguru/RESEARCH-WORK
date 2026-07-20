"""
generate_ispd2019_visualization.py
===================================
Runs Quantum VLSI Placement on a synthetic, ISPD-inspired benchmark and produces
DREAMPlace-style visualizations:

  docs/circuit_layout.gif          ← Cell layout animation (per iteration)
  docs/density_map.gif             ← Bin-density animation
  docs/qubo_energy.gif             ← QUBO energy landscape animation
  docs/quantum_gradient.gif        ← Quantum gradient field animation
  docs/quantum_placement_animation.gif  ← Combined 4-panel animation
  docs/quantum_placement_result.png     ← Final combined 4-panel snapshot

Usage
-----
  python generate_ispd2019_visualization.py

  # Larger benchmark:
  python generate_ispd2019_visualization.py --num_cells 200 --algorithm quantum_annealing

  # Optional user-provided Bookshelf files:
  python generate_ispd2019_visualization.py \
      --benchmark_dir /path/to/ispd2019 --name ispd2019_test1
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from quantum_placement_config import QuantumPlacerConfig
from quantum_vlsi_placer import QuantumVLSIPlacer
from ispd2019_benchmark import (
    ISPD2019BenchmarkLoader,
    ISPD2019Evaluator,
    SyntheticISPD2019,
)


def parse_args():
    p = argparse.ArgumentParser(
        description="Quantum VLSI Placement — synthetic or user-supplied benchmark visualization")
    p.add_argument("--benchmark_dir", default=None,
                   help="Optional directory with Bookshelf benchmark files")
    p.add_argument("--name", default="ispd2019_test1")
    p.add_argument("--algorithm", default="quantum_annealing",
                   choices=["qaoa", "vqe", "quantum_annealing"])
    p.add_argument("--num_cells", type=int, default=150,
                   help="Synthetic benchmark cell count")
    p.add_argument("--bits_per_dim", type=int, default=3)
    p.add_argument("--qaoa_depth", type=int, default=2)
    p.add_argument("--vqe_depth", type=int, default=3)
    p.add_argument("--qa_sweeps", type=int, default=300)
    p.add_argument("--refinement_iterations", type=int, default=5)
    p.add_argument("--out_dir", default="docs")
    p.add_argument("--seed", type=int, default=42,
                   help="Random seed for reproducible runs")
    return p.parse_args()


def main():
    args = parse_args()

    # ---- Load / generate benchmark ----
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
        print(f"Generating synthetic, ISPD-inspired benchmark: {args.name} "
              f"({args.num_cells} cells)")
        gen = SyntheticISPD2019(seed=args.seed)
        netlist, die_w, die_h, init_pl = gen.generate(
            args.name, num_cells=args.num_cells)

    print(f"  Cells: {netlist.cell_count}   Nets: {netlist.net_count}   "
          f"Die: {die_w:.1f} × {die_h:.1f}")

    # ---- Configure ----
    cfg = QuantumPlacerConfig(
        algorithm=args.algorithm,
        bits_per_dim=args.bits_per_dim,
        qaoa_depth=args.qaoa_depth,
        vqe_depth=args.vqe_depth,
        qa_sweeps=args.qa_sweeps,
        refinement_iterations=args.refinement_iterations,
        wl_weight=1.0,
        density_weight=8.0,
    )

    # ---- Run placement with visualization ----
    placer = QuantumVLSIPlacer(
        netlist, die_w, die_h, cfg,
        visualize=True,
        out_dir=args.out_dir,
        seed=args.seed,
    )
    final_pl = placer.run()

    # ---- Evaluate ----
    evaluator = ISPD2019Evaluator(netlist, die_w, die_h)
    evaluator.print_report(final_pl, ref=init_pl)

    print(f"\nVisualization files written to: {os.path.abspath(args.out_dir)}/")
    for fname in [
        "quantum_placement_result.png",
        "quantum_placement_animation.gif",
        "circuit_layout.gif",
        "density_map.gif",
        "qubo_energy.gif",
        "quantum_gradient.gif",
    ]:
        path = os.path.join(args.out_dir, fname)
        if os.path.exists(path):
            size_kb = os.path.getsize(path) // 1024
            print(f"  {fname:<40s} {size_kb:>6} KB")


if __name__ == "__main__":
    main()
