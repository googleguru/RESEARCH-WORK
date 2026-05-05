"""Configuration dataclass for the Quantum VLSI Placer."""

from dataclasses import dataclass, field


@dataclass
class QuantumPlacerConfig:
    # Algorithm selection: "qaoa" | "vqe" | "quantum_annealing"
    algorithm: str = "qaoa"

    # QUBO encoding
    bits_per_dim: int = 3           # grid resolution = 2^bits_per_dim per axis
    wl_weight: float = 1.0          # wirelength QUBO weight
    density_weight: float = 8.0     # overlap penalty weight

    # QAOA
    qaoa_depth: int = 2             # QAOA circuit depth (p)
    qaoa_shots: int = 1024
    qaoa_max_iter: int = 60

    # VQE
    vqe_ansatz: str = "hardware_efficient"  # or "problem_inspired"
    vqe_depth: int = 3
    vqe_shots: int = 512
    vqe_max_iter: int = 100

    # Quantum Annealing
    qa_num_replicas: int = 8
    qa_sweeps: int = 200
    qa_T_start: float = 5.0
    qa_T_end: float = 0.1
    qa_Gamma_start: float = 5.0
    qa_Gamma_end: float = 0.01

    # Legalization
    row_height: float = 1.0

    # Global refinement iterations after quantum solve
    refinement_iterations: int = 3
    refinement_moves: int = 50
