"""Sparse QUBO matrix builder — combines wirelength and density operators."""

import numpy as np
from itertools import combinations


class QUBOMatrix:
    """
    Sparse QUBO dict Q where cost = x^T Q x.
    Keys are (i, j) with i <= j.
    """

    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.Q: dict[tuple[int, int], float] = {}

    # ------------------------------------------------------------------ ops

    def add(self, i: int, j: int, coeff: float):
        if coeff == 0.0:
            return
        key = (min(i, j), max(i, j))
        self.Q[key] = self.Q.get(key, 0.0) + coeff

    def scale(self, factor: float):
        self.Q = {k: v * factor for k, v in self.Q.items()}

    def merge(self, other: "QUBOMatrix", weight: float = 1.0):
        for (i, j), coeff in other.Q.items():
            self.add(i, j, weight * coeff)

    # ------------------------------------------------------------------ eval

    def evaluate(self, bitstring: str) -> float:
        bits = [int(b) for b in bitstring]
        cost = 0.0
        for (i, j), coeff in self.Q.items():
            if i == j:
                cost += coeff * bits[i]
            else:
                cost += coeff * bits[i] * bits[j]
        return cost

    def to_dense(self) -> np.ndarray:
        M = np.zeros((self.num_qubits, self.num_qubits))
        for (i, j), v in self.Q.items():
            M[i, j] += v
        return M

    def nnz(self) -> int:
        return len(self.Q)
