"""
Quantum VLSI Placement Metrics.

Tracks all quality indicators used in ISPD 2019 contest scoring and
quantum algorithm convergence analysis.
"""

import math
import numpy as np


class QuantumPlacementMetrics:

    # ------------------------------------------------------------------ static

    @staticmethod
    def hpwl(placement: dict, netlist) -> float:
        total = 0.0
        for net_id, net_info in netlist.nets.items():
            xs, ys = [], []
            for cid, _ in net_info["pins"]:
                if cid in placement:
                    x, y = placement[cid]
                    xs.append(x)
                    ys.append(y)
            if len(xs) >= 2:
                total += (max(xs) - min(xs)) + (max(ys) - min(ys))
        return total

    @staticmethod
    def total_overlap_area(placement: dict, netlist) -> float:
        cells = [(cid, placement[cid]) for cid in netlist.movable_cells
                 if cid in placement]
        total = 0.0
        for i, (c1, (x1, y1)) in enumerate(cells):
            w1 = netlist.cells[c1]["width"]
            h1 = netlist.cells[c1]["height"]
            for c2, (x2, y2) in cells[i + 1:]:
                w2 = netlist.cells[c2]["width"]
                h2 = netlist.cells[c2]["height"]
                ox = max(0.0, min(x1 + w1, x2 + w2) - max(x1, x2))
                oy = max(0.0, min(y1 + h1, y2 + h2) - max(y1, y2))
                total += ox * oy
        return total

    @staticmethod
    def boundary_violations(placement: dict, netlist,
                            die_width: float, die_height: float) -> float:
        viol = 0.0
        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            w = netlist.cells[cid]["width"]
            h = netlist.cells[cid]["height"]
            viol += max(0.0, -x) + max(0.0, -y)
            viol += max(0.0, x + w - die_width)
            viol += max(0.0, y + h - die_height)
        return viol

    @staticmethod
    def placement_cost(placement: dict, netlist,
                       die_width: float, die_height: float,
                       wl_w: float = 1.0, ov_w: float = 5.0,
                       bv_w: float = 2.0) -> float:
        wl = QuantumPlacementMetrics.hpwl(placement, netlist)
        ov = QuantumPlacementMetrics.total_overlap_area(placement, netlist)
        bv = QuantumPlacementMetrics.boundary_violations(
            placement, netlist, die_width, die_height)
        return wl_w * wl + ov_w * ov + bv_w * bv

    # ------------------------------------------------------------------ convergence

    @staticmethod
    def convergence_rate(history: list[float]) -> float:
        """Geometric mean improvement per step."""
        if len(history) < 2 or history[0] == 0:
            return 0.0
        return (history[-1] / history[0]) ** (1.0 / max(len(history) - 1, 1))

    @staticmethod
    def print_summary(label: str, placement: dict, netlist,
                      die_width: float, die_height: float):
        hpwl = QuantumPlacementMetrics.hpwl(placement, netlist)
        ov   = QuantumPlacementMetrics.total_overlap_area(placement, netlist)
        bv   = QuantumPlacementMetrics.boundary_violations(
            placement, netlist, die_width, die_height)
        print(f"  [{label:25s}]  HPWL={hpwl:12.2f}  "
              f"Overlap={ov:10.2f}  BndViol={bv:10.2f}")
