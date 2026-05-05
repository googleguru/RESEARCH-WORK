"""
Placement Animation Generator.

Assembles per-iteration frames into:
  - GIF animations  (circuit_layout.gif, density_map.gif, qubo_energy.gif, quantum_gradient.gif)
  - PNG snapshots   (one per stage)
  - Combined 4-panel PNG/GIF   (matches the DREAMPlace website layout exactly)
"""

import os
import numpy as np
from PIL import Image

from .circuit_layout_renderer import CircuitLayoutRenderer
from .qubo_field_renderer import QUBOFieldRenderer


_HEADER_BG    = "#0D1117"
_HEADER_FG    = "#FFFFFF"
_COL_HEADERS  = ["ISPD 2019 Circuit", "Density Map",
                 "QUBO Energy Landscape", "Quantum Gradient Field"]
_HEADER_CYAN  = ["#5DADE2", "#5DADE2", "#5DADE2", "#5DADE2"]


class PlacementAnimationGenerator:
    """
    Collects placement snapshots and renders the 4-panel DREAMPlace-style output.

    Usage
    -----
    gen = PlacementAnimationGenerator(netlist, die_w, die_h, out_dir="docs")
    gen.add_frame(placement, iteration=0)
    ...
    gen.save_all()   # writes GIFs + combined PNG
    """

    def __init__(self, netlist, die_width: float, die_height: float,
                 out_dir: str = "docs", dpi: int = 150):
        self.netlist = netlist
        self.dw = die_width
        self.dh = die_height
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

        self._layout_r  = CircuitLayoutRenderer(dpi=dpi, fig_size=5.5)
        self._field_r   = QUBOFieldRenderer(grid_bins=64, dpi=dpi, fig_size=4.0)

        self._frames_layout   : list[np.ndarray] = []
        self._frames_density  : list[np.ndarray] = []
        self._frames_energy   : list[np.ndarray] = []
        self._frames_gradient : list[np.ndarray] = []
        self._iterations      : list[int]         = []

    # ------------------------------------------------------------------ frame

    def add_frame(self, placement: dict, iteration: int):
        self._iterations.append(iteration)

        self._frames_layout.append(
            self._layout_r.render(placement, self.netlist,
                                  self.dw, self.dh, iteration))

        self._frames_density.append(
            self._field_r.render_density_map(placement, self.netlist,
                                             self.dw, self.dh))

        self._frames_energy.append(
            self._field_r.render_qubo_energy(placement, self.netlist,
                                             self.dw, self.dh))

        self._frames_gradient.append(
            self._field_r.render_quantum_gradient(placement, self.netlist,
                                                  self.dw, self.dh))

        print(f"    [Viz] Frame {len(self._frames_layout):3d}  iter={iteration}")

    # ------------------------------------------------------------------ save

    def save_all(self, fps: int = 8):
        """Save all GIFs, a final combined snapshot PNG, and individual PNGs."""
        _save_gif(self._frames_layout,
                  os.path.join(self.out_dir, "circuit_layout.gif"), fps)
        _save_gif(self._frames_density,
                  os.path.join(self.out_dir, "density_map.gif"), fps)
        _save_gif(self._frames_energy,
                  os.path.join(self.out_dir, "qubo_energy.gif"), fps)
        _save_gif(self._frames_gradient,
                  os.path.join(self.out_dir, "quantum_gradient.gif"), fps)

        # Final-frame individual PNGs
        for name, frames in [
            ("circuit_layout",   self._frames_layout),
            ("density_map",      self._frames_density),
            ("qubo_energy",      self._frames_energy),
            ("quantum_gradient", self._frames_gradient),
        ]:
            if frames:
                Image.fromarray(frames[-1]).save(
                    os.path.join(self.out_dir, f"{name}_final.png"))

        # Combined 4-panel PNG (DREAMPlace style)
        if self._frames_layout:
            combined = self._build_panel(
                self._frames_layout[-1],
                self._frames_density[-1],
                self._frames_energy[-1],
                self._frames_gradient[-1],
            )
            Image.fromarray(combined).save(
                os.path.join(self.out_dir, "quantum_placement_result.png"))
            print(f"    [Viz] Saved combined panel → "
                  f"{self.out_dir}/quantum_placement_result.png")

        # Combined GIF
        if len(self._frames_layout) > 1:
            combined_frames = [
                self._build_panel(l, d, e, g)
                for l, d, e, g in zip(
                    self._frames_layout, self._frames_density,
                    self._frames_energy, self._frames_gradient)
            ]
            _save_gif(combined_frames,
                      os.path.join(self.out_dir, "quantum_placement_animation.gif"),
                      fps)
            print(f"    [Viz] Saved animation GIF → "
                  f"{self.out_dir}/quantum_placement_animation.gif")

    # ------------------------------------------------------------------ panel builder

    def _build_panel(self, layout: np.ndarray, density: np.ndarray,
                     energy: np.ndarray, gradient: np.ndarray) -> np.ndarray:
        """Build a DREAMPlace-style 4-column panel with headers."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        bg = "#0D1117"
        fig = plt.figure(figsize=(22, 7), dpi=100, facecolor=bg)
        gs = GridSpec(2, 4, figure=fig,
                      height_ratios=[0.08, 0.92],
                      hspace=0.03, wspace=0.03,
                      left=0.01, right=0.99, top=0.99, bottom=0.01)

        cols = [layout, density, energy, gradient]
        headers = _COL_HEADERS

        for col_idx, (img, header) in enumerate(zip(cols, headers)):
            # Header row
            ax_h = fig.add_subplot(gs[0, col_idx])
            ax_h.set_facecolor(bg)
            ax_h.axis("off")
            ax_h.text(0.5, 0.5, header,
                      transform=ax_h.transAxes,
                      color="#5DADE2", fontsize=13,
                      ha="center", va="center",
                      fontweight="bold")

            # Image row
            ax_i = fig.add_subplot(gs[1, col_idx])
            ax_i.set_facecolor(bg)
            ax_i.imshow(img, aspect="auto")
            ax_i.axis("off")

        from quantum_placement_visualization.circuit_layout_renderer import _fig_to_array
        arr = _fig_to_array(fig)
        plt.close(fig)
        return arr


# ------------------------------------------------------------------ helpers

def _save_gif(frames: list[np.ndarray], path: str, fps: int):
    if not frames:
        return
    imgs = [Image.fromarray(f) for f in frames]
    duration_ms = max(50, int(1000 / fps))
    imgs[0].save(
        path, save_all=True, append_images=imgs[1:],
        loop=0, duration=duration_ms, optimize=False)
    print(f"    [Viz] Saved {len(frames)}-frame GIF → {path}")
