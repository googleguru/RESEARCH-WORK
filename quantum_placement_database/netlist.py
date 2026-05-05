"""VLSI netlist database for quantum placement — mirrors DREAMPlace PlaceDB."""

import numpy as np


class QuantumNetlist:
    """Compact netlist representation backed by numpy arrays for QUBO construction."""

    def __init__(self):
        self.cells = {}       # {cell_id: {"width", "height", "type", "fixed"}}
        self.nets = {}        # {net_id: {"pins": [(cell_id, pin_name)]}}
        self.num_movable = 0
        self.num_fixed = 0

    # ------------------------------------------------------------------ build

    def add_cell(self, cell_id: str, width: float, height: float,
                 cell_type: str = "standard", fixed: bool = False):
        self.cells[cell_id] = {
            "width": float(width),
            "height": float(height),
            "type": cell_type,
            "fixed": fixed,
        }
        if fixed:
            self.num_fixed += 1
        else:
            self.num_movable += 1

    def add_net(self, net_id: str):
        self.nets[net_id] = {"pins": []}

    def add_pin(self, cell_id: str, net_id: str, pin_name: str = ""):
        if cell_id not in self.cells:
            return
        if net_id not in self.nets:
            self.add_net(net_id)
        self.nets[net_id]["pins"].append((cell_id, pin_name))

    # ------------------------------------------------------------------ query

    @property
    def movable_cells(self):
        return [c for c, d in self.cells.items() if not d["fixed"]]

    @property
    def cell_count(self):
        return len(self.cells)

    @property
    def net_count(self):
        return len(self.nets)

    def total_cell_area(self) -> float:
        return sum(d["width"] * d["height"] for d in self.cells.values())

    # ------------------------------------------------------------------ arrays (for efficient QUBO build)

    def to_numpy(self):
        """Return cell widths/heights as numpy arrays (movable cells first)."""
        ordered = self.movable_cells + [c for c, d in self.cells.items() if d["fixed"]]
        idx_map = {c: i for i, c in enumerate(ordered)}
        widths = np.array([self.cells[c]["width"] for c in ordered], dtype=np.float64)
        heights = np.array([self.cells[c]["height"] for c in ordered], dtype=np.float64)
        return ordered, idx_map, widths, heights
