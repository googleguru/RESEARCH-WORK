#!/usr/bin/env python3
"""Quantum VLSI Placement - Expert Implementation

Features:
  - Quantum algorithms (QAOA, VQE) for placement optimization
  - QUBO formulation from placement constraints
  - ISPD 2019 benchmark support
  - Hybrid quantum-classical refinement
  - First iteration optimization flow
"""

from benchmarks import CircuitGenerator
from benchmarks.ispd2019 import ISPD2019Loader
from quantum_placement.qubo_formulation import PlacementQUBO
from quantum_placement.qaoa import QAOAPlacementOptimizer
from quantum_placement.vqe import VQEPlacementSolver
from quantum_placement.hybrid_optimizer import HybridPlacementOptimizer
from classical_solver import SimulatedAnnealingSolver
from placement_core.legalization import Legalizer
from placement_core.metrics import PlacementMetrics
from config import PlacementConfig


def run_quantum_example():
    """Run quantum placement on synthetic circuit."""
    config = PlacementConfig()
    config.die_width = 300.0
    config.die_height = 300.0

    # Generate test circuit
    netlist = CircuitGenerator.generate_random_circuit(
        num_cells=16, num_nets=40, avg_fanout=3, seed=42)

    print("\n" + "="*70)
    print("QUANTUM VLSI PLACEMENT - FIRST ITERATION")
    print("="*70)
    print(f"Circuit: {netlist.get_cell_count()} cells, {netlist.get_net_count()} nets")

    # QUBO formulation
    qubo_form = PlacementQUBO(netlist, config.die_width, config.die_height,
                             grid_cells=4)
    qubo_form.build_qubo(wl_weight=1.0, overlap_weight=5.0)
    print(f"QUBO: {qubo_form.get_qubit_count()} qubits, "
          f"{len(qubo_form.qubo)} terms")

    # QAOA optimization
    print("\n[QAOA] Depth=2, Iterations=30")
    qaoa = QAOAPlacementOptimizer(qubo_form, depth=2)
    qaoa_place, _, _ = qaoa.optimize(max_iterations=30)

    # VQE optimization
    print("[VQE] Ansatz Depth=2, Iterations=30")
    vqe = VQEPlacementSolver(qubo_form, ansatz_depth=2)
    vqe_place, _, _ = vqe.solve(max_iterations=30)

    # Legalize
    legalizer = Legalizer(grid_unit=config.grid_unit)
    qaoa_legal = legalizer.legalize(qaoa_place, netlist,
                                   config.die_width, config.die_height)
    vqe_legal = legalizer.legalize(vqe_place, netlist,
                                  config.die_width, config.die_height)

    # Metrics
    qaoa_hpwl = PlacementMetrics.half_perimeter_wirelength(qaoa_legal, netlist)
    vqe_hpwl = PlacementMetrics.half_perimeter_wirelength(vqe_legal, netlist)

    print(f"\nResults:")
    print(f"  QAOA HPWL: {qaoa_hpwl:.0f}")
    print(f"  VQE HPWL:  {vqe_hpwl:.0f}")


def run_hybrid_example():
    """Run hybrid quantum-classical optimization."""
    config = PlacementConfig()
    config.die_width = 350.0
    config.die_height = 350.0

    netlist = CircuitGenerator.generate_grid_circuit(4, 4, spacing=1.5)

    print("\n" + "="*70)
    print("HYBRID QUANTUM-CLASSICAL OPTIMIZATION")
    print("="*70)

    hybrid = HybridPlacementOptimizer(netlist, config.die_width,
                                     config.die_height, config)
    placement = hybrid.optimize_iterations(num_iterations=3, quantum_depth=2)

    hpwl = PlacementMetrics.half_perimeter_wirelength(placement, netlist)
    print(f"\nFinal HPWL: {hpwl:.0f}")


def run_ispd_example():
    """Run on ISPD 2019 benchmark (if available)."""
    print("\n" + "="*70)
    print("ISPD 2019 BENCHMARK")
    print("="*70)

    loader = ISPD2019Loader()
    benchmarks = loader.get_ispd2019_benchmarks()
    print(f"Available benchmarks: {', '.join(benchmarks[:3])}...")
    print("\nTo use ISPD benchmarks:")
    print("  1. Download ISPD 2019 files (superblue*.{nodes,nets,scl,pl})")
    print("  2. Place in benchmark directory")
    print("  3. Call: loader.load_benchmark('path/', 'superblue1')")


def main():
    """Run examples."""
    run_quantum_example()
    run_hybrid_example()
    run_ispd_example()

    print("\n" + "="*70)
    print("For detailed flow, run: python placement_iteration_flow.py")
    print("="*70)


if __name__ == "__main__":
    main()
