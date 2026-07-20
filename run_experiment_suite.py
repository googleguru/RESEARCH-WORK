"""Run a small batch of experiments and write CSV/JSON logs for analysis."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from quantum_placement_experiments import ExperimentRunner


def parse_args():
    p = argparse.ArgumentParser(description="Run reproducible placement experiments")
    p.add_argument("--output_dir", default="experiments", help="Where to store logs")
    p.add_argument("--benchmark", default="ispd2019_test1")
    p.add_argument("--algorithm", default="qaoa", choices=["qaoa", "vqe", "quantum_annealing"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--num_cells", type=int, default=None)
    p.add_argument("--bits_per_dim", type=int, default=3)
    p.add_argument("--refinement_iterations", type=int, default=3)
    return p.parse_args()


def main():
    args = parse_args()
    runner = ExperimentRunner(output_dir=args.output_dir)
    result = runner.run_experiment(
        benchmark_name=args.benchmark,
        algorithm=args.algorithm,
        seed=args.seed,
        num_cells=args.num_cells,
        bits_per_dim=args.bits_per_dim,
        refinement_iterations=args.refinement_iterations,
    )
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    import json
    main()
