"""
Hardware-Efficient Ansatz (HEA) for quantum VLSI placement.

Layer structure per depth:
  Ry(θ) → Rz(φ) on every qubit  →  linear CNOT chain
"""

import numpy as np

try:
    from qiskit import QuantumCircuit
    QISKIT = True
except ImportError:
    QISKIT = False


class HardwareEfficientAnsatz:

    def __init__(self, num_qubits: int, depth: int = 3):
        self.num_qubits = num_qubits
        self.depth = depth
        self.num_params = 2 * num_qubits * depth   # Ry + Rz per qubit per layer

    def build(self, params: np.ndarray):
        """Return QuantumCircuit (or None if Qiskit unavailable)."""
        if not QISKIT:
            return None
        assert len(params) == self.num_params
        qc = QuantumCircuit(self.num_qubits)
        for q in range(self.num_qubits):
            qc.h(q)

        idx = 0
        for _ in range(self.depth):
            for q in range(self.num_qubits):
                qc.ry(params[idx], q);   idx += 1
                qc.rz(params[idx], q);   idx += 1
            for q in range(self.num_qubits - 1):
                qc.cx(q, q + 1)
        return qc

    def random_params(self) -> np.ndarray:
        return np.random.uniform(0, 2 * np.pi, self.num_params)
