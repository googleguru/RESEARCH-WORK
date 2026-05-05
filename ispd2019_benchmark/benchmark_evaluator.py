"""
ISPD 2019 Placement Evaluator.

Computes the official contest metrics:
  1. HPWL (half-perimeter wirelength) — primary metric
  2. Density overflow — movable-cell area / bin area excess
  3. Displacement — from initial placement
"""

import math
import numpy as np
from quantum_placement_database.netlist import QuantumNetlist


class ISPD2019Evaluator:

    def __init__(self, netlist: QuantumNetlist,
                 die_width: float, die_height: float,
                 num_bins: int = 32):
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.num_bins = num_bins

    # ------------------------------------------------------------------ HPWL

    def hpwl(self, placement: dict[str, tuple[float, float]]) -> float:
        total = 0.0
        for net_id, net_info in self.netlist.nets.items():
            xs, ys = [], []
            for cid, _ in net_info["pins"]:
                if cid in placement:
                    x, y = placement[cid]
                    xs.append(x)
                    ys.append(y)
            if len(xs) >= 2:
                total += (max(xs) - min(xs)) + (max(ys) - min(ys))
        return total

    # ------------------------------------------------------------------ overflow

    def density_overflow(self, placement: dict[str, tuple[float, float]]) -> float:
        """Fraction of bins whose cell-area density exceeds 1.0."""
        b = self.num_bins
        bw = self.die_width / b
        bh = self.die_height / b
        grid = np.zeros((b, b), dtype=np.float64)

        for cid, (x, y) in placement.items():
            if cid not in self.netlist.cells:
                continue
            c = self.netlist.cells[cid]
            bx = min(int(x / bw), b - 1)
            by = min(int(y / bh), b - 1)
            grid[by, bx] += c["width"] * c["height"] / (bw * bh)

        return float(np.mean(np.maximum(grid - 1.0, 0.0)))

    # ------------------------------------------------------------------ displacement

    def displacement(self, placement: dict[str, tuple[float, float]],
                     ref: dict[str, tuple[float, float]]) -> float:
        total = 0.0
        count = 0
        for cid, (x, y) in placement.items():
            if cid in ref:
                rx, ry = ref[cid]
                total += math.hypot(x - rx, y - ry)
                count += 1
        return total / max(count, 1)

    # ------------------------------------------------------------------ summary

    def evaluate(self, placement: dict[str, tuple[float, float]],
                 ref: dict[str, tuple[float, float]] | None = None) -> dict:
        result = {
            "hpwl": self.hpwl(placement),
            "density_overflow": self.density_overflow(placement),
        }
        if ref is not None:
            result["avg_displacement"] = self.displacement(placement, ref)
        return result

    def print_report(self, placement: dict, ref: dict | None = None):
        m = self.evaluate(placement, ref)
        print(f"\n{'ISPD 2019 Placement Metrics':=^50}")
        print(f"  HPWL              : {m['hpwl']:>15.2f}")
        print(f"  Density Overflow  : {m['density_overflow']:>15.4f}")
        if "avg_displacement" in m:
            print(f"  Avg Displacement  : {m['avg_displacement']:>15.4f}")
        print("=" * 50)
