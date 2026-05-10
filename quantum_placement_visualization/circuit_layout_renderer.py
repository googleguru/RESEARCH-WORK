"""
Circuit Layout Renderer — white-background DREAMPlace-style cell+net view.

White background, die border, salmon macros, teal standard cells,
thin dark-blue net lines, no axis overlap, iteration label bottom-right.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Rectangle

_MACRO_AREA_FRAC = 0.0008   # cells larger than 0.08 % of die area = macro

# White-background palette
_WHITE    = "#FFFFFF"
_DIE_EDGE = "#222222"
_STD_FC   = "#F0A8A0"       # soft salmon
_STD_EC   = "#C06858"       # darker salmon border
_MAC_FC   = "#C03830"       # deep red
_MAC_EC   = "#801010"
_NET      = "#1A3A8F"       # dark navy, low alpha
_LABEL_BG = "#EEEEEE"
_LABEL_FG = "#1A3A8F"


class CircuitLayoutRenderer:

    def __init__(self, dpi: int = 120, fig_inches: float = 5.5):
        self.dpi = dpi
        self.fig_inches = fig_inches

    # ------------------------------------------------------------------ public

    def render(self, placement: dict, netlist,
               die_width: float, die_height: float,
               iteration: int = 0,
               max_nets: int = 2500,
               title: str = "") -> np.ndarray:
        """Return H×W×3 uint8 RGB array (white background)."""
        die_area  = die_width * die_height
        macro_thr = die_area * _MACRO_AREA_FRAC

        pad = 0.04          # 4 % margin around die
        w_range = die_width  * (1 + 2 * pad)
        h_range = die_height * (1 + 2 * pad)

        fig, ax = plt.subplots(figsize=(self.fig_inches, self.fig_inches),
                               dpi=self.dpi)
        fig.patch.set_facecolor(_WHITE)
        ax.set_facecolor(_WHITE)

        ax.set_xlim(-die_width * pad, die_width  * (1 + pad))
        ax.set_ylim(-die_height * pad, die_height * (1 + pad))
        ax.set_aspect("equal")
        ax.tick_params(left=False, bottom=False,
                       labelleft=False, labelbottom=False)
        for s in ax.spines.values():
            s.set_visible(False)

        # Die boundary
        ax.add_patch(Rectangle(
            (0, 0), die_width, die_height,
            linewidth=1.5, edgecolor=_DIE_EDGE, facecolor="none", zorder=5))

        # ---- Cell rectangles ------------------------------------------------
        std_patches, mac_patches = [], []
        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            c  = netlist.cells[cid]
            w, h = c["width"], c["height"]
            rect = mpatches.FancyBboxPatch(
                (x, y), max(w, die_width * 0.002), max(h, die_height * 0.002),
                boxstyle="square,pad=0", linewidth=0)
            if w * h >= macro_thr:
                mac_patches.append(rect)
            else:
                std_patches.append(rect)

        if std_patches:
            ax.add_collection(PatchCollection(
                std_patches, facecolor=_STD_FC, edgecolor=_STD_EC,
                linewidths=0.25, alpha=0.88, zorder=2))
        if mac_patches:
            ax.add_collection(PatchCollection(
                mac_patches, facecolor=_MAC_FC, edgecolor=_MAC_EC,
                linewidths=0.6, alpha=0.95, zorder=3))

        # ---- Net lines -------------------------------------------------------
        all_nets = list(netlist.nets.items())
        if len(all_nets) > max_nets:
            rng = np.random.default_rng(0)
            idx = rng.choice(len(all_nets), max_nets, replace=False)
            all_nets = [all_nets[i] for i in idx]

        segments = []
        for _, net_info in all_nets:
            pts = []
            for cid, _ in net_info["pins"]:
                if cid in placement and cid in netlist.cells:
                    c  = netlist.cells[cid]
                    cx = placement[cid][0] + c["width"]  / 2
                    cy = placement[cid][1] + c["height"] / 2
                    pts.append((cx, cy))
            for k in range(len(pts) - 1):
                segments.append([pts[k], pts[k + 1]])

        if segments:
            lc = LineCollection(segments, colors=_NET,
                                linewidths=0.22, alpha=0.30, zorder=4)
            ax.add_collection(lc)

        # ---- Iteration label -------------------------------------------------
        ax.text(0.985, 0.015,
                f"Iter: {iteration}" + (f"  |  {title}" if title else ""),
                transform=ax.transAxes,
                color=_LABEL_FG, fontsize=8, ha="right", va="bottom",
                fontweight="bold", fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.25",
                          facecolor=_LABEL_BG, edgecolor="none", alpha=0.85),
                zorder=10)

        fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        img = _fig_to_rgb(fig)
        plt.close(fig)
        return img

    def save(self, img: np.ndarray, path: str):
        from PIL import Image
        Image.fromarray(img).save(path, optimize=True)


# ------------------------------------------------------------------ util

def _fig_to_rgb(fig) -> np.ndarray:
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    arr = np.asarray(buf)
    return arr[:, :, :3].copy()
