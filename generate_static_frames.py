"""
generate_static_frames.py
==========================
Generates all DREAMPlace-style visualization frames for the Quantum VLSI
Placement project WITHOUT running quantum circuits.

Simulates 8 placement stages (random → converged) using fast heuristic
moves so the script completes quickly in any environment.

Output (docs/frames/ + docs/):
  frames/circuit_layout_frame_{000..007}.png
  frames/density_map_frame_{000..007}.png
  frames/qubo_energy_frame_{000..007}.png
  frames/quantum_gradient_frame_{000..007}.png
  frames/combined_frame_{000..007}.png
  circuit_layout.gif / density_map.gif / qubo_energy.gif / quantum_gradient.gif
  quantum_placement_animation.gif
  quantum_placement_result.png
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
from ispd2019_benchmark import SyntheticISPD2019
from quantum_placement_operators import QuantumLegalizer
from quantum_placement_metrics import QuantumPlacementMetrics
from quantum_placement_visualization import PlacementAnimationGenerator


# ------------------------------------------------------------------ placement stages

def random_placement(netlist, die_w, die_h, rng):
    pl = {}
    for cid, c in netlist.cells.items():
        x = rng.uniform(0, max(0.1, die_w - c["width"]))
        y = rng.uniform(0, max(0.1, die_h - c["height"]))
        pl[cid] = (float(x), float(y))
    return pl


def grid_placement(netlist, die_w, die_h, grid_bins=8):
    """Decode a random bitstring through the grid — simulates QUBO decode."""
    rng = np.random.default_rng(0)
    cell_w = die_w / grid_bins
    cell_h = die_h / grid_bins
    pl = {}
    for cid, c in netlist.cells.items():
        bx = rng.integers(0, grid_bins)
        by = rng.integers(0, grid_bins)
        x  = min(bx * cell_w, die_w - c["width"])
        y  = min(by * cell_h, die_h - c["height"])
        pl[cid] = (max(0.0, x), max(0.0, y))
    return pl


def gravity_step(placement, netlist, die_w, die_h, alpha=0.25, rng=None):
    """Move each cell toward its net centroid by alpha fraction."""
    if rng is None:
        rng = np.random.default_rng(42)
    refined = dict(placement)
    for cid in netlist.movable_cells:
        if cid not in placement:
            continue
        # Collect neighbour centroids
        nx, ny, cnt = 0.0, 0.0, 0
        for net_id, pin_name in netlist.cells[cid].get("pins", []) \
                if isinstance(netlist.cells[cid].get("pins"), list) else []:
            for other, _ in netlist.nets.get(net_id, {}).get("pins", []):
                if other != cid and other in placement:
                    nx += placement[other][0]
                    ny += placement[other][1]
                    cnt += 1
        if cnt == 0:
            continue
        cx, cy = nx / cnt, ny / cnt
        x, y = placement[cid]
        w, h = netlist.cells[cid]["width"], netlist.cells[cid]["height"]
        noise = rng.normal(0, 0.5)
        new_x = max(0.0, min(x + alpha * (cx - x) + noise, die_w - w))
        new_y = max(0.0, min(y + alpha * (cy - y) + noise, die_h - h))
        refined[cid] = (new_x, new_y)
    return refined


def build_net_index(netlist):
    """Return {cell_id: [(net_id, [other_cell_ids])]} for fast lookup."""
    idx = {}
    for net_id, net_info in netlist.nets.items():
        pins = [c for c, _ in net_info["pins"]]
        for c in pins:
            others = [o for o in pins if o != c]
            if c not in idx:
                idx[c] = []
            idx[c].append((net_id, others))
    return idx


def gravity_step_fast(placement, netlist, net_idx, die_w, die_h,
                       alpha=0.30, noise_std=0.3, rng=None):
    """Fast gravity pull using pre-built net index."""
    if rng is None:
        rng = np.random.default_rng(42)
    refined = dict(placement)
    for cid in netlist.movable_cells:
        if cid not in placement or cid not in net_idx:
            continue
        nx = ny = cnt = 0.0
        for _, others in net_idx[cid]:
            for o in others:
                if o in placement:
                    nx += placement[o][0]; ny += placement[o][1]; cnt += 1
        if cnt == 0:
            continue
        cx, cy = nx / cnt, ny / cnt
        x, y   = placement[cid]
        w, h   = netlist.cells[cid]["width"], netlist.cells[cid]["height"]
        noise  = rng.normal(0, noise_std)
        refined[cid] = (
            max(0.0, min(x + alpha * (cx - x) + noise, die_w - w)),
            max(0.0, min(y + alpha * (cy - y) + noise, die_h - h)),
        )
    return refined


# ------------------------------------------------------------------ main

def main():
    print("Generating synthetic ISPD 2019 benchmark (ispd2019_test1, 200 cells)…")
    gen     = SyntheticISPD2019(seed=42)
    netlist, die_w, die_h, _ = gen.generate("ispd2019_test1", num_cells=200)
    print(f"  Cells={netlist.cell_count}  Nets={netlist.net_count}  "
          f"Die={die_w:.1f}×{die_h:.1f}")

    rng     = np.random.default_rng(7)
    leg     = QuantumLegalizer(row_height=1.0)
    net_idx = build_net_index(netlist)
    gen_obj = PlacementAnimationGenerator(
        netlist, die_w, die_h, out_dir="docs", dpi=120)

    # -------- Stage 0 : random initialisation --------
    pl = random_placement(netlist, die_w, die_h, rng)
    gen_obj.add_frame(pl, iteration=0,   label="Random Init")

    # -------- Stage 1 : QUBO grid decode (simulates QA bitstring) --------
    pl = grid_placement(netlist, die_w, die_h, grid_bins=8)
    gen_obj.add_frame(pl, iteration=1,   label="QUBO Grid Decode")

    # -------- Stage 2 : after legalization --------
    pl = leg.legalize(pl, netlist, die_w, die_h)
    gen_obj.add_frame(pl, iteration=2,   label="Post-Legalization")

    # -------- Stages 3–7 : iterative gravity refinement --------
    labels = [
        "Refinement 1 — coarse pull",
        "Refinement 2 — medium pull",
        "Refinement 3 — fine pull",
        "Refinement 4 — detail pull",
        "Final — legalised",
    ]
    alphas = [0.40, 0.30, 0.20, 0.12, 0.06]
    noise  = [1.5,  0.8,  0.4,  0.15, 0.05]

    for step, (lbl, alp, ns) in enumerate(zip(labels, alphas, noise), start=3):
        pl = gravity_step_fast(pl, netlist, net_idx, die_w, die_h,
                               alpha=alp, noise_std=ns, rng=rng)
        pl = leg.legalize(pl, netlist, die_w, die_h)
        gen_obj.add_frame(pl, iteration=step, label=lbl)

    # -------- Save all GIFs + combined panel --------
    gen_obj.save_all(fps=5)

    # -------- Print metrics on final placement --------
    hpwl = QuantumPlacementMetrics.hpwl(pl, netlist)
    ov   = QuantumPlacementMetrics.total_overlap_area(pl, netlist)
    bv   = QuantumPlacementMetrics.boundary_violations(pl, netlist, die_w, die_h)
    print(f"\n  Final HPWL={hpwl:.2f}  Overlap={ov:.2f}  BndViol={bv:.2f}")

    # -------- List output files --------
    print("\nGenerated files:")
    for root, _, files in os.walk("docs"):
        for f in sorted(files):
            path = os.path.join(root, f)
            kb   = os.path.getsize(path) // 1024
            print(f"  {path:<55s} {kb:>5} KB")


if __name__ == "__main__":
    main()
