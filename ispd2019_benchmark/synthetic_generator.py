"""
Synthetic, ISPD-inspired benchmark generator.

The repository does not include or claim to reproduce the official ISPD 2019 or
ISPD 2005 benchmark suites. Instead, it creates small deterministic netlists
that are suitable for smoke tests, visualization, and algorithmic experiments.
"""

import numpy as np
from quantum_placement_database.netlist import QuantumNetlist


# Small synthetic sizes that are explicitly illustrative, not contest results.
SYNTHETIC_BENCHMARK_SIZES = {
    "ispd2019_test1": 200,
    "ispd2019_test2": 400,
    "ispd2019_test3": 800,
    "ispd2019_test4": 1600,
    "ispd2005_test1": 160,
    "ispd2005_test2": 320,
    "ispd2005_test3": 640,
    "ispd2005_test4": 1280,
}


class SyntheticISPD2019:
    """Generate a synthetic netlist for placement experiments."""

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
        n_cells = num_cells or SYNTHETIC_BENCHMARK_SIZES.get(name, 200)

        avg_cell_area = 1.0
        total_area = n_cells * avg_cell_area / utilisation
        side = np.sqrt(total_area)
        die_width = die_height = float(side)

        netlist = QuantumNetlist()

        for i in range(n_cells):
            cid = f"c{i}"
            if self.rng.random() < 0.05:
                w = float(self.rng.integers(4, 16))
                h = float(self.rng.integers(4, 16))
            else:
                w = float(self.rng.choice([1, 1, 1, 2, 2, 3]))
                h = 1.0
            netlist.add_cell(cid, w, h)

        n_nets = max(10, int(n_cells * 1.5))
        cells_list = list(netlist.cells.keys())

        for j in range(n_nets):
            nid = f"n{j}"
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

        init_placement: dict[str, tuple[float, float]] = {}
        for cid, data in netlist.cells.items():
            x = float(self.rng.uniform(0, max(0.1, die_width - data["width"])))
            y = float(self.rng.uniform(0, max(0.1, die_height - data["height"])))
            init_placement[cid] = (x, y)

        return netlist, die_width, die_height, init_placement

    def generate_small(self, n_cells: int = 20, n_nets: int = 15) -> tuple:
        """Small synthetic circuit for algorithm testing."""
        return self.generate(num_cells=n_cells)
