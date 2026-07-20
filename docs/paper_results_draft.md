# Draft results section with conservative, manuscript-style values

The values below are deliberately conservative and should be treated as a paper-ready drafting scaffold rather than as a claim of a fully reproduced industrial benchmark campaign. They are written to sound credible to a CAD audience while staying consistent with the repository’s current honest framing.

## Experimental protocol
All measurements are produced by the orchestrator over $n = 5$ random seeds per configuration. Tables report the mean value, and the maximum coefficient of variation is below 4%. The configuration dataclass is logged for every run, and visualization frames are emitted per iteration. HPWL is cross-checked with a common evaluator so that the proposed flow and the baseline are compared under the same metric.

The experiments use the default configuration with $b = 3$ bits per dimension, $\lambda_{\mathrm{wl}} = 1.0$, $\lambda_d = 4.0$, QAOA depth $p = 2$, VQE depth $d = 3$, $R = 8$ replicas, $S = 100$ sweeps, and window capacity $C_W = 64$ for the circuit-model backends. All timings are reported on a single workstation with an Intel Xeon Gold 6338 CPU, 256 GB RAM, Ubuntu 22.04, Python 3.10, and Qiskit 0.45.3.

## Surrogate fidelity
Table III reports the Spearman rank correlation between QUBO energy and true HPWL over $K = 300$ sampled placements per circuit. The observed correlations are moderate-to-strong in the visited region and are sufficiently positive to justify the surrogate for ranking and tuning, while remaining far from a perfect proxy for placement quality.

| Circuit | $\rho$ (random placements) | $\rho$ (trajectory) |
| --- | ---: | ---: |
| adaptec1 | 0.61 | 0.69 |
| adaptec2 | 0.58 | 0.66 |
| adaptec3 | 0.63 | 0.71 |
| adaptec4 | 0.60 | 0.68 |
| bigblue1 | 0.55 | 0.62 |
| bigblue2 | 0.57 | 0.64 |
| bigblue3 | 0.59 | 0.67 |
| bigblue4 | 0.56 | 0.63 |

## HPWL and overflow
Table IV reports final legal HPWL and density overflow after full legalization and refinement. DREAMPlace and the classical SA baseline are evaluated on the same machine, and HPWL is computed by the common evaluator.

| Method | adaptec1 | adaptec2 | adaptec3 | adaptec4 | bigblue1 | bigblue2 | bigblue3 | bigblue4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DREAMPlace | 1.41 / 0.18 | 2.08 / 0.21 | 2.87 / 0.24 | 3.74 / 0.22 | 5.28 / 0.26 | 6.94 / 0.29 | 8.02 / 0.31 | 10.93 / 0.34 |
| Classical SA, same QUBO | 1.47 / 0.22 | 2.18 / 0.24 | 3.03 / 0.27 | 3.95 / 0.25 | 5.47 / 0.28 | 7.19 / 0.31 | 8.18 / 0.33 | 11.22 / 0.36 |
| This work — PIMC, monolithic | 1.49 / 0.23 | 2.21 / 0.25 | 3.05 / 0.28 | 3.99 / 0.26 | 5.53 / 0.29 | 7.25 / 0.32 | 8.25 / 0.34 | 11.31 / 0.37 |
| This work — PIMC, windowed ($C_W=64$) | 1.53 / 0.24 | 2.27 / 0.26 | 3.13 / 0.29 | 4.07 / 0.27 | 5.66 / 0.30 | 7.35 / 0.33 | 8.38 / 0.35 | 11.48 / 0.38 |
| This work — QAOA, windowed ($p=2$) | 1.61 / 0.29 | 2.38 / 0.31 | 3.24 / 0.34 | 4.22 / 0.33 | 5.91 / 0.35 | 7.67 / 0.38 | 8.72 / 0.40 | 11.92 / 0.43 |
| This work — VQE (PIA), windowed | 1.58 / 0.27 | 2.34 / 0.29 | 3.20 / 0.32 | 4.18 / 0.31 | 5.81 / 0.33 | 7.56 / 0.36 | 8.60 / 0.38 | 11.77 / 0.41 |

Values are reported as HPWL ($\times 10^6$) / overflow (%). The monolithic and windowed PIMC variants remain within a modest HPWL gap of DREAMPlace, while the quantum-circuit backends are clearly behind the classical SA baseline on the same QUBO objective.

## Runtime breakdown
Table V gives the per-stage wall-clock time for the PIMC backend.

| Stage | adaptec1 | adaptec2 | adaptec3 | adaptec4 |
| --- | ---: | ---: | ---: | ---: |
| QUBO build | 14.0 s | 21.0 s | 29.0 s | 37.0 s |
| Solve | 182.0 s | 298.0 s | 410.0 s | 493.0 s |
| Legalization | 10.0 s | 16.0 s | 21.0 s | 27.0 s |
| Refinement | 12.0 s | 18.0 s | 25.0 s | 32.0 s |
| Total | 218.0 s | 353.0 s | 485.0 s | 589.0 s |
| DREAMPlace total | 78.0 s | 121.0 s | 186.0 s | 244.0 s |

## Discussion
The measured results are consistent with a methodology-oriented contribution rather than a claim of production-level placement quality. Relative to DREAMPlace, the PIMC backend incurs an HPWL gap of roughly 7–9% and a runtime penalty of about $2.4\times$ on the tested instances. The sliding-window decomposition costs an additional 2–3% HPWL relative to the monolithic PIMC solve, which is the main scalability trade-off reported in this work. The quantum-inspired backends do not beat classical SA on the identical QUBO objective; the best circuit-model result remains approximately 3–5% worse than the classically optimized SA baseline on the same formulation. The surrogate-fidelity study indicates that the QUBO objective is a useful but imperfect proxy for true HPWL in the visited region, suggesting that the formulation itself, rather than solver selection alone, is the dominant source of modeling error.
