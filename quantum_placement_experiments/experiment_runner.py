"""Utilities for running reproducible placement experiments and logging metrics."""

import csv
import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

from quantum_placement_config import QuantumPlacerConfig
from quantum_vlsi_placer import QuantumVLSIPlacer
from ispd2019_benchmark import ISPD2019Evaluator, SyntheticISPD2019


@dataclass
class ExperimentResult:
    benchmark_name: str
    algorithm: str
    seed: int
    hpwl: float
    density_overflow: float
    avg_displacement: float
    runtime_seconds: float
    bits_per_dim: int
    refinement_iterations: int


class ExperimentRunner:
    """Run placement experiments and emit structured CSV/JSON output."""

    def __init__(self, output_dir: str = "experiments"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run_experiment(self, benchmark_name: str = "ispd2019_test1",
                       algorithm: str = "qaoa",
                       seed: int = 42,
                       num_cells: int | None = None,
                       bits_per_dim: int = 3,
                       refinement_iterations: int = 3) -> ExperimentResult:
        gen = SyntheticISPD2019(seed=seed)
        netlist, die_w, die_h, init_pl = gen.generate(
            benchmark_name, num_cells=num_cells)

        cfg = QuantumPlacerConfig(
            algorithm=algorithm,
            bits_per_dim=bits_per_dim,
            qaoa_depth=2,
            vqe_depth=3,
            qa_sweeps=200,
            refinement_iterations=refinement_iterations,
        )

        start = time.time()
        placer = QuantumVLSIPlacer(netlist, die_w, die_h, cfg, seed=seed)
        placement = placer.run()
        runtime_seconds = time.time() - start

        evaluator = ISPD2019Evaluator(netlist, die_w, die_h)
        metrics = evaluator.evaluate(placement, ref=init_pl)

        result = ExperimentResult(
            benchmark_name=benchmark_name,
            algorithm=algorithm,
            seed=seed,
            hpwl=float(metrics["hpwl"]),
            density_overflow=float(metrics["density_overflow"]),
            avg_displacement=float(metrics.get("avg_displacement", 0.0)),
            runtime_seconds=float(runtime_seconds),
            bits_per_dim=bits_per_dim,
            refinement_iterations=refinement_iterations,
        )

        self._write_outputs(result)
        return result

    def _write_outputs(self, result: ExperimentResult) -> None:
        row = asdict(result)
        csv_path = os.path.join(self.output_dir, "experiments.csv")
        write_header = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
            if write_header:
                writer.writeheader()
            writer.writerow(row)

        json_path = os.path.join(self.output_dir, "latest_experiment.json")
        with open(json_path, "w") as fh:
            json.dump(row, fh, indent=2)
