# Paper-ready results tables

The repository currently has logged runs for surrogate-fidelity checks and a small synthetic-style quality sweep. The ISPD 2005 benchmark suite and DREAMPlace baseline outputs are not present in this workspace, so the tables below use explicit "N/A" placeholders rather than fabricating numbers.

## Table IV. HPWL and density overflow

| Method | adaptec1 | adaptec2 | adaptec3 | adaptec4 | bigblue1 | bigblue2 | bigblue3 | bigblue4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DREAMPlace (measured) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Classical SA, same QUBO | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| This work — PIMC, monolithic | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| This work — PIMC, windowed (CW) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| This work — QAOA, windowed (p=2) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| This work — VQE (PIA), windowed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## Table V. Per-stage wall-clock time (s), PIMC backend

| Stage | adaptec1 | adaptec2 | adaptec3 | adaptec4 | bigblue1 | bigblue2 | bigblue3 | bigblue4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUBO build | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Solve | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Legalization | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Refinement | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| Total | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| DREAMPlace total (same machine) | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |

## Logged repository evidence currently available

- Surrogate fidelity: $\rho = 0.0545$ on ispd2005_test1 and $\rho = -0.0664$ on ispd2005_test2 from [experiments_tmp/surrogate.csv](../experiments_tmp/surrogate.csv)
- Sample quality sweep: QAOA on a synthetic-style benchmark produced HPWL around 1.88e3 and overflow around 4.06% at seed 1 from [experiments_tmp/sweep.log](../experiments_tmp/sweep.log)
