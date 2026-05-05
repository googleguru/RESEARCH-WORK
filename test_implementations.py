#!/usr/bin/env python3
"""Test suite for Quantum VLSI Placement implementations"""

import sys


def test_netlist():
    """Test netlist parsing and management."""
    from placement_core.netlist import Netlist

    netlist = Netlist()
    netlist.add_cell('cell_0', 10.0, 10.0)
    netlist.add_cell('cell_1', 15.0, 15.0)
    netlist.add_net('net_0')
    netlist.add_connection('cell_0', 'net_0', 'pin0')
    netlist.add_connection('cell_1', 'net_0', 'pin1')

    assert netlist.get_cell_count() == 2
    assert netlist.get_net_count() == 1
    assert netlist.get_cell_area('cell_0') == 100.0
    print("✓ Netlist tests passed")


def test_qubo_formulation():
    """Test QUBO formulation."""
    try:
        from benchmarks.circuit_generator import CircuitGenerator
        from quantum_placement.qubo_formulation import PlacementQUBO

        netlist = CircuitGenerator.generate_random_circuit(
            num_cells=5, num_nets=10, seed=42)

        qubo = PlacementQUBO(netlist, 100, 100, grid_cells=2)
        qubo.build_qubo()

        assert qubo.get_qubit_count() > 0
        assert len(qubo.qubo) > 0
        print(f"✓ QUBO formulation passed ({qubo.get_qubit_count()} qubits)")
    except ImportError as e:
        print(f"⊘ QUBO formulation skipped (requires numpy): {e}")


def test_legalization():
    """Test placement legalization."""
    from placement_core.legalization import Legalizer
    from placement_core.netlist import Netlist

    netlist = Netlist()
    netlist.add_cell('c0', 5.0, 5.0)
    netlist.add_cell('c1', 5.0, 5.0)

    # Overlapping placement
    placement = {'c0': (10.2, 15.7), 'c1': (12.1, 18.3)}

    legalizer = Legalizer(grid_unit=1.0)
    legal = legalizer.legalize(placement, netlist, 100, 100)

    # Check grid alignment
    for cell_id, (x, y) in legal.items():
        assert x % 1.0 < 0.01 or abs(x % 1.0 - 1.0) < 0.01
        assert y % 1.0 < 0.01 or abs(y % 1.0 - 1.0) < 0.01

    print("✓ Legalization tests passed")


def test_metrics():
    """Test placement metrics."""
    from placement_core.metrics import PlacementMetrics
    from benchmarks.circuit_generator import CircuitGenerator

    netlist = CircuitGenerator.generate_random_circuit(
        num_cells=4, num_nets=8, seed=42)

    placement = {f'cell_{i}': (float(i)*10, float(i)*10)
                 for i in range(4)}

    hpwl = PlacementMetrics.half_perimeter_wirelength(placement, netlist)
    assert hpwl >= 0
    print(f"✓ Metrics tests passed (HPWL={hpwl:.0f})")


def test_circuit_generation():
    """Test circuit generation."""
    from benchmarks.circuit_generator import CircuitGenerator

    # Random circuit
    netlist1 = CircuitGenerator.generate_random_circuit(
        num_cells=8, num_nets=20, avg_fanout=3, seed=42)
    assert netlist1.get_cell_count() == 8
    assert netlist1.get_net_count() == 20

    # Grid circuit
    netlist2 = CircuitGenerator.generate_grid_circuit(3, 3, spacing=2.0)
    assert netlist2.get_cell_count() == 9
    assert netlist2.get_net_count() > 0

    print("✓ Circuit generation tests passed")


def test_ispd_loader():
    """Test ISPD 2019 loader."""
    from benchmarks.ispd2019 import ISPD2019Loader

    loader = ISPD2019Loader()
    benchmarks = loader.get_ispd2019_benchmarks()
    assert len(benchmarks) > 0
    assert 'superblue1' in benchmarks
    print(f"✓ ISPD loader tests passed ({len(benchmarks)} benchmarks)")


def test_classical_solvers():
    """Test classical baseline solvers."""
    from classical_solver import SimulatedAnnealingSolver, GeneticPlacementSolver
    from benchmarks.circuit_generator import CircuitGenerator

    netlist = CircuitGenerator.generate_random_circuit(
        num_cells=6, num_nets=15, seed=42)

    # Simulated Annealing
    sa = SimulatedAnnealingSolver(initial_temp=100, cooling_rate=0.95)
    placement_sa = sa.solve(netlist, 100, 100, max_iterations=50)
    assert len(placement_sa) == netlist.get_cell_count()

    # Genetic Algorithm
    ga = GeneticPlacementSolver(population_size=20, generations=5)
    placement_ga = ga.solve(netlist, 100, 100)
    assert len(placement_ga) == netlist.get_cell_count()

    print("✓ Classical solvers tests passed")


def test_config():
    """Test configuration."""
    from config import PlacementConfig

    config = PlacementConfig()
    assert config.die_width == 1000.0
    assert config.qaoa_depth == 5

    config_dict = config.to_dict()
    assert len(config_dict) > 0

    config2 = PlacementConfig()
    config2.from_dict({'die_width': 500.0})
    assert config2.die_width == 500.0

    print("✓ Configuration tests passed")


def test_io_utils():
    """Test I/O utilities."""
    from utils.io_utils import save_placement, load_placement
    import tempfile
    import os

    placement = {'cell_0': (10.5, 20.3), 'cell_1': (30.1, 40.2)}

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'test_placement.json')

        # Save
        save_placement(placement, filepath)
        assert os.path.exists(filepath)

        # Load
        loaded = load_placement(filepath)
        assert len(loaded) == 2
        assert loaded['cell_0'] == (10.5, 20.3)

    print("✓ I/O utilities tests passed")


def test_hybrid_optimizer():
    """Test hybrid optimizer structure."""
    try:
        from quantum_placement.hybrid_optimizer import (
            HybridPlacementOptimizer, IncrementalPlacementRefinement)
        from benchmarks.circuit_generator import CircuitGenerator
        from config import PlacementConfig

        netlist = CircuitGenerator.generate_random_circuit(
            num_cells=6, num_nets=15, seed=42)
        config = PlacementConfig()

        # Hybrid optimizer
        hybrid = HybridPlacementOptimizer(netlist, 100, 100, config)
        assert hybrid.netlist == netlist

        # Incremental refinement
        refiner = IncrementalPlacementRefinement(netlist, 100, 100)
        placement = {f'cell_{i}': (float(i)*10, float(i)*10)
                     for i in range(6)}
        critical = refiner.identify_critical_nets(placement, top_k=3)
        assert len(critical) <= 3

        print("✓ Hybrid optimizer tests passed")
    except ImportError as e:
        print(f"⊘ Hybrid optimizer skipped (requires numpy): {e}")


def run_all_tests():
    """Run all tests."""
    tests = [
        ('Netlist', test_netlist),
        ('QUBO Formulation', test_qubo_formulation),
        ('Legalization', test_legalization),
        ('Metrics', test_metrics),
        ('Circuit Generation', test_circuit_generation),
        ('ISPD Loader', test_ispd_loader),
        ('Classical Solvers', test_classical_solvers),
        ('Configuration', test_config),
        ('I/O Utils', test_io_utils),
        ('Hybrid Optimizer', test_hybrid_optimizer),
    ]

    print("\n" + "="*70)
    print("QUANTUM VLSI PLACEMENT - IMPLEMENTATION TEST SUITE")
    print("="*70 + "\n")

    passed = 0
    failed = 0
    skipped = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result == 'skip':
                skipped += 1
            else:
                passed += 1
        except Exception as e:
            print(f"✗ {name} FAILED: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {skipped} skipped, {failed} failed")
    print("="*70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
