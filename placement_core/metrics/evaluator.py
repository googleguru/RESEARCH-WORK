"""Placement quality evaluation metrics"""

import math


class PlacementMetrics:
    """Compute and track placement optimization metrics."""

    @staticmethod
    def half_perimeter_wirelength(placement, netlist):
        """Compute half-perimeter wirelength (HPWL).

        Args:
            placement: Dict of {cell_id: (x, y)}
            netlist: Circuit netlist

        Returns:
            Total HPWL in microns
        """
        total_hpwl = 0
        for net_id, net_info in netlist.nets.items():
            if not net_info['pins']:
                continue
            # Get bounding box of net pins
            xs, ys = [], []
            for cell_id, _ in net_info['pins']:
                if cell_id in placement:
                    x, y = placement[cell_id]
                    xs.append(x)
                    ys.append(y)
            if xs and ys:
                hpwl = (max(xs) - min(xs)) + (max(ys) - min(ys))
                total_hpwl += hpwl
        return total_hpwl

    @staticmethod
    def total_displacement(placement, reference_placement):
        """Compute total cell displacement from reference.

        Args:
            placement: Current placement
            reference_placement: Reference placement

        Returns:
            Sum of L2 distances
        """
        displacement = 0
        for cell_id, (x, y) in placement.items():
            if cell_id in reference_placement:
                ref_x, ref_y = reference_placement[cell_id]
                dist = math.sqrt((x - ref_x)**2 + (y - ref_y)**2)
                displacement += dist
        return displacement

    @staticmethod
    def compute_placement_cost(placement, netlist, die_width, die_height,
                               wl_weight=1.0, boundary_weight=0.1):
        """Compute total placement cost.

        Args:
            placement: Cell placement
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            wl_weight: Wirelength weight
            boundary_weight: Boundary violation weight

        Returns:
            Total cost value
        """
        # Wirelength cost
        hpwl = PlacementMetrics.half_perimeter_wirelength(placement, netlist)
        cost = wl_weight * hpwl

        # Boundary violation cost
        boundary_cost = 0
        for cell_id, (x, y) in placement.items():
            w = netlist.cells[cell_id]['width']
            h = netlist.cells[cell_id]['height']
            # Penalize boundary violations
            if x < 0:
                boundary_cost += abs(x)
            if y < 0:
                boundary_cost += abs(y)
            if x + w > die_width:
                boundary_cost += x + w - die_width
            if y + h > die_height:
                boundary_cost += y + h - die_height

        cost += boundary_weight * boundary_cost
        return cost
