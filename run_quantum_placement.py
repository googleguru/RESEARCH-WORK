#!/usr/bin/env python3
"""Quantum-based VLSI Placement: First Iteration Implementation using ISPD 2019"""

import sys
import time
from benchmarks.ispd2019 import ISPD2019Loader
from benchmarks.circuit_generator import CircuitGenerator
from quantum_placement.qubo_formulation import PlacementQUBO
from quantum_placement.qaoa import QAOAPlacementOptimizer
from quantum_placement.vqe import VQEPlacementSolver
from classical_solver import SimulatedAnnealingSolver
from placement_core.legalization import Legalizer
from placement_core.metrics import PlacementMetrics
from config import PlacementConfig


def run_quantum_placement(netlist, die_width, die_height, config, benchmark_name=""):
    """Run first iteration of quantum-based placement.

    Args:
        netlist: Circuit netlist
        die_width: Die width
        die_height: Die height
        config: PlacementConfig object
        benchmark_name: Benchmark name for reporting

    Returns:
        Results dict
    """
    print(f"\n{'='*70}")
    print(f"Quantum VLSI Placement: {benchmark_name}")
    print(f"Cells: {netlist.get_cell_count()}, Nets: {netlist.get_net_count()}")
    print(f"Die: {die_width:.0f} x {die_height:.0f}")
    print(f"{'='*70}")

    results = {'benchmark': benchmark_name, 'configs': {}}

    # Step 1: Build QUBO formulation
    print("\n[1/4] Building QUBO formulation...")
    qubo_form = PlacementQUBO(
        netlist, die_width, die_height,
        grid_cells=4  # 4x4 grid for place encoding
    )
    qubo_form.build_qubo(wl_weight=1.0, overlap_weight=5.0)
    qubits_needed = qubo_form.get_qubit_count()
    print(f"  Qubits required: {qubits_needed}")

    # Step 2: QAOA First Iteration
    print("\n[2/4] QAOA Optimization (depth=2, max_iter=30)...")
    start = time.time()
    qaoa = QAOAPlacementOptimizer(qubo_form, depth=2)
    qaoa_placement, qaoa_cost, qaoa_hist = qaoa.optimize(max_iterations=30)
    qaoa_time = time.time() - start

    # Legalize QAOA placement
    legalizer = Legalizer(grid_unit=config.grid_unit)
    qaoa_legal = legalizer.legalize(qaoa_placement, netlist, die_width, die_height)
    qaoa_hpwl = PlacementMetrics.half_perimeter_wirelength(qaoa_legal, netlist)

    print(f"  Time: {qaoa_time:.3f}s | HPWL: {qaoa_hpwl:.0f}")
    results['qaoa'] = {
        'hpwl': qaoa_hpwl,
        'time': qaoa_time,
        'placement': qaoa_legal
    }

    # Step 3: VQE First Iteration
    print("\n[3/4] VQE Optimization (depth=2, max_iter=30)...")
    start = time.time()
    vqe = VQEPlacementSolver(qubo_form, ansatz_depth=2)
    vqe_placement, vqe_cost, vqe_hist = vqe.solve(max_iterations=30)
    vqe_time = time.time() - start

    vqe_legal = legalizer.legalize(vqe_placement, netlist, die_width, die_height)
    vqe_hpwl = PlacementMetrics.half_perimeter_wirelength(vqe_legal, netlist)

    print(f"  Time: {vqe_time:.3f}s | HPWL: {vqe_hpwl:.0f}")
    results['vqe'] = {
        'hpwl': vqe_hpwl,
        'time': vqe_time,
        'placement': vqe_legal
    }

    # Step 4: Classical baseline (Simulated Annealing)
    print("\n[4/4] Simulated Annealing Baseline...")
    start = time.time()
    sa = SimulatedAnnealingSolver(initial_temp=500, cooling_rate=0.95)
    sa_placement = sa.solve(netlist, die_width, die_height, max_iterations=1000)
    sa_time = time.time() - start

    sa_legal = legalizer.legalize(sa_placement, netlist, die_width, die_height)
    sa_hpwl = PlacementMetrics.half_perimeter_wirelength(sa_legal, netlist)

    print(f"  Time: {sa_time:.3f}s | HPWL: {sa_hpwl:.0f}")
    results['sa'] = {
        'hpwl': sa_hpwl,
        'time': sa_time,
        'placement': sa_legal
    }

    # Summary
    print(f"\n{'-'*70}")
    print("RESULTS SUMMARY:")
    print(f"{'-'*70}")
    print(f"Algorithm          HPWL        Time(s)    Speedup")
    print(f"{'-'*70}")
    print(f"QAOA              {qaoa_hpwl:10.0f}    {qaoa_time:8.3f}    {sa_time/qaoa_time:7.2f}x")
    print(f"VQE               {vqe_hpwl:10.0f}    {vqe_time:8.3f}    {sa_time/vqe_time:7.2f}x")
    print(f"Simulated Anneal  {sa_hpwl:10.0f}    {sa_time:8.3f}    1.00x (baseline)")
    print(f"{'-'*70}")

    # Quality comparison
    qa_improvement = (1 - qaoa_hpwl/sa_hpwl) * 100
    vqe_improvement = (1 - vqe_hpwl/sa_hpwl) * 100
    print(f"\nQuality vs Baseline:")
    print(f"  QAOA: {qa_improvement:+.1f}%")
    print(f"  VQE:  {vqe_improvement:+.1f}%")

    return results


def main():
    # Configuration
    config = PlacementConfig()

    # Test 1: Synthetic benchmark (small)
    print("\n" + "="*70)
    print("TEST 1: Synthetic Benchmark (Small Circuit)")
    print("="*70)

    netlist = CircuitGenerator.generate_random_circuit(
        num_cells=8,
        num_nets=20,
        avg_fanout=3,
        seed=42
    )
    config.die_width = 200.0
    config.die_height = 200.0

    results1 = run_quantum_placement(
        netlist, config.die_width, config.die_height,
        config, "synthetic_small"
    )

    # Test 2: Grid circuit
    print("\n" + "="*70)
    print("TEST 2: Grid-Structured Circuit")
    print("="*70)

    netlist2 = CircuitGenerator.generate_grid_circuit(3, 3, spacing=2.0)
    config.die_width = 300.0
    config.die_height = 300.0

    results2 = run_quantum_placement(
        netlist2, config.die_width, config.die_height,
        config, "grid_3x3"
    )

    # Test 3: ISPD 2019 style (if benchmark file available)
    print("\n" + "="*70)
    print("TEST 3: ISPD 2019 Benchmark Format")
    print("="*70)

    try:
        ispd_loader = ISPD2019Loader()
        # Example: Load from local directory if available
        # netlist3, die_w, die_h, _ = ispd_loader.load_benchmark('.', 'superblue1')
        print("  [INFO] ISPD 2019 loader ready for benchmark files")
        print("  [INFO] Place .nodes, .nets, .scl, .pl files for ISPD benchmarks")
    except Exception as e:
        print(f"  [INFO] ISPD file not available: {e}")

    print("\n" + "="*70)
    print("First Iteration Quantum Placement Complete!")
    print("="*70)


if __name__ == "__main__":
    main()
