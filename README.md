# Quantum-based VLSI Placement Algorithms

Quantum algorithms for VLSI physical design placement using QAOA, VQE, and
Quantum Annealing. Framework architecture inspired by DREAMPlace — no deep learning.
ISPD 2019 benchmarks only.

---

## Animation — Combined 4-Panel View

| ISPD 2019 Circuit Layout | Density Map | QUBO Energy Landscape | Quantum Gradient Field |
|:------------------------:|:-----------:|:---------------------:|:----------------------:|
| ![circuit](docs/circuit_layout.gif) | ![density](docs/density_map.gif) | ![energy](docs/qubo_energy.gif) | ![gradient](docs/quantum_gradient.gif) |
| Cell layout evolution.<br>Red = macros · blue = nets | Per-bin cell-area density.<br>Dark = overflow | Smoothed QUBO energy field.<br>Dark = high-energy (crowded) | Gradient magnitude field.<br>Dark = high repulsion force |

![combined animation](docs/quantum_placement_animation.gif)

---

## Frame-by-Frame: Circuit Layout

Each frame shows the ISPD 2019 cell placement at one stage of the quantum
placement flow. White background, salmon standard cells, red macros, navy net lines.

| Iter 000 — Random Init | Iter 001 — QUBO Grid Decode | Iter 002 — Post-Legalization | Iter 003 — Refinement 1 |
|:----------------------:|:---------------------------:|:----------------------------:|:----------------------:|
| ![](docs/frames/circuit_layout_frame_000.png) | ![](docs/frames/circuit_layout_frame_001.png) | ![](docs/frames/circuit_layout_frame_002.png) | ![](docs/frames/circuit_layout_frame_003.png) |

| Iter 004 — Refinement 2 | Iter 005 — Refinement 3 | Iter 006 — Refinement 4 | Iter 007 — Final |
|:-----------------------:|:-----------------------:|:-----------------------:|:----------------:|
| ![](docs/frames/circuit_layout_frame_004.png) | ![](docs/frames/circuit_layout_frame_005.png) | ![](docs/frames/circuit_layout_frame_006.png) | ![](docs/frames/circuit_layout_frame_007.png) |

---

## Frame-by-Frame: Density Map

Shows per-bin cell-area density. White = empty bins; dark = overcrowded bins.
The density penalty drives the QUBO solver to spread cells.

| Iter 000 — Random Init | Iter 001 — QUBO Grid Decode | Iter 002 — Post-Legalization | Iter 003 — Refinement 1 |
|:----------------------:|:---------------------------:|:----------------------------:|:----------------------:|
| ![](docs/frames/density_map_frame_000.png) | ![](docs/frames/density_map_frame_001.png) | ![](docs/frames/density_map_frame_002.png) | ![](docs/frames/density_map_frame_003.png) |

| Iter 004 — Refinement 2 | Iter 005 — Refinement 3 | Iter 006 — Refinement 4 | Iter 007 — Final |
|:-----------------------:|:-----------------------:|:-----------------------:|:----------------:|
| ![](docs/frames/density_map_frame_004.png) | ![](docs/frames/density_map_frame_005.png) | ![](docs/frames/density_map_frame_006.png) | ![](docs/frames/density_map_frame_007.png) |

---

## Frame-by-Frame: QUBO Energy Landscape

Gaussian-smoothed potential field derived from the density grid.
Equivalent to DREAMPlace's Electric Potential. Dark = high-energy regions where
the QUBO Hamiltonian penalises cell overlap.

| Iter 000 — Random Init | Iter 001 — QUBO Grid Decode | Iter 002 — Post-Legalization | Iter 003 — Refinement 1 |
|:----------------------:|:---------------------------:|:----------------------------:|:----------------------:|
| ![](docs/frames/qubo_energy_frame_000.png) | ![](docs/frames/qubo_energy_frame_001.png) | ![](docs/frames/qubo_energy_frame_002.png) | ![](docs/frames/qubo_energy_frame_003.png) |

| Iter 004 — Refinement 2 | Iter 005 — Refinement 3 | Iter 006 — Refinement 4 | Iter 007 — Final |
|:-----------------------:|:-----------------------:|:-----------------------:|:----------------:|
| ![](docs/frames/qubo_energy_frame_004.png) | ![](docs/frames/qubo_energy_frame_005.png) | ![](docs/frames/qubo_energy_frame_006.png) | ![](docs/frames/qubo_energy_frame_007.png) |

---

## Frame-by-Frame: Quantum Gradient Field

Gradient magnitude of the QUBO energy landscape.
Equivalent to DREAMPlace's Electric Field. Shows the repulsion force magnitude
that drives cells away from overcrowded regions.

| Iter 000 — Random Init | Iter 001 — QUBO Grid Decode | Iter 002 — Post-Legalization | Iter 003 — Refinement 1 |
|:----------------------:|:---------------------------:|:----------------------------:|:----------------------:|
| ![](docs/frames/quantum_gradient_frame_000.png) | ![](docs/frames/quantum_gradient_frame_001.png) | ![](docs/frames/quantum_gradient_frame_002.png) | ![](docs/frames/quantum_gradient_frame_003.png) |

| Iter 004 — Refinement 2 | Iter 005 — Refinement 3 | Iter 006 — Refinement 4 | Iter 007 — Final |
|:-----------------------:|:-----------------------:|:-----------------------:|:----------------:|
| ![](docs/frames/quantum_gradient_frame_004.png) | ![](docs/frames/quantum_gradient_frame_005.png) | ![](docs/frames/quantum_gradient_frame_006.png) | ![](docs/frames/quantum_gradient_frame_007.png) |

---

## Frame-by-Frame: Combined 4-Panel

Full side-by-side view at each stage.

| Iter 000 — Random Init | Iter 001 — QUBO Grid Decode |
|:----------------------:|:---------------------------:|
| ![](docs/frames/combined_frame_000.png) | ![](docs/frames/combined_frame_001.png) |

| Iter 002 — Post-Legalization | Iter 003 — Refinement 1 |
|:----------------------------:|:-----------------------:|
| ![](docs/frames/combined_frame_002.png) | ![](docs/frames/combined_frame_003.png) |

| Iter 004 — Refinement 2 | Iter 005 — Refinement 3 |
|:-----------------------:|:-----------------------:|
| ![](docs/frames/combined_frame_004.png) | ![](docs/frames/combined_frame_005.png) |

| Iter 006 — Refinement 4 | Iter 007 — Final |
|:-----------------------:|:----------------:|
| ![](docs/frames/combined_frame_006.png) | ![](docs/frames/combined_frame_007.png) |

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
| **Macro Legalization** | Macro-legalize with fixed boundaries | Macros assigned to nearest legal row; movable cells resolve around them |
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

quantum_placement_visualization/     ← DREAMPlace-style visualization
  ├── circuit_layout_renderer.py     ← White-bg cell+net layout view
  ├── qubo_field_renderer.py         ← Density / QUBO energy / gradient views
  └── animation_generator.py         ← Frame-by-frame PNG + GIF builder

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
- **Hardware-Efficient Ansatz (HEA)**: `Ry→Rz` layers + linear CNOT chain
- **Problem-Inspired Ansatz (PIA)**: CNOT gates placed only on QUBO-active qubit pairs

### Quantum Annealing (PIMC)
- Simulates transverse-field Ising model via Path-Integral Monte Carlo
- Suzuki-Trotter decomposition with `R` replicas
- Annealing schedule: `Γ: 5.0 → 0.01`, `T: 5.0 → 0.1`

---

## QUBO Formulation

```
H_total = λ_wl · H_wirelength  +  λ_d · H_density

H_wirelength = Σ_nets  Σ_(c1,c2) ∈ clique(net)  Σ_k  w_k · x_{c1,k} · x_{c2,k}
H_density    = Σ_(c1,c2)  √(area_c1 · area_c2) · Σ_k  (x_{c1,k}·x_{c2,k} + y_{c1,k}·y_{c2,k})

Encoding: each movable cell → 2 × bits_per_dim qubits
          grid resolution   → 2^bits_per_dim bins per axis (default 8×8)
```

---

## Usage

```bash
# Generate all visualization frames (fast, no quantum hardware needed)
python generate_static_frames.py

# Full quantum placement with live visualization
python generate_ispd2019_visualization.py \
    --algorithm quantum_annealing --num_cells 150

# Real ISPD 2019 files
python run_quantum_vlsi_placement.py \
    --benchmark_dir /path/to/ispd2019 --name ispd2019_test1 --algorithm qaoa

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
    wl_weight        = 1.0,
    density_weight   = 8.0,
    qaoa_depth       = 2,
    refinement_iterations = 5,
)

placer = QuantumVLSIPlacer(netlist, die_width, die_height, cfg,
                            visualize=True, out_dir="docs")
placement = placer.run()
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

---

## Requirements

```
numpy >= 1.24
scipy >= 1.10
matplotlib >= 3.5
pillow >= 9.0
qiskit >= 1.0        (optional — falls back to classical simulation)
qiskit-aer >= 0.13   (optional)
```

```bash
pip install -r requirements.txt
```

---

## References

- Y.-C. Lu et al., "DREAMPlace: Deep Learning Toolkit-Enabled GPU Acceleration for Modern VLSI Placement," *DAC 2019*
- E. Farhi et al., "A Quantum Approximate Optimization Algorithm," *arXiv:1411.4028*
- A. Peruzzo et al., "A variational eigenvalue solver on a photonic quantum chip," *Nature Communications 2014*
- M. Suzuki, "Quantum Monte Carlo Methods," *Springer 1987* (Trotter / PIMC)
- ISPD 2019 Contest: "Initial Placement with Mixed-Size Cells"
