"""Placement legalization algorithms"""


class Legalizer:
    """Convert illegal placement to legal grid-aligned positions."""

    def __init__(self, grid_unit=1.0):
        """Initialize legalizer.

        Args:
            grid_unit: Grid step size in microns
        """
        self.grid_unit = grid_unit

    def legalize(self, placement, netlist, die_width, die_height):
        """Legalize placement by grid alignment and overlap removal.

        Args:
            placement: Dict of {cell_id: (x, y)}
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height

        Returns:
            Legal placement dict
        """
        # Step 1: Snap to grid
        legal = self._snap_to_grid(placement)

        # Step 2: Resolve overlaps
        legal = self._resolve_overlaps(legal, netlist, die_width, die_height)

        # Step 3: Enforce boundaries
        legal = self._enforce_boundaries(legal, netlist, die_width, die_height)

        return legal

    def _snap_to_grid(self, placement):
        """Align placement to grid."""
        snapped = {}
        for cell_id, (x, y) in placement.items():
            gx = round(x / self.grid_unit) * self.grid_unit
            gy = round(y / self.grid_unit) * self.grid_unit
            snapped[cell_id] = (gx, gy)
        return snapped

    def _resolve_overlaps(self, placement, netlist, die_width, die_height):
        """Remove cell overlaps via local displacement."""
        # Iteratively displace overlapping cells
        resolved = placement.copy()
        max_iterations = 10
        for _ in range(max_iterations):
            if not self._has_overlap(resolved, netlist):
                break
            resolved = self._displace_overlaps(resolved, netlist)
        return resolved

    def _enforce_boundaries(self, placement, netlist, die_width, die_height):
        """Ensure all cells stay within die boundaries."""
        bounded = {}
        for cell_id, (x, y) in placement.items():
            width = netlist.cells[cell_id]['width']
            height = netlist.cells[cell_id]['height']
            # Clamp to boundaries
            bx = max(0, min(x, die_width - width))
            by = max(0, min(y, die_height - height))
            bounded[cell_id] = (bx, by)
        return bounded

    def _has_overlap(self, placement, netlist):
        """Check if any cells overlap."""
        cells_list = list(placement.items())
        for i, (cid1, (x1, y1)) in enumerate(cells_list):
            w1, h1 = netlist.cells[cid1]['width'], netlist.cells[cid1]['height']
            for cid2, (x2, y2) in cells_list[i+1:]:
                w2, h2 = netlist.cells[cid2]['width'], netlist.cells[cid2]['height']
                if self._cells_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
                    return True
        return False

    def _cells_overlap(self, x1, y1, w1, h1, x2, y2, w2, h2):
        """Check if two cells overlap."""
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or
                    y1 + h1 <= y2 or y2 + h2 <= y1)

    def _displace_overlaps(self, placement, netlist):
        """Displace overlapping cells."""
        return placement  # Placeholder
