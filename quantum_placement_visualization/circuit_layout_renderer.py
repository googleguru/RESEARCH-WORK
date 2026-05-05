"""
Circuit Layout Renderer — produces the DREAMPlace-style cell+net layout view.

Color scheme matches DREAMPlace output:
  - Background  : #0D1117 (near-black)
  - Macros      : #D4706A (coral-red)
  - Std cells   : #E89A96 (salmon-pink)
  - Net lines   : #3366FF (blue, low alpha)
  - Iter label  : #4488FF (blue text)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection, PatchCollection


_BG      = "#0D1117"
_MACRO   = "#C05048"
_STD     = "#E89A96"
_NET     = "#2244CC"
_LABEL   = "#4488FF"

# Threshold: cells with area > this fraction of die are treated as macros
_MACRO_AREA_FRAC = 0.0005


class CircuitLayoutRenderer:

    def __init__(self, dpi: int = 150, fig_size: float = 5.5):
        self.dpi = dpi
        self.fig_size = fig_size

    # ------------------------------------------------------------------ public

    def render(self, placement: dict, netlist,
               die_width: float, die_height: float,
               iteration: int = 0,
               max_nets: int = 3000) -> np.ndarray:
        """Return HxWx3 uint8 RGB array."""
        die_area = die_width * die_height
        macro_thresh = die_area * _MACRO_AREA_FRAC

        fig = plt.figure(figsize=(self.fig_size, self.fig_size),
                         dpi=self.dpi, facecolor=_BG)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor(_BG)
        ax.set_xlim(0, die_width)
        ax.set_ylim(0, die_height)
        ax.set_aspect("equal")
        ax.axis("off")

        # ---- Cell rectangles ----
        std_patches, mac_patches = [], []
        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            c = netlist.cells[cid]
            w, h = c["width"], c["height"]
            rect = mpatches.FancyBboxPatch(
                (x, y), w, h,
                boxstyle="square,pad=0",
                linewidth=0.0,
            )
            if w * h >= macro_thresh:
                mac_patches.append(rect)
            else:
                std_patches.append(rect)

        if std_patches:
            ax.add_collection(PatchCollection(
                std_patches, facecolor=_STD, edgecolor="none", alpha=0.85))
        if mac_patches:
            ax.add_collection(PatchCollection(
                mac_patches, facecolor=_MACRO, edgecolor="#882222",
                linewidths=0.4, alpha=0.95))

        # ---- Net connections ----
        segments = []
        nets = list(netlist.nets.items())
        if len(nets) > max_nets:
            rng = np.random.default_rng(0)
            idx = rng.choice(len(nets), max_nets, replace=False)
            nets = [nets[i] for i in idx]

        for _, net_info in nets:
            pts = []
            for cid, _ in net_info["pins"]:
                if cid in placement and cid in netlist.cells:
                    c = netlist.cells[cid]
                    cx = placement[cid][0] + c["width"]  / 2
                    cy = placement[cid][1] + c["height"] / 2
                    pts.append((cx, cy))
            if len(pts) >= 2:
                for k in range(len(pts) - 1):
                    segments.append([pts[k], pts[k + 1]])

        if segments:
            lc = LineCollection(segments, colors=_NET,
                                linewidths=0.25, alpha=0.28)
            ax.add_collection(lc)

        # ---- Iteration label ----
        ax.text(0.985, 0.015, f"Iter: {iteration}",
                transform=ax.transAxes, color=_LABEL,
                fontsize=9, ha="right", va="bottom",
                fontweight="bold", fontfamily="monospace")

        img = _fig_to_array(fig)
        plt.close(fig)
        return img

    def save(self, img: np.ndarray, path: str):
        from PIL import Image
        Image.fromarray(img).save(path)


# ------------------------------------------------------------------ util

def _fig_to_array(fig) -> np.ndarray:
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    arr = np.asarray(buf)
    return arr[:, :, :3].copy()
