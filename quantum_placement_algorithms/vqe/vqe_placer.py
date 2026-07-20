"""
VQE Placement Algorithm — a compact variational solver prototype for VLSI placement.

The implementation minimizes the expectation of a QUBO-derived Hamiltonian
using a variational circuit ansatz. The design is intentionally lightweight so
that it can be run locally and inspected easily, but it should be regarded as a
research-oriented baseline rather than a production placement solver.
"""

import numpy as np
from scipy.optimize import minimize
from dataclasses import dataclass, field
from typing import Optional

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT = True
except ImportError:
    QISKIT = False

from quantum_placement_ansatz.hardware_efficient import HardwareEfficientAnsatz
from quantum_placement_ansatz.problem_inspired import ProblemInspiredAnsatz


@dataclass
class VQEResult:
    placement: dict
    energy: float
    ansatz_type: str
    iterations: int
    convergence: list = field(default_factory=list)


class VQEPlacer:
    """
    VQE-based global placer.

    Parameters
    ----------
    qubo_Q      : Combined QUBO dict.
    num_qubits  : Total qubit count.
    ansatz_type : "hardware_efficient" | "problem_inspired".
    depth       : Ansatz circuit depth.
    shots       : Shots per circuit evaluation.
    """

    def __init__(self, qubo_Q: dict, num_qubits: int,
                 ansatz_type: str = "hardware_efficient",
                 depth: int = 3, shots: int = 512):
        self.Q = qubo_Q
        self.num_qubits = num_qubits
        self.shots = shots
        self._history: list[float] = []
        self._best_bits: Optional[str] = None
        self._best_energy = float("inf")

        if ansatz_type == "problem_inspired":
            self.ansatz = ProblemInspiredAnsatz(num_qubits, qubo_Q, depth)
        else:
            self.ansatz = HardwareEfficientAnsatz(num_qubits, depth)

    # ------------------------------------------------------------------ public

    def run(self, max_iter: int = 100) -> VQEResult:
        if self.num_qubits < 2:
            self._best_bits = "0" * self.num_qubits
            self._best_energy = self._eval_bits(self._best_bits)
            self._history.append(self._best_energy)
            return VQEResult(
                placement={"_bitstring": self._best_bits},
                energy=self._best_energy,
                ansatz_type=type(self.ansatz).__name__,
                iterations=0,
                convergence=self._history,
            )

        x0 = self.ansatz.random_params()

        result = minimize(
            self._energy,
            x0,
            method="COBYLA",
            options={"maxiter": max_iter, "rhobeg": 0.3},
        )

        self._energy(result.x, capture=True)
        bits = self._best_bits or "0" * self.num_qubits

        return VQEResult(
            placement={"_bitstring": bits},
            energy=self._best_energy,
            ansatz_type=type(self.ansatz).__name__,
            iterations=len(self._history),
            convergence=self._history,
        )

    # ------------------------------------------------------------------ internals

    def _energy(self, params: np.ndarray, capture: bool = False) -> float:
        if QISKIT:
            return self._energy_qiskit(params, capture)
        return self._energy_fallback(params, capture)

    def _energy_qiskit(self, params, capture: bool) -> float:
        qc = self.ansatz.build(params)
        if qc is None:
            return float("inf")
        qc.measure_all()

        try:
            sim = AerSimulator()
            counts = sim.run(qc, shots=self.shots).result().get_counts()
        except Exception:
            return float("inf")

        total, total_shots = 0.0, sum(counts.values())
        best_e, best_bits = float("inf"), None

        for bits, cnt in counts.items():
            e = self._eval_bits(bits)
            total += e * cnt
            if e < best_e:
                best_e, best_bits = e, bits

        if best_e < self._best_energy:
            self._best_energy = best_e
            self._best_bits = best_bits
            self._history.append(best_e)

        if capture and best_bits:
            self._best_bits = best_bits

        return total / total_shots

    def _eval_bits(self, bits: str) -> float:
        cost = 0.0
        for (i, j), coeff in self.Q.items():
            if i < len(bits) and j < len(bits):
                if i == j:
                    cost += coeff * int(bits[i])
                else:
                    cost += coeff * int(bits[i]) * int(bits[j])
        return cost

    def _energy_fallback(self, params, capture: bool) -> float:
        rng = np.random.default_rng(seed=int(np.sum(params * 1e4)) % (2**31))
        best_e, best_bits = float("inf"), None
        for _ in range(self.shots):
            bits = "".join(rng.choice(["0", "1"], size=self.num_qubits))
            e = self._eval_bits(bits)
            if e < best_e:
                best_e, best_bits = e, bits
        if best_e < self._best_energy:
            self._best_energy = best_e
            self._best_bits = best_bits
            self._history.append(best_e)
        if capture and best_bits:
            self._best_bits = best_bits
        return best_e
