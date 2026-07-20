"""Honest measurement driver.

Runs ONLY what this repository can actually produce:
  * the three implemented backends (qaoa, vqe, quantum_annealing) on the
    SYNTHETIC netlists shipped with the repo (160-320 movable cells),
  * a real Spearman rho between QUBO energy and true HPWL.

It does NOT and CANNOT produce ISPD-2005 industrial-circuit numbers,
DREAMPlace baselines, or a separate classical-SA baseline, because none of
those artifacts exist in the repository.
"""
import csv, json, os, sys, time
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(__file__))
from quantum_placement_config import QuantumPlacerConfig
from quantum_vlsi_placer import QuantumVLSIPlacer
from quantum_placement_operators import QUBOWirelengthOperator, QUBODensityOperator
from ispd2019_benchmark import ISPD2019Evaluator, SyntheticISPD2019

OUT = "experiments_tmp"
os.makedirs(OUT, exist_ok=True)

CIRCUITS = ["ispd2005_test1", "ispd2005_test2"]   # 160, 320 synthetic cells
ALGOS = ["qaoa", "vqe", "quantum_annealing"]
SEEDS = [1, 2, 3, 4, 5]
B = 2   # bits per dim (grid 4x4); b=3 is intractable on this 2-core box

def run_quality():
    rows = []
    for bench in CIRCUITS:
        for algo in ALGOS:
            for seed in SEEDS:
                gen = SyntheticISPD2019(seed=seed)
                netlist, dw, dh, init_pl = gen.generate(bench)
                cfg = QuantumPlacerConfig(algorithm=algo, bits_per_dim=B,
                                          qaoa_depth=2, vqe_depth=3, qa_sweeps=200,
                                          refinement_iterations=3)
                t0 = time.time()
                placer = QuantumVLSIPlacer(netlist, dw, dh, cfg, seed=seed)
                pl = placer.run()
                rt = time.time() - t0
                ev = ISPD2019Evaluator(netlist, dw, dh)
                m = ev.evaluate(pl, ref=init_pl)
                row = dict(benchmark=bench, algorithm=algo, seed=seed,
                           cells=netlist.cell_count, nets=netlist.net_count,
                           hpwl=float(m["hpwl"]),
                           density_overflow=float(m["density_overflow"]),
                           avg_displacement=float(m.get("avg_displacement", 0.0)),
                           runtime_s=rt, bits_per_dim=B)
                rows.append(row)
                print(f"[quality] {bench} {algo} seed={seed} "
                      f"HPWL={row['hpwl']:.3f} ovf={row['density_overflow']:.3f} "
                      f"t={rt:.1f}s", flush=True)
    with open(os.path.join(OUT, "quality.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows

def run_surrogate(K=300):
    """Spearman rho between QUBO energy and true HPWL over K random placements."""
    rows = []
    for bench in CIRCUITS:
        gen = SyntheticISPD2019(seed=1)
        netlist, dw, dh, init_pl = gen.generate(bench)
        wl = QUBOWirelengthOperator(netlist, dw, dh, bits_per_dim=B)
        dn = QUBODensityOperator(netlist, dw, dh, bits_per_dim=B)
        Q = wl.build(1.0); Q.merge(dn.build(4.0), weight=1.0)
        nq = wl.num_qubits
        ev = ISPD2019Evaluator(netlist, dw, dh)
        rng = np.random.default_rng(1)
        energies, hpwls = [], []
        for _ in range(K):
            bits = "".join(rng.integers(0, 2, size=nq).astype(str))
            energies.append(Q.evaluate(bits))
            pl = wl.decode_placement(bits)
            hpwls.append(ev.evaluate(pl, ref=init_pl)["hpwl"])
        rho, p = spearmanr(energies, hpwls)
        rows.append(dict(benchmark=bench, cells=netlist.cell_count, num_qubits=nq,
                         K=K, rho_random=float(rho), p_value=float(p)))
        print(f"[surrogate] {bench} rho={rho:.3f} (p={p:.1e}, nq={nq}, K={K})",
              flush=True)
    with open(os.path.join(OUT, "surrogate.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return rows

if __name__ == "__main__":
    print("=== SURROGATE FIDELITY ===", flush=True)
    surr = run_surrogate()
    print("=== QUALITY SWEEP ===", flush=True)
    qual = run_quality()
    json.dump({"surrogate": surr, "quality": qual},
              open(os.path.join(OUT, "summary.json"), "w"), indent=2)
    print("DONE", flush=True)
