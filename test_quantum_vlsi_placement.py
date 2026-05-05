"""
Test suite for Quantum VLSI Placement algorithms on ISPD 2019 benchmarks.

Covers:
  - QUBO formulation correctness
  - QAOA / VQE / Quantum Annealing on tiny synthetic circuits
  - Legalizer output validity
  - End-to-end placement flow
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np

from quantum_placement_database import QuantumNetlist, QUBOMatrix
from quantum_placement_operators import (
    QUBOWirelengthOperator, QUBODensityOperator, QuantumLegalizer)
from quantum_placement_algorithms import QAOAPlacer, VQEPlacer, QuantumAnnealer
from quantum_placement_metrics import QuantumPlacementMetrics
from quantum_placement_config import QuantumPlacerConfig
from quantum_vlsi_placer import QuantumVLSIPlacer
from ispd2019_benchmark import SyntheticISPD2019, ISPD2019Evaluator


# ------------------------------------------------------------------ helpers

def make_tiny_netlist(n: int = 8) -> tuple:
    nl = QuantumNetlist()
    for i in range(n):
        nl.add_cell(f"c{i}", 2.0, 1.0)
    # Chain: c0-c1, c1-c2, ..., c(n-2)-c(n-1)
    for i in range(n - 1):
        nl.add_net(f"net{i}")
        nl.add_pin(f"c{i}", f"net{i}")
        nl.add_pin(f"c{i+1}", f"net{i}")
    return nl, 20.0, 10.0


def test_quantum_netlist():
    nl, dw, dh = make_tiny_netlist(6)
    assert nl.cell_count == 6
    assert nl.net_count == 5
    assert nl.num_movable == 6
    print("  PASS: QuantumNetlist")


def test_qubo_matrix():
    Q = QUBOMatrix(4)
    Q.add(0, 1, 2.5)
    Q.add(0, 0, -1.0)
    assert Q.nnz() == 2
    cost = Q.evaluate("1010")
    assert isinstance(cost, float)
    print("  PASS: QUBOMatrix")


def test_wirelength_operator():
    nl, dw, dh = make_tiny_netlist(4)
    op = QUBOWirelengthOperator(nl, dw, dh, bits_per_dim=2)
    Q = op.build(weight=1.0)
    assert Q.nnz() > 0
    bits = "0" * op.num_qubits
    pl = op.decode_placement(bits)
    assert len(pl) == 4
    for cid, (x, y) in pl.items():
        assert 0 <= x <= dw
        assert 0 <= y <= dh
    print("  PASS: QUBOWirelengthOperator")


def test_density_operator():
    nl, dw, dh = make_tiny_netlist(4)
    op = QUBODensityOperator(nl, dw, dh, bits_per_dim=2)
    Q = op.build(weight=5.0)
    assert Q.nnz() > 0
    pl = {f"c{i}": (float(i * 3), 0.0) for i in range(4)}
    overflow = op.overflow(pl)
    assert 0.0 <= overflow <= 1.0
    print("  PASS: QUBODensityOperator")


def test_legalizer():
    nl, dw, dh = make_tiny_netlist(6)
    pl = {f"c{i}": (float(i * 1.5), float(i % 3)) for i in range(6)}
    leg = QuantumLegalizer(row_height=1.0)
    legal = leg.legalize(pl, nl, dw, dh)
    assert len(legal) >= len(nl.movable_cells)
    for cid, (x, y) in legal.items():
        if cid in nl.cells:
            assert x >= 0 and y >= 0
    print("  PASS: QuantumLegalizer")


def test_qaoa_placer():
    nl, dw, dh = make_tiny_netlist(4)
    wl_op = QUBOWirelengthOperator(nl, dw, dh, bits_per_dim=2)
    Q = wl_op.build(1.0)
    solver = QAOAPlacer(Q.Q, wl_op.num_qubits, p_depth=1, shots=64)
    result = solver.run(max_iter=5)
    assert "_bitstring" in result.placement
    assert len(result.placement["_bitstring"]) == wl_op.num_qubits
    print("  PASS: QAOAPlacer")


def test_vqe_placer():
    nl, dw, dh = make_tiny_netlist(4)
    wl_op = QUBOWirelengthOperator(nl, dw, dh, bits_per_dim=2)
    Q = wl_op.build(1.0)
    solver = VQEPlacer(Q.Q, wl_op.num_qubits, depth=1, shots=64)
    result = solver.run(max_iter=5)
    assert "_bitstring" in result.placement
    print("  PASS: VQEPlacer")


def test_quantum_annealer():
    nl, dw, dh = make_tiny_netlist(4)
    wl_op = QUBOWirelengthOperator(nl, dw, dh, bits_per_dim=2)
    Q = wl_op.build(1.0)
    solver = QuantumAnnealer(Q.Q, wl_op.num_qubits, num_replicas=4, seed=0)
    result = solver.run(num_sweeps=20)
    assert len(result.placement["_bitstring"]) == wl_op.num_qubits
    assert result.energy < float("inf")
    print("  PASS: QuantumAnnealer")


def test_placement_metrics():
    nl, dw, dh = make_tiny_netlist(4)
    pl = {f"c{i}": (float(i * 3), 0.0) for i in range(4)}
    h = QuantumPlacementMetrics.hpwl(pl, nl)
    assert h >= 0
    ov = QuantumPlacementMetrics.total_overlap_area(pl, nl)
    assert ov >= 0
    bv = QuantumPlacementMetrics.boundary_violations(pl, nl, dw, dh)
    assert bv >= 0
    print("  PASS: QuantumPlacementMetrics")


def test_synthetic_generator():
    gen = SyntheticISPD2019(seed=0)
    nl, dw, dh, init_pl = gen.generate("ispd2019_test1", num_cells=50)
    assert nl.cell_count == 50
    assert dw > 0 and dh > 0
    assert len(init_pl) == 50
    print("  PASS: SyntheticISPD2019 generator")


def test_ispd2019_evaluator():
    gen = SyntheticISPD2019(seed=0)
    nl, dw, dh, init_pl = gen.generate("ispd2019_test1", num_cells=30)
    ev = ISPD2019Evaluator(nl, dw, dh)
    m = ev.evaluate(init_pl)
    assert "hpwl" in m and "density_overflow" in m
    assert m["hpwl"] >= 0
    print("  PASS: ISPD2019Evaluator")


def test_end_to_end_qaoa():
    gen = SyntheticISPD2019(seed=1)
    nl, dw, dh, init_pl = gen.generate("ispd2019_test1", num_cells=12)
    cfg = QuantumPlacerConfig(
        algorithm="qaoa", bits_per_dim=2,
        qaoa_depth=1, qaoa_max_iter=5,
        refinement_iterations=1)
    placer = QuantumVLSIPlacer(nl, dw, dh, cfg)
    pl = placer.run()
    assert len(pl) > 0
    for cid, (x, y) in pl.items():
        if cid in nl.cells:
            assert x >= 0 and y >= 0
    print("  PASS: End-to-end QAOA placement")


def test_end_to_end_quantum_annealing():
    gen = SyntheticISPD2019(seed=2)
    nl, dw, dh, init_pl = gen.generate("ispd2019_test1", num_cells=12)
    cfg = QuantumPlacerConfig(
        algorithm="quantum_annealing", bits_per_dim=2,
        qa_sweeps=30, refinement_iterations=1)
    placer = QuantumVLSIPlacer(nl, dw, dh, cfg)
    pl = placer.run()
    assert len(pl) > 0
    print("  PASS: End-to-end Quantum Annealing placement")


# ------------------------------------------------------------------ runner

TESTS = [
    test_quantum_netlist,
    test_qubo_matrix,
    test_wirelength_operator,
    test_density_operator,
    test_legalizer,
    test_qaoa_placer,
    test_vqe_placer,
    test_quantum_annealer,
    test_placement_metrics,
    test_synthetic_generator,
    test_ispd2019_evaluator,
    test_end_to_end_qaoa,
    test_end_to_end_quantum_annealing,
]


if __name__ == "__main__":
    print(f"\n{'Quantum VLSI Placement — Test Suite':=^60}")
    passed = failed = 0
    for fn in TESTS:
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {fn.__name__} — {e}")
            failed += 1
    print(f"\n  Results: {passed}/{len(TESTS)} passed, {failed} failed")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
