# Quantum-based VLSI Placement Algorithms

Quantum algorithms for VLSI physical design placement using QAOA, VQE, and
Quantum Annealing. Framework architecture inspired by DREAMPlace — no deep learning.
ISPD 2019 benchmarks only.

---

## Animation

| ISPD 2019 Circuit | Density Map | QUBO Energy Landscape | Quantum Gradient Field |
|:-----------------:|:-----------:|:---------------------:|:----------------------:|
| ![circuit](docs/circuit_layout.gif) | ![density](docs/density_map.gif) | ![energy](docs/qubo_energy.gif) | ![gradient](docs/quantum_gradient.gif) |
| Cell placement evolving over QAOA iterations. Red = macros, blue = routing. | Per-bin cell-area density. Dark = overflow. Drives QUBO density penalty. | QUBO Hamiltonian energy landscape. Dark = high energy regions (crowded). | Quantum gradient field guiding cells away from high-density regions. |

> Run `python run_quantum_vlsi_placement.py` to generate placement animations.

---

## Reference Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│  2-Stage Quantum Global Placement         Legalization         Detailed Placement            │
│                                                                                              │
│  ┌───────┐                                                     ┌─────────────────────┐      │
│  │ Input │                                                     │   Local Reordering  │      │
│  └───┬───┘                                                     └──────────┬──────────┘      │
│      │                                                                    │                  │
│      ▼                                ┌──────────────────┐   ┌──────────▼──────────┐      │
│  ┌──────────────┐    ◄────────────────│ Fix Macros       │   │  Independent Set    │      │
│  │Initialization│                     │ & Reset          │   │  Matching (Quantum) │      │
│  └──────┬───────┘                     └──────────────────┘   └──────────┬──────────┘      │
│         │                                      ▲                         │                  │
│         ▼                                      │ N                       ▼                  │
│  ┌──────────────┐                      ┌───────┴────────┐   ┌──────────────────────┐      │
│  │  Build QUBO  │◄──────────────────── │  Macro Fixed?  │   │    Global Swap       │      │
│  │  Objective   │                      └───────┬────────┘   └──────────┬───────────┘      │
│  └──────┬───────┘                              │ Y                      │                  │
│         │                              ┌───────▼────────┐   ┌──────────▼──────────┐      │
│         ▼                              │    Quantum      │   │   Local Reordering  │      │
│  ┌──────────────┐  ┌─────────────┐    │    Macro        │   └──────────┬──────────┘      │
│  │Quantum Solve │  │Fix Macros & │    │  Legalization   │              │                  │
│  │QAOA/VQE/QA   │  │   Reset     │    └────────┬────────┘   ┌──────────▼──────────┐      │
│  └──────┬───────┘  └─────────────┘             │            │       Output        │      │
│         │                                        ▼            └─────────────────────┘      │
│         ▼                            ┌──────────────────┐                                  │
│  ┌──────────────┐    N    ┌────┐     │ Tetris           │                                  │
│  │Update Grid   │◄────────┤Conv│     │ Legalization     │                                  │
│  │  Positions   │         │erg │     └────────┬─────────┘                                  │
│  └──────────────┘         │ e? │              │                                             │
│                       Y   └──┬─┘     ┌────────▼─────────┐                                 │
│                         ──►  │       │ Abacus Refinement│                                  │
│                              └──────►│ Critical-Net     │                                  │
│                                      │ Refinement       │                                  │
│                                      └──────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Flow Description

| Stage | DREAMPlace Equivalent | Quantum Implementation |
|-------|-----------------------|------------------------|
| **Initialization** | Random / analytical init | Random grid assignment over `2^bits_per_dim` bins |
| **Build QUBO Objective** | Compute wirelength + density gradient | `QUBOWirelengthOperator` + `QUBODensityOperator` → combined sparse QUBO |
| **Quantum Solve** | Nesterov gradient descent | QAOA (COBYLA outer loop) / VQE (HEA or PIA) / Quantum Annealing (PIMC/Trotter) |
| **Update Grid Positions** | Cell coordinate update via gradient step | Decode best-energy bitstring → `(x, y)` via `QUBOWirelengthOperator.decode_placement` |
| **Macro Legalization** | Macro macro-legalize with fixed boundaries | Macros assigned to nearest legal row, then movable cells resolve around them |
| **Tetris Legalization** | Tetris-style left-scan legalizer | `QuantumLegalizer` — row-based scan, cursor-x advance per row |
| **Abacus Refinement** | Abacus min-displacement refinement | Critical-net centroid pull — top-10 nets by HPWL refined iteratively |
| **Independent Set Matching** | Optimal matching within independent sets | Pairwise swap evaluated by HPWL delta; quantum-assisted for large sets |
| **Global Swap** | Global cell pair swap | QUBO-guided cell swap: accept if energy decreases |
| **Local Reordering** | Single-segment reordering | Within-row reorder by net connectivity weight |

---

## Project Structure

```
quantum_placement_database/          ← VLSI netlist DB + sparse QUBO matrix
  ├── netlist.py                     ← QuantumNetlist (cells, nets, pins)
  └── qubo_matrix.py                 ← QUBOMatrix — sparse {(i,j): coeff} dict

quantum_placement_operators/         ← DREAMPlace-style quantum operators
  ├── qubo_wirelength.py             ← Net clique expansion → wirelength QUBO
  ├── qubo_density.py                ← Bin-overflow penalty → density QUBO
  └── quantum_legalizer.py           ← Row-scan legalizer (Tetris + Abacus)

quantum_placement_algorithms/        ← Core quantum solvers
  ├── qaoa/qaoa_placer.py            ← p-layer QAOA + COBYLA optimizer
  ├── vqe/vqe_placer.py             ← VQE + Hardware-Efficient Ansatz
  └── quantum_annealing/annealer.py  ← PIMC Suzuki-Trotter quantum annealing

quantum_placement_ansatz/            ← Parameterised quantum circuit library
  ├── hardware_efficient.py          ← Ry-Rz + linear CNOT chain
  └── problem_inspired.py            ← QUBO-connectivity-driven entanglers

quantum_placement_metrics/           ← Placement quality evaluation
  └── placement_metrics.py           ← HPWL, overlap area, boundary violation

quantum_placement_config/            ← Hyperparameter configuration
  └── placer_config.py               ← QuantumPlacerConfig dataclass

quantum_vlsi_placer/                 ← Main placement engine
  └── quantum_placer.py              ← QuantumVLSIPlacer (full flow orchestrator)

ispd2019_benchmark/                  ← ISPD 2019 benchmarks only
  ├── benchmark_loader.py            ← Bookshelf format (.nodes/.nets/.pl/.scl)
  ├── benchmark_evaluator.py         ← HPWL, density overflow, displacement
  └── synthetic_generator.py         ← Synthetic ISPD 2019-style circuits
```

---

## Algorithms

### QAOA — Quantum Approximate Optimization Algorithm
- `p`-layer alternating problem + mixer Hamiltonian circuit
- Problem Hamiltonian encodes combined wirelength + density QUBO
- Classical outer loop: COBYLA (gradient-free, hardware-noise tolerant)
- Placement decoded from highest-frequency bitstring measurement

### VQE — Variational Quantum Eigensolver
- Minimises `⟨ψ(θ)|H_QUBO|ψ(θ)⟩` over parameterised ansatz
- Two ansatz options:
  - **Hardware-Efficient (HEA)**: `Ry→Rz` layers + linear CNOT chain
  - **Problem-Inspired (PIA)**: CNOT gates placed only on QUBO-active qubit pairs
- Optimizer: COBYLA / SPSA

### Quantum Annealing (PIMC)
- Simulates transverse-field Ising model via Path-Integral Monte Carlo
- Suzuki-Trotter decomposition with `R` replicas
- Annealing schedule: `Γ: 5.0 → 0.01`, `T: 5.0 → 0.1`
- Inter-replica coupling drives tunnelling out of local minima

---

## QUBO Formulation

```
H_total = λ_wl · H_wirelength  +  λ_d · H_density

H_wirelength = Σ_{nets} Σ_{(c1,c2) ∈ clique(net)} Σ_k  w_k · x_{c1,k} · x_{c2,k}
H_density    = Σ_{(c1,c2)} √(area_c1 · area_c2) · Σ_k  (x_{c1,k}·x_{c2,k} + y_{c1,k}·y_{c2,k})

Encoding: each movable cell → 2 × bits_per_dim qubits
          grid resolution   → 2^bits_per_dim bins per axis
```

---

## Usage

```bash
# Synthetic ISPD 2019 benchmark (no files needed)
python run_quantum_vlsi_placement.py

# Real ISPD 2019 benchmark files (Bookshelf format)
python run_quantum_vlsi_placement.py \
    --benchmark_dir /path/to/ispd2019 \
    --name ispd2019_test1 \
    --algorithm qaoa

# Algorithm options: qaoa | vqe | quantum_annealing
python run_quantum_vlsi_placement.py --algorithm vqe --vqe_depth 4
python run_quantum_vlsi_placement.py --algorithm quantum_annealing --qa_sweeps 500

# Run test suite
python test_quantum_vlsi_placement.py
```

### Configuration

```python
from quantum_placement_config import QuantumPlacerConfig
from quantum_vlsi_placer import QuantumVLSIPlacer

cfg = QuantumPlacerConfig(
    algorithm        = "qaoa",      # qaoa | vqe | quantum_annealing
    bits_per_dim     = 3,           # grid = 2^3 = 8 bins per axis
    wl_weight        = 1.0,         # wirelength QUBO weight (λ_wl)
    density_weight   = 8.0,         # overlap penalty weight (λ_d)
    qaoa_depth       = 2,           # QAOA p-layers
    qaoa_max_iter    = 60,
    refinement_iterations = 3,      # critical-net refinement passes
)

placer = QuantumVLSIPlacer(netlist, die_width, die_height, cfg)
placement = placer.run()            # returns {cell_id: (x, y)}
```

---

## ISPD 2019 Benchmarks

| Benchmark | Cells (approx.) | Nets |
|-----------|----------------|------|
| ispd2019_test1 | 10 K | 15 K |
| ispd2019_test2 | 25 K | 37 K |
| ispd2019_test3 | 50 K | 75 K |
| ispd2019_test4 | 100 K | 150 K |
| ispd2019_test5 | 200 K | 300 K |
| ispd2019_test6 | 500 K | 750 K |
| ispd2019_test7 | 1 M | 1.5 M |
| ispd2019_test8 | 2 M | 3 M |
| ispd2019_test9 | 5 M | 7.5 M |

Cell format: Bookshelf (`.nodes` `.nets` `.pl` `.scl` `.wts`)

---

## Requirements

```
numpy >= 1.24
scipy >= 1.10
qiskit >= 1.0        (optional — falls back to classical simulation)
qiskit-aer >= 0.13   (optional)
matplotlib >= 3.5    (for visualization)
pillow >= 9.0        (for image processing)
```

```bash
pip install -r requirements.txt
```

### Docker Setup

For environments where dependencies are difficult to install (e.g., GitHub Codespaces), use Docker:

```bash
# Build and run with Docker
./run_docker.sh

# Or use docker-compose
docker-compose up

# Or manually:
docker build -t quantum-vlsi-placement .
docker run -v $(pwd)/output:/app/output quantum-vlsi-placement
```

The Docker setup includes all required dependencies and generates DREAMPlace-style visualizations in the `output/` directory.

---

## References

- Y.-C. Lu et al., "DREAMPlace: Deep Learning Toolkit-Enabled GPU Acceleration for Modern VLSI Placement," *DAC 2019*
- E. Farhi et al., "A Quantum Approximate Optimization Algorithm," *arXiv:1411.4028*
- A. Peruzzo et al., "A variational eigenvalue solver on a photonic quantum chip," *Nature Communications 2014*
- M. Suzuki, "Quantum Monte Carlo Methods," *Springer 1987* (Trotter decomposition / PIMC)
- ISPD 2019 Contest: "Initial Placement with Mixed-Size Cells"
