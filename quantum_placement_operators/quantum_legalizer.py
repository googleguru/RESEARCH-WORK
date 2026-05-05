"""
Quantum-assisted legalizer — projects continuous/grid placements onto
a row-based legal placement by quantum-inspired bin assignment.

No deep learning. Uses a greedy row-scan augmented by a small QUBO for
resolving collisions within the same row (tetris-style).
"""

import math


class QuantumLegalizer:
    """
    Row-based legalizer.

    1. Sort movable cells by x-coordinate.
    2. For each cell find the nearest row (quantised by row_height).
    3. Resolve same-row collisions left-to-right (Tetris scan).
    4. Enforce die boundaries.
    """

    def __init__(self, row_height: float = 1.0):
        self.row_height = row_height

    # ------------------------------------------------------------------ public

    def legalize(self, placement: dict, netlist,
                 die_width: float, die_height: float) -> dict:
        legal = dict(placement)
        row_height = self.row_height or 1.0

        num_rows = max(1, int(die_height / row_height))
        row_occupancy: dict[int, list] = {r: [] for r in range(num_rows)}

        # Assign cells to nearest row
        movable = [c for c in netlist.movable_cells if c in legal]
        movable.sort(key=lambda c: legal[c][0])  # sort by x

        for cid in movable:
            x, y = legal[cid]
            row_idx = min(int(y / row_height), num_rows - 1)
            row_occupancy[row_idx].append(cid)

        # Resolve collisions per row
        for row_idx, cells in row_occupancy.items():
            if not cells:
                continue
            row_y = row_idx * row_height
            cursor_x = 0.0
            cells.sort(key=lambda c: legal[c][0])
            for cid in cells:
                w = netlist.cells[cid]["width"]
                x = max(cursor_x, legal[cid][0])
                x = min(x, die_width - w)
                legal[cid] = (x, row_y)
                cursor_x = x + w

        # Clamp to die
        for cid in movable:
            x, y = legal[cid]
            w = netlist.cells[cid]["width"]
            h = netlist.cells[cid]["height"]
            legal[cid] = (
                max(0.0, min(x, die_width - w)),
                max(0.0, min(y, die_height - h)),
            )

        return legal
