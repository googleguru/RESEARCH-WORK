"""Simulated annealing for VLSI placement"""

import random
import math


class SimulatedAnnealingSolver:
    """Simulated annealing-based placement optimizer."""

    def __init__(self, initial_temp=1000, cooling_rate=0.95, iterations_per_temp=100):
        """Initialize SA solver.

        Args:
            initial_temp: Initial temperature
            cooling_rate: Cooling rate per iteration
            iterations_per_temp: Iterations before temperature decrease
        """
        self.temp = initial_temp
        self.cooling_rate = cooling_rate
        self.iters_per_temp = iterations_per_temp

    def solve(self, netlist, die_width, die_height, max_iterations=10000):
        """Solve placement using simulated annealing.

        Args:
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            max_iterations: Maximum iterations

        Returns:
            Best placement found
        """
        # Initialize with random placement
        current = self._random_placement(netlist, die_width, die_height)
        best = current.copy()
        best_cost = self._compute_cost(current, netlist)

        current_cost = best_cost
        temp = self.temp
        iteration = 0

        while iteration < max_iterations and temp > 1e-6:
            for _ in range(self.iters_per_temp):
                # Generate neighbor via move
                neighbor = self._generate_neighbor(current, netlist,
                                                  die_width, die_height)
                neighbor_cost = self._compute_cost(neighbor, netlist)

                # Metropolis acceptance criterion
                delta = neighbor_cost - current_cost
                if delta < 0 or random.random() < math.exp(-delta / temp):
                    current = neighbor
                    current_cost = neighbor_cost

                    # Update best solution
                    if current_cost < best_cost:
                        best = current.copy()
                        best_cost = current_cost

                iteration += 1
                if iteration >= max_iterations:
                    break

            # Cool down
            temp *= self.cooling_rate

        return best

    def _random_placement(self, netlist, die_width, die_height):
        """Generate random placement."""
        placement = {}
        for cell_id in netlist.cells:
            x = random.uniform(0, die_width)
            y = random.uniform(0, die_height)
            placement[cell_id] = (x, y)
        return placement

    def _generate_neighbor(self, placement, netlist, die_width, die_height):
        """Generate neighbor via random cell displacement."""
        neighbor = placement.copy()
        cell_id = random.choice(list(netlist.cells.keys()))
        x, y = neighbor[cell_id]
        # Random move within bounds
        x += random.gauss(0, die_width * 0.02)
        y += random.gauss(0, die_height * 0.02)
        x = max(0, min(x, die_width))
        y = max(0, min(y, die_height))
        neighbor[cell_id] = (x, y)
        return neighbor

    def _compute_cost(self, placement, netlist):
        """Compute placement cost."""
        from placement_core.metrics import PlacementMetrics
        return PlacementMetrics.half_perimeter_wirelength(placement, netlist)
