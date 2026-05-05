"""
Quantum Annealing Placement — simulates a transverse-field Ising model annealing
schedule to solve the VLSI placement QUBO.

No quantum hardware required: simulates the annealing dynamics classically
using path-integral Monte Carlo (PIMC) with a Suzuki-Trotter expansion.
This mirrors what D-Wave hardware does, making results portable.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AnnealingResult:
    placement: dict
    energy: float
    schedule_steps: int
    convergence: list = field(default_factory=list)


class QuantumAnnealer:
    """
    Path-Integral Monte Carlo simulation of quantum annealing for VLSI QUBO.

    Parameters
    ----------
    qubo_Q      : QUBO dict {(i,j): coeff}.
    num_qubits  : Number of binary variables.
    num_replicas: Suzuki-Trotter replicas (Trotter number).
    """

    def __init__(self, qubo_Q: dict, num_qubits: int,
                 num_replicas: int = 8, seed: int = 0):
        self.Q = qubo_Q
        self.n = num_qubits
        self.R = num_replicas
        self.rng = np.random.default_rng(seed)
        self._best_bits: Optional[str] = None
        self._best_energy = float("inf")

    # ------------------------------------------------------------------ public

    def run(self, num_sweeps: int = 200,
            T_start: float = 5.0, T_end: float = 0.1,
            Gamma_start: float = 5.0, Gamma_end: float = 0.01) -> AnnealingResult:
        """
        Anneal from high transverse field (Gamma_start) to low (Gamma_end)
        while cooling temperature T_start → T_end.
        """
        # Initialise random spin configurations for all replicas
        spins = self.rng.choice([0, 1], size=(self.R, self.n))
        convergence = []

        schedules = np.linspace(0, 1, num_sweeps)

        for step_idx, t in enumerate(schedules):
            T = T_start * (T_end / T_start) ** t
            Gamma = Gamma_start * (Gamma_end / Gamma_start) ** t
            J_perp = -0.5 * self.R * T * np.log(
                np.tanh(Gamma / (self.R * T + 1e-12))
            )

            for r in range(self.R):
                self._sweep_replica(spins, r, T, J_perp)

            # Track best across all replicas every 10 steps
            if step_idx % 10 == 0:
                for r in range(self.R):
                    bits = "".join(str(int(b)) for b in spins[r])
                    e = self._eval_bits(bits)
                    if e < self._best_energy:
                        self._best_energy = e
                        self._best_bits = bits
                convergence.append(self._best_energy)

        bits = self._best_bits or "0" * self.n
        return AnnealingResult(
            placement={"_bitstring": bits},
            energy=self._best_energy,
            schedule_steps=num_sweeps,
            convergence=convergence,
        )

    # ------------------------------------------------------------------ internals

    def _sweep_replica(self, spins: np.ndarray, r: int,
                       T: float, J_perp: float):
        """One Metropolis sweep over all qubits in replica r."""
        R, n = self.R, self.n
        perm = self.rng.permutation(n)

        for q in perm:
            delta_E = self._local_energy_delta(spins, r, q)

            # Inter-replica coupling (periodic boundary)
            r_prev = (r - 1) % R
            r_next = (r + 1) % R
            coupling = J_perp * (
                (1 if spins[r_prev, q] == spins[r, q] else -1) +
                (1 if spins[r_next, q] == spins[r, q] else -1)
            )
            delta_total = delta_E + coupling

            if delta_total < 0 or self.rng.random() < np.exp(-delta_total / (T + 1e-12)):
                spins[r, q] ^= 1  # flip

    def _local_energy_delta(self, spins: np.ndarray, r: int, q: int) -> float:
        """Energy change from flipping qubit q in replica r."""
        delta = 0.0
        current = spins[r, q]
        flipped = 1 - current
        for (i, j), coeff in self.Q.items():
            if i == j == q:
                delta += coeff * (flipped - current)
            elif i == q:
                delta += coeff * (flipped - current) * spins[r, j]
            elif j == q:
                delta += coeff * spins[r, i] * (flipped - current)
        return delta

    def _eval_bits(self, bits: str) -> float:
        cost = 0.0
        for (i, j), coeff in self.Q.items():
            if i < len(bits) and j < len(bits):
                if i == j:
                    cost += coeff * int(bits[i])
                else:
                    cost += coeff * int(bits[i]) * int(bits[j])
        return cost
