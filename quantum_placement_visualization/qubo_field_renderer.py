"""
QUBO Field Renderer — three white-background field visualisations.

  render_density_map()    → per-bin cell-area density   (dark = overflow)
  render_qubo_energy()    → Gaussian-smoothed potential  (dark = high energy)
  render_quantum_gradient()→ gradient magnitude field    (dark = high gradient)

All use a pure white figure background; the field image fills a clean axis
with thin black border. No title text drawn inside the figure (titles live
in the README / combined panel).
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import gaussian_filter


class QUBOFieldRenderer:

    def __init__(self, grid_bins: int = 64, dpi: int = 120,
                 fig_inches: float = 4.0):
        self.bins = grid_bins
        self.dpi  = dpi
        self.fig_inches = fig_inches

    # ------------------------------------------------------------------ public

    def render_density_map(self, placement, netlist,
                           die_width, die_height) -> np.ndarray:
        grid  = self._density_grid(placement, netlist, die_width, die_height)
        norm  = self._normalise(grid)
        macro = self._macro_mask(placement, netlist, die_width, die_height)
        return self._render(norm, macro_mask=macro)

    def render_qubo_energy(self, placement, netlist,
                           die_width, die_height,
                           sigma_frac: float = 0.14) -> np.ndarray:
        grid = self._density_grid(placement, netlist, die_width, die_height)
        sig  = sigma_frac * self.bins
        pot  = gaussian_filter(grid.astype(float), sigma=sig) * 0.7 \
             + gaussian_filter(grid.astype(float), sigma=sig * 0.35) * 0.3
        return self._render(self._normalise(pot))

    def render_quantum_gradient(self, placement, netlist,
                                die_width, die_height,
                                sigma_frac: float = 0.14) -> np.ndarray:
        grid = self._density_grid(placement, netlist, die_width, die_height)
        sig  = sigma_frac * self.bins
        pot  = gaussian_filter(grid.astype(float), sigma=sig)
        gy, gx = np.gradient(pot)
        mag  = np.sqrt(gx ** 2 + gy ** 2)
        return self._render(self._normalise(mag))

    def save(self, img: np.ndarray, path: str):
        from PIL import Image
        Image.fromarray(img).save(path, optimize=True)

    # ------------------------------------------------------------------ internals

    def _density_grid(self, placement, netlist,
                      die_width, die_height) -> np.ndarray:
        b  = self.bins
        bw = die_width  / b
        bh = die_height / b
        grid = np.zeros((b, b), dtype=np.float64)

        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            c = netlist.cells[cid]
            bx0 = max(0, int(x / bw))
            by0 = max(0, int(y / bh))
            bx1 = min(b - 1, int((x + c["width"])  / bw))
            by1 = min(b - 1, int((y + c["height"]) / bh))
            area  = c["width"] * c["height"]
            span  = max(1, (bx1 - bx0 + 1) * (by1 - by0 + 1))
            for bxk in range(bx0, bx1 + 1):
                for byk in range(by0, by1 + 1):
                    grid[byk, bxk] += area / (bw * bh * span)
        return grid

    def _macro_mask(self, placement, netlist,
                    die_width, die_height) -> np.ndarray:
        thresh = die_width * die_height * 0.0008
        b  = self.bins
        bw = die_width  / b
        bh = die_height / b
        mask = np.zeros((b, b), dtype=bool)
        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            c = netlist.cells[cid]
            if c["width"] * c["height"] < thresh:
                continue
            bx0 = max(0, int(x / bw));    bx1 = min(b - 1, int((x + c["width"]) / bw))
            by0 = max(0, int(y / bh));    by1 = min(b - 1, int((y + c["height"]) / bh))
            mask[by0:by1 + 1, bx0:bx1 + 1] = True
        return mask

    @staticmethod
    def _normalise(arr: np.ndarray) -> np.ndarray:
        mn, mx = arr.min(), arr.max()
        if mx == mn:
            return np.zeros_like(arr, dtype=float)
        return (arr - mn) / (mx - mn)

    def _render(self, norm: np.ndarray,
                macro_mask: np.ndarray | None = None) -> np.ndarray:
        fi = self.fig_inches
        fig, ax = plt.subplots(figsize=(fi, fi), dpi=self.dpi)
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        # Field image — white=low, black=high; flip so y=0 is bottom
        ax.imshow(np.flipud(norm),
                  cmap="gray_r", vmin=0, vmax=1,
                  interpolation="bilinear", aspect="equal",
                  extent=[0, 1, 0, 1])

        # Macro outlines
        if macro_mask is not None:
            b = self.bins
            for by in range(b):
                for bx in range(b):
                    if macro_mask[by, bx]:
                        ax.add_patch(Rectangle(
                            (bx / b, by / b), 1 / b, 1 / b,
                            linewidth=0.4, edgecolor="#555555",
                            facecolor="none", zorder=3))

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.tick_params(left=False, bottom=False,
                       labelleft=False, labelbottom=False)
        for s in ax.spines.values():
            s.set_visible(True)
            s.set_edgecolor("#333333")
            s.set_linewidth(1.2)

        fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
        from quantum_placement_visualization.circuit_layout_renderer import _fig_to_rgb
        img = _fig_to_rgb(fig)
        plt.close(fig)
        return img
