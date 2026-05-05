"""
QUBO density/overlap operator — quantum equivalent of DREAMPlace's electric
field density formulation.

Penalises two movable cells from occupying the same grid bin by adding a
quadratic penalty whenever their encoded positions share the same qubit pattern.
"""

import numpy as np
from itertools import combinations
from quantum_placement_database.qubo_matrix import QUBOMatrix


class QUBODensityOperator:
    """
    Builds the overlap-penalty QUBO.

    Two cells sharing the same X-grid AND Y-grid bin incur a penalty equal to
    the product of their areas, which drives the solver to separate them.
    """

    def __init__(self, netlist, die_width: float, die_height: float,
                 bits_per_dim: int = 3):
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.bits_per_dim = bits_per_dim
        self.grid_size = 2 ** bits_per_dim
        self._movable = netlist.movable_cells
        self._qubit_offset: dict[str, int] = {}
        offset = 0
        for cid in self._movable:
            self._qubit_offset[cid] = offset
            offset += 2 * bits_per_dim
        self.num_qubits = offset

    # ------------------------------------------------------------------ build

    def build(self, weight: float = 10.0) -> QUBOMatrix:
        Q = QUBOMatrix(self.num_qubits)
        bpd = self.bits_per_dim
        cells = self._movable

        for c1, c2 in combinations(cells, 2):
            if c1 not in self._qubit_offset or c2 not in self._qubit_offset:
                continue
            o1 = self._qubit_offset[c1]
            o2 = self._qubit_offset[c2]

            # Overlap area (penalise more for larger cells)
            a1 = self.netlist.cells[c1]["width"] * self.netlist.cells[c1]["height"]
            a2 = self.netlist.cells[c2]["width"] * self.netlist.cells[c2]["height"]
            penalty = weight * np.sqrt(a1 * a2)

            # Same-bin penalty: add coupling for each bit pair in both dims
            for k in range(bpd):
                Q.add(o1 + k, o2 + k, penalty / bpd)             # X dim
                Q.add(o1 + bpd + k, o2 + bpd + k, penalty / bpd) # Y dim

        return Q

    # ------------------------------------------------------------------ density map

    def compute_bin_density(self, placement: dict[str, tuple[float, float]]) -> np.ndarray:
        """Return 2-D bin density array for visualisation / overflow check."""
        grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float64)
        cell_w = self.die_width / self.grid_size
        cell_h = self.die_height / self.grid_size
        bin_area = cell_w * cell_h

        for cid, (x, y) in placement.items():
            if cid not in self.netlist.cells:
                continue
            bx = min(int(x / cell_w), self.grid_size - 1)
            by = min(int(y / cell_h), self.grid_size - 1)
            cell_area = (self.netlist.cells[cid]["width"] *
                         self.netlist.cells[cid]["height"])
            grid[by, bx] += cell_area / bin_area

        return grid

    def overflow(self, placement: dict[str, tuple[float, float]]) -> float:
        """Density overflow: fraction of bins exceeding capacity 1.0."""
        density = self.compute_bin_density(placement)
        overflow = np.maximum(density - 1.0, 0.0)
        return float(overflow.sum()) / density.size
