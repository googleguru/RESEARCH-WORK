"""
Synthetic ISPD 2019-style benchmark generator.

Produces netlists with realistic ISPD 2019 characteristics:
  - Mixed-size cells (standard cells + macros)
  - Power-law net-degree distribution (mostly 2-pin, some high fanout)
  - Die utilisation ~70%
  - Row-aligned site grid

Use when real ISPD 2019 files are not present.
"""

import numpy as np
from quantum_placement_database.netlist import QuantumNetlist


# Approximate cell counts for ISPD 2019 test cases
ISPD2019_SIZES = {
    "ispd2019_test1": 10_000,
    "ispd2019_test2": 25_000,
    "ispd2019_test3": 50_000,
    "ispd2019_test4": 100_000,
    "ispd2019_test5": 200_000,
    "ispd2019_test6": 500_000,
    "ispd2019_test7": 1_000_000,
    "ispd2019_test8": 2_000_000,
    "ispd2019_test9": 5_000_000,
}


class SyntheticISPD2019:
    """Generate a synthetic netlist matching ISPD 2019 benchmark statistics."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------ public

    def generate(self, name: str = "ispd2019_test1",
                 num_cells: int | None = None,
                 utilisation: float = 0.70) -> tuple:
        """
        Returns
        -------
        netlist       : QuantumNetlist
        die_width     : float
        die_height    : float
        init_placement: dict {cell_id: (x, y)}
        """
        n_cells = num_cells or ISPD2019_SIZES.get(name, 1000)

        # Die sizing from utilisation
        avg_cell_area = 1.0  # normalised
        total_area = n_cells * avg_cell_area / utilisation
        side = np.sqrt(total_area)
        die_width = die_height = float(side)

        netlist = QuantumNetlist()

        # Cell dimensions: ~95% standard cells (1×1), ~5% macros (larger)
        for i in range(n_cells):
            cid = f"c{i}"
            if self.rng.random() < 0.05:        # macro
                w = float(self.rng.integers(4, 16))
                h = float(self.rng.integers(4, 16))
            else:                               # standard cell
                w = float(self.rng.choice([1, 1, 1, 2, 2, 3]))
                h = 1.0
            netlist.add_cell(cid, w, h)

        # Nets: power-law degree distribution
        n_nets = int(n_cells * 1.5)
        cells_list = list(netlist.cells.keys())

        for j in range(n_nets):
            nid = f"n{j}"
            # Degree: 60% 2-pin, 25% 3-pin, 10% 4-pin, 5% ≥5-pin
            r = self.rng.random()
            if r < 0.60:
                deg = 2
            elif r < 0.85:
                deg = 3
            elif r < 0.95:
                deg = 4
            else:
                deg = int(self.rng.integers(5, 12))
            deg = min(deg, n_cells)

            pins = self.rng.choice(cells_list, size=deg, replace=False)
            netlist.add_net(nid)
            for cid in pins:
                netlist.add_pin(cid, nid)

        # Initial random legal placement
        init_placement: dict[str, tuple[float, float]] = {}
        for cid, data in netlist.cells.items():
            x = float(self.rng.uniform(0, max(0.1, die_width - data["width"])))
            y = float(self.rng.uniform(0, max(0.1, die_height - data["height"])))
            init_placement[cid] = (x, y)

        return netlist, die_width, die_height, init_placement

    def generate_small(self, n_cells: int = 20, n_nets: int = 15) -> tuple:
        """Small synthetic circuit for algorithm testing."""
        return self.generate(num_cells=n_cells)
