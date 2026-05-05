"""QUBO formulation for VLSI placement optimization"""

import numpy as np
from itertools import combinations


class PlacementQUBO:
    """Convert placement problem to QUBO matrix."""

    def __init__(self, netlist, die_width, die_height, grid_cells=4):
        """Initialize QUBO formulation.

        Args:
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            grid_cells: Grid resolution (cells per dimension)
        """
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.grid_cells = grid_cells
        self.qubo = {}
        self.cell_to_qubit = {}
        self._build_cell_mapping()

    def _build_cell_mapping(self):
        """Map cells to qubit indices."""
        idx = 0
        for cell_id in self.netlist.cells:
            # Each cell uses log2(grid_cells) qubits per dimension
            qubits_per_dim = int(np.log2(self.grid_cells)) if self.grid_cells > 1 else 1
            self.cell_to_qubit[cell_id] = list(range(idx, idx + 2 * qubits_per_dim))
            idx += 2 * qubits_per_dim

    def get_qubit_count(self):
        """Return total number of qubits needed."""
        return sum(len(qubits) for qubits in self.cell_to_qubit.values())

    def build_qubo(self, wl_weight=1.0, overlap_weight=10.0):
        """Build QUBO matrix from placement objective.

        Args:
            wl_weight: Wirelength weight
            overlap_weight: Overlap penalty weight

        Returns:
            QUBO dict {(i, j): coeff}
        """
        qubo = {}

        # Wirelength minimization via net clique expansion
        for net_id, net_info in self.netlist.nets.items():
            pins = net_info['pins']
            if len(pins) < 2:
                continue

            # Create cliques for net fanout
            for cell1, cell2 in combinations([c for c, _ in pins], 2):
                if cell1 in self.cell_to_qubit and cell2 in self.cell_to_qubit:
                    qubits1 = self.cell_to_qubit[cell1]
                    qubits2 = self.cell_to_qubit[cell2]

                    # Manhattan distance approximation
                    for i, q1 in enumerate(qubits1[:len(qubits1)//2]):
                        for q2 in qubits2[:len(qubits2)//2]:
                            key = tuple(sorted([q1, q2]))
                            qubo[key] = qubo.get(key, 0) + wl_weight * 0.5

        # Overlap penalty (simplified via cell conflicts)
        cells = list(self.netlist.cells.keys())
        for cell1, cell2 in combinations(cells, 2):
            if cell1 in self.cell_to_qubit and cell2 in self.cell_to_qubit:
                # Penalize similar qubit states (potential overlap)
                qubits1 = self.cell_to_qubit[cell1]
                qubits2 = self.cell_to_qubit[cell2]

                for q1, q2 in zip(qubits1, qubits2):
                    key = tuple(sorted([q1, q2]))
                    qubo[key] = qubo.get(key, 0) + overlap_weight

        self.qubo = qubo
        return qubo

    def extract_placement(self, bitstring):
        """Extract cell coordinates from quantum bitstring.

        Args:
            bitstring: Measurement result (str of 0s and 1s)

        Returns:
            Placement dict {cell_id: (x, y)}
        """
        placement = {}
        cell_width = self.die_width / self.grid_cells
        cell_height = self.die_height / self.grid_cells

        for cell_id, qubits in self.cell_to_qubit.items():
            if len(qubits) >= 2:
                x_bits = ''.join(bitstring[q] for q in qubits[:len(qubits)//2])
                y_bits = ''.join(bitstring[q] for q in qubits[len(qubits)//2:])

                x_idx = int(x_bits, 2) if x_bits else 0
                y_idx = int(y_bits, 2) if y_bits else 0

                x = min(x_idx * cell_width, self.die_width - 1)
                y = min(y_idx * cell_height, self.die_height - 1)
                placement[cell_id] = (x, y)
            else:
                placement[cell_id] = (0, 0)

        return placement
