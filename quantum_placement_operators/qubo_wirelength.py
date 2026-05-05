"""
QUBO wirelength operator — DREAMPlace-style operator adapted for quantum.

Maps the half-perimeter wirelength (HPWL) objective onto a QUBO by encoding
each movable cell's grid position as a binary string and using net clique
expansion to penalise cells connected by the same net from being placed far apart.
"""

import numpy as np
from itertools import combinations
from quantum_placement_database.qubo_matrix import QUBOMatrix


class QUBOWirelengthOperator:
    """
    Builds the wirelength QUBO for VLSI global placement.

    Encoding:  each movable cell uses `bits_per_dim` qubits for X and the same
    for Y, giving a discrete grid of 2^bits_per_dim cells per dimension.
    """

    def __init__(self, netlist, die_width: float, die_height: float,
                 bits_per_dim: int = 3):
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.bits_per_dim = bits_per_dim
        self.grid_size = 2 ** bits_per_dim          # cells per axis
        self.cell_w = die_width / self.grid_size
        self.cell_h = die_height / self.grid_size

        # Assign qubit ranges: 2*bits_per_dim qubits per movable cell
        self._movable = netlist.movable_cells
        self._qubit_offset: dict[str, int] = {}
        offset = 0
        for cid in self._movable:
            self._qubit_offset[cid] = offset
            offset += 2 * bits_per_dim
        self.num_qubits = offset

    # ------------------------------------------------------------------ build

    def build(self, weight: float = 1.0) -> QUBOMatrix:
        Q = QUBOMatrix(self.num_qubits)
        bpd = self.bits_per_dim

        for net_id, net_info in self.netlist.nets.items():
            movable_pins = [c for c, _ in net_info["pins"]
                            if c in self._qubit_offset]
            if len(movable_pins) < 2:
                continue

            # Net clique expansion — pair-wise coordinate interaction
            for c1, c2 in combinations(movable_pins, 2):
                o1 = self._qubit_offset[c1]
                o2 = self._qubit_offset[c2]

                # X dimension: bits [o+0 .. o+bpd-1]
                for k in range(bpd):
                    # Binary positional weight: bit k represents 2^k grid units
                    pos_weight = (2 ** k) * self.cell_w
                    Q.add(o1 + k, o2 + k, weight * pos_weight)

                # Y dimension: bits [o+bpd .. o+2*bpd-1]
                for k in range(bpd):
                    pos_weight = (2 ** k) * self.cell_h
                    Q.add(o1 + bpd + k, o2 + bpd + k, weight * pos_weight)

        return Q

    # ------------------------------------------------------------------ decode

    def decode_placement(self, bitstring: str) -> dict[str, tuple[float, float]]:
        placement = {}
        bpd = self.bits_per_dim
        for cid, offset in self._qubit_offset.items():
            x_idx = int(bitstring[offset: offset + bpd], 2)
            y_idx = int(bitstring[offset + bpd: offset + 2 * bpd], 2)
            w = self.netlist.cells[cid]["width"]
            h = self.netlist.cells[cid]["height"]
            x = min(x_idx * self.cell_w, self.die_width - w)
            y = min(y_idx * self.cell_h, self.die_height - h)
            placement[cid] = (max(0.0, x), max(0.0, y))
        return placement
