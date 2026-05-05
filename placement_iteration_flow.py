#!/usr/bin/env python3
"""VLSI Physical Design: Quantum Placement - First Iteration Flow

Demonstrates complete placement flow:
  1. Problem formulation (QUBO from netlist)
  2. Quantum algorithm execution (QAOA/VQE)
  3. Solution legalization (grid alignment, overlap removal)
  4. Iterative refinement (hybrid quantum-classical)
  5. Quality evaluation vs classical baselines
"""

import time
import json
from benchmarks.circuit_generator import CircuitGenerator
from benchmarks.ispd2019 import ISPD2019Loader
from quantum_placement.qubo_formulation import PlacementQUBO
from quantum_placement.qaoa import QAOAPlacementOptimizer
from quantum_placement.vqe import VQEPlacementSolver
from quantum_placement.hybrid_optimizer import (
    HybridPlacementOptimizer, IncrementalPlacementRefinement)
from placement_core.legalization import Legalizer
from placement_core.metrics import PlacementMetrics
from classical_solver import SimulatedAnnealingSolver, GeneticPlacementSolver
from config import PlacementConfig
from utils import save_placement, PlacementVisualizer


class PlacementIterationFlow:
    """Complete placement iteration flow."""

    def __init__(self, netlist, die_width, die_height, config):
        """Initialize flow.

        Args:
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            config: PlacementConfig
        """
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.config = config
        self.legalizer = Legalizer(grid_unit=config.grid_unit)
        self.results = {}

    def run_full_flow(self, num_iterations=3):
        """Execute complete placement flow.

        Args:
            num_iterations: Number of refinement iterations

        Returns:
            Results dict with all metrics
        """
        print("\n" + "="*80)
        print("QUANTUM-BASED VLSI PLACEMENT - FIRST ITERATION FLOW")
        print("="*80)

        # Phase 1: Problem Formulation
        print("\n[PHASE 1] PROBLEM FORMULATION")
        print("-"*80)
        qubo_form = self._formulate_qubo()

        # Phase 2: Quantum Initialization
        print("\n[PHASE 2] QUANTUM INITIALIZATION (First Iteration)")
        print("-"*80)
        quantum_placement = self._quantum_init(qubo_form)

        # Phase 3: Legalization
        print("\n[PHASE 3] SOLUTION LEGALIZATION")
        print("-"*80)
        legal_placement = self._legalize(quantum_placement)

        # Phase 4: Iterative Refinement
        print("\n[PHASE 4] ITERATIVE REFINEMENT")
        print("-"*80)
        refined_placement = self._iterative_refine(legal_placement, num_iterations)

        # Phase 5: Evaluation
        print("\n[PHASE 5] QUALITY EVALUATION")
        print("-"*80)
        self._evaluate_quality(refined_placement)

        return self.results

    def _formulate_qubo(self):
        """Formulate QUBO from placement problem."""
        print(f"Circuit: {self.netlist.get_cell_count()} cells, "
              f"{self.netlist.get_net_count()} nets")
        print(f"Die size: {self.die_width:.0f} x {self.die_height:.0f}")

        qubo_form = PlacementQUBO(
            self.netlist, self.die_width, self.die_height,
            grid_cells=4
        )
        qubo_form.build_qubo(wl_weight=1.0, overlap_weight=5.0)

        qubit_count = qubo_form.get_qubit_count()
        qubo_terms = len(qubo_form.qubo)

        print(f"\nQUBO Formulation:")
        print(f"  Qubits: {qubit_count}")
        print(f"  QUBO terms: {qubo_terms}")
        print(f"  Grid resolution: 4x4 ({qubit_count//4} bits per cell)")

        self.results['qubo_stats'] = {
            'qubits': qubit_count,
            'terms': qubo_terms
        }

        return qubo_form

    def _quantum_init(self, qubo_form):
        """Execute quantum algorithm for first iteration."""
        print("\nQuantum Algorithms:")

        # QAOA
        print("  [QAOA] Depth=2, Iterations=25")
        start = time.time()
        qaoa = QAOAPlacementOptimizer(qubo_form, depth=2)
        qaoa_place, qaoa_cost, _ = qaoa.optimize(max_iterations=25)
        qaoa_time = time.time() - start
        print(f"    Time: {qaoa_time:.3f}s, Cost: {qaoa_cost:.1f}")

        # VQE
        print("  [VQE] Ansatz Depth=2, Iterations=25")
        start = time.time()
        vqe = VQEPlacementSolver(qubo_form, ansatz_depth=2)
        vqe_place, vqe_cost, _ = vqe.solve(max_iterations=25)
        vqe_time = time.time() - start
        print(f"    Time: {vqe_time:.3f}s, Cost: {vqe_cost:.1f}")

        # Classical baseline
        print("  [SimAnneal] Baseline reference")
        start = time.time()
        sa = SimulatedAnnealingSolver(initial_temp=500, cooling_rate=0.95)
        sa_place = sa.solve(self.netlist, self.die_width, self.die_height,
                           max_iterations=500)
        sa_time = time.time() - start
        sa_cost = PlacementMetrics.half_perimeter_wirelength(sa_place, self.netlist)
        print(f"    Time: {sa_time:.3f}s, HPWL: {sa_cost:.0f}")

        self.results['quantum_init'] = {
            'qaoa': {'time': qaoa_time, 'cost': qaoa_cost},
            'vqe': {'time': vqe_time, 'cost': vqe_cost},
            'sa_baseline': {'time': sa_time, 'cost': sa_cost}
        }

        # Select best quantum result
        if qaoa_cost <= vqe_cost:
            print(f"\n  Best: QAOA (cost={qaoa_cost:.1f})")
            return qaoa_place
        else:
            print(f"\n  Best: VQE (cost={vqe_cost:.1f})")
            return vqe_place

    def _legalize(self, placement):
        """Legalize placement solution."""
        print("\nLegalization Steps:")
        print("  1. Grid snapping (1.0 micron grid)")
        print("  2. Overlap resolution")
        print("  3. Boundary enforcement")

        legal = self.legalizer.legalize(
            placement, self.netlist,
            self.die_width, self.die_height
        )

        # Check legality
        overlap = self._compute_overlap(legal)
        boundary_violations = self._check_boundaries(legal)

        print(f"\n  Result: Overlap={overlap:.0f}, Violations={boundary_violations}")

        self.results['legalization'] = {
            'overlap': overlap,
            'boundary_violations': boundary_violations
        }

        return legal

    def _iterative_refine(self, placement, num_iterations):
        """Run iterative refinement."""
        print(f"\nIterative Refinement ({num_iterations} iterations):")
        print(f"{'Iter':>4} {'Method':15} {'HPWL':>12} {'Time(s)':>8}")
        print("-"*45)

        current = placement
        history = []

        # Initial metrics
        hpwl = PlacementMetrics.half_perimeter_wirelength(current, self.netlist)
        print(f"  0 {'Initial':15} {hpwl:12.0f}")
        history.append(hpwl)

        # Incremental refinement
        refiner = IncrementalPlacementRefinement(
            self.netlist, self.die_width, self.die_height)

        for it in range(1, num_iterations + 1):
            start = time.time()

            # Identify critical nets
            refiner.identify_critical_nets(current, top_k=5)

            # Refine critical region
            current = refiner.refine_critical_region(current, num_iterations=10)

            # Legalize
            current = self.legalizer.legalize(
                current, self.netlist,
                self.die_width, self.die_height
            )

            elapsed = time.time() - start
            hpwl = PlacementMetrics.half_perimeter_wirelength(current, self.netlist)
            history.append(hpwl)

            improvement = (history[it-1] - hpwl) / history[it-1] * 100
            print(f"  {it} {'CriticalNet':15} {hpwl:12.0f} {elapsed:8.3f}s ({improvement:+.1f}%)")

        self.results['refinement_history'] = history
        return current

    def _evaluate_quality(self, placement):
        """Evaluate final placement quality."""
        hpwl = PlacementMetrics.half_perimeter_wirelength(placement, self.netlist)
        overlap = self._compute_overlap(placement)
        utilization = self._compute_utilization(placement)

        print(f"\nFinal Quality Metrics:")
        print(f"  HPWL: {hpwl:.0f} microns")
        print(f"  Overlap: {overlap:.0f} square microns")
        print(f"  Die utilization: {utilization:.1f}%")

        self.results['final_quality'] = {
            'hpwl': hpwl,
            'overlap': overlap,
            'utilization': utilization
        }

    def _compute_overlap(self, placement):
        """Compute total overlap area."""
        overlap = 0
        cells_list = list(placement.items())

        for i, (cid1, (x1, y1)) in enumerate(cells_list):
            w1, h1 = self.netlist.cells[cid1]['width'], \
                     self.netlist.cells[cid1]['height']

            for cid2, (x2, y2) in cells_list[i+1:]:
                w2, h2 = self.netlist.cells[cid2]['width'], \
                         self.netlist.cells[cid2]['height']

                x_overlap = max(0, min(x1+w1, x2+w2) - max(x1, x2))
                y_overlap = max(0, min(y1+h1, y2+h2) - max(y1, y2))
                overlap += x_overlap * y_overlap

        return overlap

    def _check_boundaries(self, placement):
        """Check boundary violations."""
        violations = 0
        for cell_id, (x, y) in placement.items():
            w, h = self.netlist.cells[cell_id]['width'], \
                   self.netlist.cells[cell_id]['height']
            if x < 0 or y < 0 or x + w > self.die_width or y + h > self.die_height:
                violations += 1
        return violations

    def _compute_utilization(self, placement):
        """Compute die utilization."""
        total_area = self.netlist.get_total_area()
        die_area = self.die_width * self.die_height
        return (total_area / die_area) * 100


def main():
    """Run complete placement flow examples."""
    config = PlacementConfig()

    # Example 1: Small circuit
    print("\n" + "="*80)
    print("EXAMPLE 1: Small Synthetic Circuit")
    print("="*80)

    netlist = CircuitGenerator.generate_random_circuit(
        num_cells=12, num_nets=30, avg_fanout=3, seed=42)
    config.die_width = 250.0
    config.die_height = 250.0

    flow1 = PlacementIterationFlow(netlist, config.die_width, config.die_height, config)
    results1 = flow1.run_full_flow(num_iterations=3)

    # Example 2: Grid circuit
    print("\n" + "="*80)
    print("EXAMPLE 2: Grid-Structured Circuit")
    print("="*80)

    netlist2 = CircuitGenerator.generate_grid_circuit(4, 4, spacing=1.5)
    config.die_width = 400.0
    config.die_height = 400.0

    flow2 = PlacementIterationFlow(netlist2, config.die_width, config.die_height, config)
    results2 = flow2.run_full_flow(num_iterations=3)

    print("\n" + "="*80)
    print("PLACEMENT FLOW COMPLETE")
    print("="*80)
    print("\nKey insights:")
    print("  • Quantum algorithms provide fast initial solutions")
    print("  • Legalization ensures valid placements")
    print("  • Iterative refinement improves quality")
    print("  • Critical net identification targets hotspots")


if __name__ == "__main__":
    main()
