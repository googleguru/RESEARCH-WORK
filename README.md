# Quantum-based VLSI Placement Algorithms

Quantum algorithms for VLSI physical design placement using QAOA, VQE, and
Quantum Annealing. The repository is best understood as a quantum-inspired
placement prototype for research and education: it provides a modular workflow
for encoding placement objectives into QUBO form, exploring solver behavior on
small synthetic netlists, and visualizing intermediate placements. It is not
positioned as a production-ready replacement for industrial placers such as
DREAMPlace, Cadence Innovus, or Synopsys ICC.

---

## Research Positioning

This project is intentionally scoped as a proof-of-concept for quantum-inspired
placement research rather than a claim of industrial-scale competitiveness.
The main value lies in three areas:

- A modular pipeline for translating placement objectives into QUBO form.
- A reproducible workflow for testing QAOA, VQE, and simulated annealing ideas
  on small, synthetic, ISPD-inspired circuits.
- An educational visualization stack that makes solver behavior and placement
  dynamics more interpretable.

### What the repository does well
- Implements a complete end-to-end prototype flow from QUBO construction to
  legalization and refinement.
- Supports reproducible experiments with a deterministic synthetic generator.
- Exposes solver behavior through visualizations and metrics.

### What it does not claim
- It does not claim to outperform commercial placers on large industrial designs.
- It does not claim to be directly deployable on current quantum hardware at
  realistic VLSI scale.
- It does not attempt to reproduce the full fidelity of state-of-the-art
  analytical placement engines.

### Suggested framing for a paper or report
- Position the work as a methodological prototype for exploring quantum-inspired
  optimization in placement.
- Emphasize modularity, reproducibility, and visualization over absolute
  placement quality.
- Pair the results with clear scalability limits and future directions.
- Frame the contribution as complementary to commercial physical-design flows,
  especially for algorithmic experimentation and educational use.

---

## Animation — Combined 4-Panel View

| ISPD 2019 Circuit Layout | Density Map | QUBO Energy Landscape | Quantum Gradient Field |
|:------------------------:|:-----------:|:---------------------:|:----------------------:|
| ![circuit](docs/circuit_layout.gif) | ![density](docs/density_map.gif) | ![energy](docs/qubo_energy.gif) | ![gradient](docs/quantum_gradient.gif) |
| Cell layout evolution.<br>Red = macros · blue = nets | Per-bin cell-area density.<br>Dark = overflow | Smoothed QUBO energy field.<br>Dark = high-energy (crowded) | Gradient magnitude field.<br>Dark = high repulsion force |

![combined animation](docs/quantum_placement_animation.gif)

---

## Frame-by-Frame: Circuit Layout

Each frame shows a synthetic, ISPD-inspired cell placement at one stage of the
quantum placement flow. White background, salmon standard cells, red macros,
navy net lines.

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

### Reproducibility notes
- Use the same seed across runs for comparable results.
- The default workflow uses synthetic, ISPD-inspired netlists for portability.
- For external benchmark files, supply a directory with Bookshelf-style inputs.
- Install dependencies with `pip install -r requirements.txt`.
- Report the algorithm, seed, grid resolution, and refinement iterations when sharing results.

### Experimental protocol
1. Generate a small synthetic netlist with a fixed seed.
2. Run a single solver configuration and record HPWL, overlap, and boundary violation metrics.
3. Repeat with a second seed only when studying stability or sensitivity.
4. Interpret results as a methodological study rather than a claim of industrial performance.

### Structured experiment logging
The repository now includes a lightweight experiment runner in [run_experiment_suite.py](run_experiment_suite.py) and [quantum_placement_experiments/experiment_runner.py](quantum_placement_experiments/experiment_runner.py). It writes CSV and JSON logs that can be used to build tables for runtime, quality, and ablation studies.

### Results generation helpers
Use [generate_results_tables.py](generate_results_tables.py) to create a LaTeX-quality table scaffold from experiment logs, and [generate_ablation_sweeps.py](generate_ablation_sweeps.py) to create a parameter grid for ablation studies. A short paper-ready results scaffold is available in [docs/results_scaffold.md](docs/results_scaffold.md), and a manuscript-style placeholder table set is in [docs/paper_results_tables.md](docs/paper_results_tables.md).

See [docs/academic_revision_note.md](docs/academic_revision_note.md) for a concise, paper-style framing of the project’s scope and contributions.

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

## Measured results snapshot

The current repository can verify the following values from its own synthetic/demo workflow. The requested ISPD 2005 and DREAMPlace comparisons are not available in this workspace because no official benchmark suite files or DREAMPlace baseline artifacts are bundled here.

| Quantity | Measured value | Evidence |
|---|---:|---|
| Surrogate fidelity $\rho$ (random placements), ispd2005_test1 | 0.0545 | [experiments_tmp/surrogate.csv](experiments_tmp/surrogate.csv) |
| Surrogate fidelity $\rho$ (random placements), ispd2005_test2 | -0.0664 | [experiments_tmp/surrogate.csv](experiments_tmp/surrogate.csv) |
| Surrogate fidelity $\rho$ (trajectory) | Not measured in this repository | — |
| Sample placement HPWL (qaoa, ispd2019_test1, seed 1) | 114.03 | [experiments_demo/experiments.csv](experiments_demo/experiments.csv) |
| Sample placement density overflow (qaoa, ispd2019_test1, seed 1) | 7.41% | [experiments_demo/experiments.csv](experiments_demo/experiments.csv) |
| Sample runtime (qaoa, ispd2019_test1, seed 1) | 6.17 s | [experiments_demo/experiments.csv](experiments_demo/experiments.csv) |
| Synthetic QAOA sweep HPWL (seed 1) | 1881.46 | [experiments_tmp/sweep.log](experiments_tmp/sweep.log) |
| Synthetic QAOA sweep overflow (seed 1) | 4.06% | [experiments_tmp/sweep.log](experiments_tmp/sweep.log) |
| Synthetic QAOA sweep HPWL (seed 2) | 2016.37 | [experiments_tmp/sweep.log](experiments_tmp/sweep.log) |
| Synthetic QAOA sweep overflow (seed 2) | 4.41% | [experiments_tmp/sweep.log](experiments_tmp/sweep.log) |
| Synthetic QAOA sweep HPWL (seed 3) | 1852.96 | [experiments_tmp/sweep.log](experiments_tmp/sweep.log) |
| Synthetic QAOA sweep overflow (seed 3) | 2.88% | [experiments_tmp/sweep.log](experiments_tmp/sweep.log) |
| HPWL gap vs. DREAMPlace | N/A (not available in this workspace) | No DREAMPlace baseline or legal placement logs are included |
| Runtime ratio vs. DREAMPlace | N/A (not available in this workspace) | No DREAMPlace baseline or runtime trace is included |
| Windowed vs. monolithic PIMC gap | N/A (not measured in this repository) | No monolithic/windowed sweep output is bundled |

These values are suitable for a transparent methodology section, but they should not be presented as a claim of industrial-scale competitiveness against DREAMPlace or a complete ISPD 2005 benchmark study.

---

## Benchmarks

The repository does not ship the official ISPD 2019 or ISPD 2005 contest suites.
The default path is a small synthetic benchmark generator that creates reproducible,
illustrative netlists. If you have your own Bookshelf-style files, pass them with
`--benchmark_dir` and `--name`.

| Name | Purpose |
|------|---------|
| ispd2019_test1 | Small synthetic example |
| ispd2019_test2 | Medium synthetic example |
| ispd2019_test3 | Larger synthetic example |
| ispd2019_test4 | Large synthetic example |
| ispd2005_test1 | Additional synthetic alias |
| ispd2005_test2 | Additional synthetic alias |
| ispd2005_test3 | Additional synthetic alias |
| ispd2005_test4 | Additional synthetic alias |

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
- Bookshelf-style placement files are supported when provided by the user.
- The repo uses a synthetic, ISPD-inspired generator by default for reproducible experiments.
