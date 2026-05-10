"""
Placement Animation Generator.

Saves every iteration as an individual numbered PNG in docs/frames/,
builds per-channel GIF animations, and writes the final combined 4-panel
PNG + GIF that mirrors the DREAMPlace website layout.

Frame filenames:
  docs/frames/circuit_layout_frame_{iter:03d}.png
  docs/frames/density_map_frame_{iter:03d}.png
  docs/frames/qubo_energy_frame_{iter:03d}.png
  docs/frames/quantum_gradient_frame_{iter:03d}.png
  docs/frames/combined_frame_{iter:03d}.png
"""

import os
import numpy as np
from PIL import Image

from .circuit_layout_renderer import CircuitLayoutRenderer, _fig_to_rgb
from .qubo_field_renderer import QUBOFieldRenderer


_HEADERS = [
    "ISPD 2019 Circuit Layout",
    "Density Map",
    "QUBO Energy Landscape",
    "Quantum Gradient Field",
]
_HDR_COLOR = "#1A4080"
_PANEL_BG  = "#FFFFFF"


class PlacementAnimationGenerator:
    """
    Collect placement frames and render DREAMPlace-style output.

    Usage
    -----
    gen = PlacementAnimationGenerator(netlist, dw, dh, out_dir="docs")
    gen.add_frame(placement, iteration=0)
    ...
    gen.save_all()
    """

    def __init__(self, netlist, die_width: float, die_height: float,
                 out_dir: str = "docs", dpi: int = 120):
        self.netlist   = netlist
        self.dw        = die_width
        self.dh        = die_height
        self.out_dir   = out_dir
        self.frames_dir = os.path.join(out_dir, "frames")
        os.makedirs(self.frames_dir, exist_ok=True)

        self._lr = CircuitLayoutRenderer(dpi=dpi, fig_inches=5.5)
        self._fr = QUBOFieldRenderer(grid_bins=64, dpi=dpi, fig_inches=4.0)

        self._frames_layout   : list[np.ndarray] = []
        self._frames_density  : list[np.ndarray] = []
        self._frames_energy   : list[np.ndarray] = []
        self._frames_gradient : list[np.ndarray] = []
        self._iters           : list[int]         = []

    # ------------------------------------------------------------------ add

    def add_frame(self, placement: dict, iteration: int, label: str = ""):
        i = len(self._iters)
        self._iters.append(iteration)

        img_l = self._lr.render(placement, self.netlist,
                                self.dw, self.dh, iteration, title=label)
        img_d = self._fr.render_density_map(
            placement, self.netlist, self.dw, self.dh)
        img_e = self._fr.render_qubo_energy(
            placement, self.netlist, self.dw, self.dh)
        img_g = self._fr.render_quantum_gradient(
            placement, self.netlist, self.dw, self.dh)

        self._frames_layout.append(img_l)
        self._frames_density.append(img_d)
        self._frames_energy.append(img_e)
        self._frames_gradient.append(img_g)

        # ---- Save individual frame PNGs ----
        tag = f"{iteration:03d}"
        _save_png(img_l, os.path.join(self.frames_dir, f"circuit_layout_frame_{tag}.png"))
        _save_png(img_d, os.path.join(self.frames_dir, f"density_map_frame_{tag}.png"))
        _save_png(img_e, os.path.join(self.frames_dir, f"qubo_energy_frame_{tag}.png"))
        _save_png(img_g, os.path.join(self.frames_dir, f"quantum_gradient_frame_{tag}.png"))

        combined = self._build_panel(img_l, img_d, img_e, img_g, iteration, label)
        _save_png(combined, os.path.join(self.frames_dir, f"combined_frame_{tag}.png"))

        print(f"  [Viz] Frame {i+1:3d}  iter={iteration:3d}"
              + (f"  {label}" if label else ""))
        return combined

    # ------------------------------------------------------------------ save all

    def save_all(self, fps: int = 5):
        for channel, frames, name in [
            ("Circuit Layout",      self._frames_layout,   "circuit_layout"),
            ("Density Map",         self._frames_density,  "density_map"),
            ("QUBO Energy",         self._frames_energy,   "qubo_energy"),
            ("Quantum Gradient",    self._frames_gradient, "quantum_gradient"),
        ]:
            gif_path = os.path.join(self.out_dir, f"{name}.gif")
            _save_gif(frames, gif_path, fps)

            # Final static PNG
            if frames:
                _save_png(frames[-1], os.path.join(self.out_dir, f"{name}_final.png"))

        # Combined GIF + final PNG
        combined_frames = [
            self._build_panel(l, d, e, g, it)
            for l, d, e, g, it in zip(
                self._frames_layout, self._frames_density,
                self._frames_energy, self._frames_gradient,
                self._iters)
        ]
        if combined_frames:
            _save_gif(combined_frames,
                      os.path.join(self.out_dir, "quantum_placement_animation.gif"), fps)
            _save_png(combined_frames[-1],
                      os.path.join(self.out_dir, "quantum_placement_result.png"))

        print(f"\n  [Viz] All frames → {self.frames_dir}/")
        print(f"  [Viz] Animations → {self.out_dir}/*.gif")

    # ------------------------------------------------------------------ panel

    def _build_panel(self, layout, density, energy, gradient,
                     iteration: int = 0, label: str = "") -> np.ndarray:
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec

        # Resize field images to match layout image height
        target_h = layout.shape[0]
        imgs = [layout, density, energy, gradient]
        resized = []
        for im in imgs:
            if im.shape[0] != target_h:
                pil = Image.fromarray(im)
                ratio = target_h / im.shape[0]
                new_w = int(im.shape[1] * ratio)
                pil = pil.resize((new_w, target_h), Image.LANCZOS)
                resized.append(np.asarray(pil))
            else:
                resized.append(im)

        total_w = sum(r.shape[1] for r in resized)
        header_h = max(38, int(target_h * 0.07))

        # White panel
        panel = np.full((target_h + header_h, total_w, 3), 255, dtype=np.uint8)

        # Draw column headers using matplotlib text rendering
        col_widths = [r.shape[1] for r in resized]
        panel = _draw_header_row(panel, _HEADERS, col_widths, header_h, iteration, label)

        # Place images side-by-side below header
        x_off = 0
        for r in resized:
            h, w = r.shape[:2]
            panel[header_h: header_h + h, x_off: x_off + w] = r
            x_off += w

        return panel


# ------------------------------------------------------------------ helpers

def _draw_header_row(panel: np.ndarray, headers: list[str],
                     col_widths: list[int], header_h: int,
                     iteration: int, label: str) -> np.ndarray:
    import matplotlib.pyplot as plt

    total_w = sum(col_widths)
    dpi = 100
    fig_w = total_w / dpi
    fig_h = header_h / dpi

    fig, axes = plt.subplots(1, len(headers),
                             figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor(_PANEL_BG)

    for ax, hdr, cw in zip(axes, headers, col_widths):
        ax.set_facecolor(_PANEL_BG)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.axis("off")
        ax.text(0.5, 0.5, hdr, transform=ax.transAxes,
                color=_HDR_COLOR, fontsize=9, fontweight="bold",
                ha="center", va="center")

    title_str = f"Iter {iteration}" + (f" — {label}" if label else "")
    fig.suptitle(title_str, fontsize=8, color="#555555",
                 y=0.05, ha="center")

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0,
                        wspace=0.01)
    fig.canvas.draw()
    buf = fig.canvas.buffer_rgba()
    hdr_arr = np.asarray(buf)[:, :, :3].copy()
    plt.close(fig)

    # Crop/resize header to exact panel width
    if hdr_arr.shape[1] != total_w:
        pil = Image.fromarray(hdr_arr)
        pil = pil.resize((total_w, header_h), Image.LANCZOS)
        hdr_arr = np.asarray(pil)
    else:
        if hdr_arr.shape[0] != header_h:
            pil = Image.fromarray(hdr_arr)
            pil = pil.resize((total_w, header_h), Image.LANCZOS)
            hdr_arr = np.asarray(pil)

    panel[:header_h, :total_w] = hdr_arr
    return panel


def _save_png(img: np.ndarray, path: str):
    Image.fromarray(img).save(path, optimize=True)


def _save_gif(frames: list, path: str, fps: int):
    if not frames:
        return
    duration_ms = max(80, int(1000 / fps))
    pil_frames = [Image.fromarray(f) for f in frames]
    pil_frames[0].save(
        path, save_all=True, append_images=pil_frames[1:],
        loop=0, duration=duration_ms, optimize=False)
    print(f"  [Viz] {len(frames)}-frame GIF → {path}")
