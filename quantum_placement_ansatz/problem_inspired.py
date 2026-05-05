"""
Problem-Inspired Ansatz for VLSI placement QUBO.

Uses the QUBO connectivity to place CNOT gates only between qubits that
share a non-zero QUBO coefficient, reducing gate count vs HEA.
"""

import numpy as np

try:
    from qiskit import QuantumCircuit
    QISKIT = True
except ImportError:
    QISKIT = False


class ProblemInspiredAnsatz:

    def __init__(self, num_qubits: int, qubo_Q: dict, depth: int = 2):
        self.num_qubits = num_qubits
        self.depth = depth
        # Interaction pairs from QUBO (off-diagonal terms)
        self.pairs = [(i, j) for (i, j) in qubo_Q if i != j]
        self.num_params = num_qubits * depth + len(self.pairs) * depth

    def build(self, params: np.ndarray):
        if not QISKIT:
            return None
        qc = QuantumCircuit(self.num_qubits)
        for q in range(self.num_qubits):
            qc.h(q)

        idx = 0
        for _ in range(self.depth):
            # Single-qubit Ry layer
            for q in range(self.num_qubits):
                qc.ry(params[idx], q); idx += 1
            # Entangling gates on QUBO-active pairs
            for (i, j) in self.pairs:
                if idx < len(params):
                    qc.cx(i, j)
                    qc.rz(params[idx], j); idx += 1
                    qc.cx(i, j)
        return qc

    def random_params(self) -> np.ndarray:
        return np.random.uniform(0, 2 * np.pi, self.num_params)
