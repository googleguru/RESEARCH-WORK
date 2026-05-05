#!/usr/bin/env python3
"""Example: Run quantum and classical placement algorithms"""

from benchmarks import CircuitGenerator, BenchmarkEvaluator
from classical_solver import GeneticPlacementSolver, SimulatedAnnealingSolver
from quantum_placement.qaoa import QAOAPlacementOptimizer
from placement_core.legalization import Legalizer
from config import PlacementConfig


def main():
    # Configuration
    config = PlacementConfig()
    config.die_width = 500.0
    config.die_height = 500.0

    # Generate benchmark circuit
    print("Generating benchmark circuit...")
    netlist = CircuitGenerator.generate_random_circuit(
        num_cells=20,
        num_nets=50,
        avg_fanout=3,
        seed=42
    )
    print(f"Circuit: {netlist.get_cell_count()} cells, {netlist.get_net_count()} nets")

    # Initialize solvers
    ga_solver = GeneticPlacementSolver(
        population_size=config.genetic_pop_size,
        generations=config.genetic_generations
    )

    sa_solver = SimulatedAnnealingSolver(
        initial_temp=config.sa_initial_temp,
        cooling_rate=config.sa_cooling_rate
    )

    qaoa_optimizer = QAOAPlacementOptimizer(
        num_qubits=netlist.get_cell_count(),
        depth=config.qaoa_depth
    )

    # Run benchmarks
    evaluator = BenchmarkEvaluator()

    print("\nRunning Genetic Algorithm...")
    ga_result = evaluator.evaluate_algorithm(
        ga_solver, netlist,
        config.die_width, config.die_height,
        "Genetic Algorithm"
    )

    print("Running Simulated Annealing...")
    sa_result = evaluator.evaluate_algorithm(
        sa_solver, netlist,
        config.die_width, config.die_height,
        "Simulated Annealing"
    )

    # Print results
    evaluator.print_summary()
    evaluator.compare_algorithms()

    # Legalize solutions
    print("\nLegalizing placements...")
    legalizer = Legalizer(grid_unit=config.grid_unit)

    ga_legal = legalizer.legalize(
        ga_result['placement'], netlist,
        config.die_width, config.die_height
    )
    sa_legal = legalizer.legalize(
        sa_result['placement'], netlist,
        config.die_width, config.die_height
    )

    print("Placement complete!")


if __name__ == "__main__":
    main()
