"""
QUBO Field Renderer — produces three DREAMPlace-style field visualisations:

  1. Density Map        — per-bin cell-area density (dark = overflow)
  2. QUBO Energy        — Gaussian-smoothed potential field (≈ Electric Potential)
  3. Quantum Gradient   — gradient magnitude of energy field (≈ Electric Field)

All outputs match DREAMPlace's grayscale style:
  white = low value (empty / low energy)
  black = high value (dense / high energy)
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter


_BG_OUTER = "#0D1117"     # panel background (matches layout renderer)
_BORDER   = "#333344"


class QUBOFieldRenderer:

    def __init__(self, grid_bins: int = 64, dpi: int = 150,
                 fig_size: float = 4.0):
        self.bins = grid_bins
        self.dpi = dpi
        self.fig_size = fig_size

    # ------------------------------------------------------------------ 1. density map

    def render_density_map(self, placement: dict, netlist,
                           die_width: float, die_height: float) -> np.ndarray:
        grid = self._build_density_grid(placement, netlist, die_width, die_height)
        # Normalise 0..1 then invert (dark = dense)
        norm = np.clip(grid / (grid.max() + 1e-9), 0, 1)
        # Overlay macro outlines
        macro_mask = self._macro_mask(placement, netlist, die_width, die_height)
        return self._render_field(norm, macro_mask, title=None)

    # ------------------------------------------------------------------ 2. QUBO energy landscape

    def render_qubo_energy(self, placement: dict, netlist,
                           die_width: float, die_height: float,
                           sigma_frac: float = 0.12) -> np.ndarray:
        grid = self._build_density_grid(placement, netlist, die_width, die_height)
        # Smooth to simulate potential field (Gaussian with large sigma)
        sigma = sigma_frac * self.bins
        potential = gaussian_filter(grid.astype(float), sigma=sigma)
        potential += gaussian_filter(grid.astype(float), sigma=sigma * 0.4) * 0.3
        norm = np.clip(potential / (potential.max() + 1e-9), 0, 1)
        return self._render_field(norm, title=None)

    # ------------------------------------------------------------------ 3. quantum gradient field

    def render_quantum_gradient(self, placement: dict, netlist,
                                die_width: float, die_height: float,
                                sigma_frac: float = 0.12) -> np.ndarray:
        grid = self._build_density_grid(placement, netlist, die_width, die_height)
        sigma = sigma_frac * self.bins
        potential = gaussian_filter(grid.astype(float), sigma=sigma)

        # Gradient magnitude (x and y components)
        gy, gx = np.gradient(potential)
        mag = np.sqrt(gx ** 2 + gy ** 2)
        norm = np.clip(mag / (mag.max() + 1e-9), 0, 1)
        return self._render_field(norm, title=None)

    # ------------------------------------------------------------------ internals

    def _build_density_grid(self, placement: dict, netlist,
                            die_width: float, die_height: float) -> np.ndarray:
        b = self.bins
        bw = die_width  / b
        bh = die_height / b
        grid = np.zeros((b, b), dtype=np.float64)

        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            c = netlist.cells[cid]
            # Distribute cell area over bins it overlaps
            bx0 = max(0, int(x / bw))
            by0 = max(0, int(y / bh))
            bx1 = min(b - 1, int((x + c["width"])  / bw))
            by1 = min(b - 1, int((y + c["height"]) / bh))
            cell_area = c["width"] * c["height"]
            span = max(1, (bx1 - bx0 + 1) * (by1 - by0 + 1))
            for bxk in range(bx0, bx1 + 1):
                for byk in range(by0, by1 + 1):
                    grid[byk, bxk] += cell_area / (bw * bh * span)

        return grid

    def _macro_mask(self, placement, netlist,
                    die_width, die_height) -> np.ndarray:
        die_area = die_width * die_height
        thresh = die_area * 0.0005
        b = self.bins
        bw = die_width  / b
        bh = die_height / b
        mask = np.zeros((b, b), dtype=bool)

        for cid, (x, y) in placement.items():
            if cid not in netlist.cells:
                continue
            c = netlist.cells[cid]
            if c["width"] * c["height"] < thresh:
                continue
            bx0 = max(0, int(x / bw))
            by0 = max(0, int(y / bh))
            bx1 = min(b - 1, int((x + c["width"])  / bw))
            by1 = min(b - 1, int((y + c["height"]) / bh))
            mask[by0:by1 + 1, bx0:bx1 + 1] = True

        return mask

    def _render_field(self, norm: np.ndarray,
                      macro_mask: np.ndarray | None = None,
                      title: str | None = None) -> np.ndarray:
        fs = self.fig_size
        fig = plt.figure(figsize=(fs, fs), dpi=self.dpi,
                         facecolor=_BG_OUTER)
        ax = fig.add_axes([0.04, 0.04, 0.92, 0.92])
        ax.set_facecolor("white")

        # Grayscale: white=0, black=1
        display = np.flipud(norm)
        ax.imshow(display, cmap="gray_r", vmin=0, vmax=1,
                  interpolation="bilinear", aspect="equal",
                  extent=[0, 1, 0, 1])

        # Macro outlines
        if macro_mask is not None:
            from matplotlib.patches import Rectangle
            b = self.bins
            for by in range(b):
                for bx in range(b):
                    if macro_mask[by, bx]:
                        rx = bx / b
                        ry = by / b
                        ax.add_patch(Rectangle(
                            (rx, ry), 1/b, 1/b,
                            linewidth=0.3, edgecolor="#555555",
                            facecolor="none"))

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # Border
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(_BORDER)
            spine.set_linewidth(1.2)

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
