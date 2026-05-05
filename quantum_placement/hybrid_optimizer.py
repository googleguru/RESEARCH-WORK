"""Hybrid Quantum-Classical Placement Optimizer"""

import numpy as np
from placement_core.metrics import PlacementMetrics
from placement_core.legalization import Legalizer


class HybridPlacementOptimizer:
    """Hybrid approach combining quantum and classical methods."""

    def __init__(self, netlist, die_width, die_height, config):
        """Initialize hybrid optimizer.

        Args:
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            config: PlacementConfig
        """
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.config = config
        self.legalizer = Legalizer(grid_unit=config.grid_unit)
        self.placement_history = []

    def optimize_iterations(self, num_iterations=3, quantum_depth=2):
        """Run iterative hybrid optimization.

        First iteration: Quick quantum approximate solution
        Subsequent iterations: Refine with classical local optimization

        Args:
            num_iterations: Number of refinement iterations
            quantum_depth: QAOA/VQE circuit depth

        Returns:
            Final placement dict
        """
        from quantum_placement.qubo_formulation import PlacementQUBO
        from quantum_placement.qaoa import QAOAPlacementOptimizer

        # Iteration 0: Quantum initialization
        print(f"\n{'Iteration':12} {'Algorithm':15} {'HPWL':>12} {'Overlap':>10}")
        print(f"{'-'*50}")

        qubo_form = PlacementQUBO(self.netlist, self.die_width,
                                 self.die_height, grid_cells=4)
        qubo_form.build_qubo(wl_weight=1.0, overlap_weight=5.0)

        # First iteration: QAOA
        qaoa = QAOAPlacementOptimizer(qubo_form, depth=quantum_depth)
        placement, _, _ = qaoa.optimize(max_iterations=20)

        # Legalize
        placement = self.legalizer.legalize(
            placement, self.netlist, self.die_width, self.die_height)

        hpwl = PlacementMetrics.half_perimeter_wirelength(placement, self.netlist)
        overlap = self._compute_overlap_penalty(placement)

        print(f"{'0 (QAOA)':12} {'Quantum':15} {hpwl:12.0f} {overlap:10.3f}")
        self.placement_history.append(placement)

        # Iterations 1+: Classical refinement
        for it in range(1, num_iterations):
            placement = self._local_search_refinement(
                placement, num_moves=50)

            hpwl = PlacementMetrics.half_perimeter_wirelength(
                placement, self.netlist)
            overlap = self._compute_overlap_penalty(placement)

            print(f"{it:2} (LocalSearch)    Classical       {hpwl:12.0f} {overlap:10.3f}")
            self.placement_history.append(placement)

        print(f"{'-'*50}")
        return placement

    def _local_search_refinement(self, placement, num_moves=50):
        """Refine placement via local search.

        Args:
            placement: Current placement
            num_moves: Number of moves to try

        Returns:
            Refined placement
        """
        import random
        refined = placement.copy()
        cells = list(self.netlist.cells.keys())

        for _ in range(num_moves):
            cell_id = random.choice(cells)
            w, h = self.netlist.cells[cell_id]['width'], \
                   self.netlist.cells[cell_id]['height']

            # Random displacement
            old_pos = refined[cell_id]
            new_x = random.uniform(max(0, old_pos[0] - 20),
                                 min(self.die_width - w, old_pos[0] + 20))
            new_y = random.uniform(max(0, old_pos[1] - 20),
                                 min(self.die_height - h, old_pos[1] + 20))

            refined[cell_id] = (new_x, new_y)

            # Legalize after each move
            refined = self.legalizer.legalize(
                refined, self.netlist, self.die_width, self.die_height)

        return refined

    def _compute_overlap_penalty(self, placement):
        """Compute penalty for cell overlaps."""
        penalty = 0
        cells_list = list(placement.items())

        for i, (cid1, (x1, y1)) in enumerate(cells_list):
            w1, h1 = self.netlist.cells[cid1]['width'], \
                     self.netlist.cells[cid1]['height']

            for cid2, (x2, y2) in cells_list[i+1:]:
                w2, h2 = self.netlist.cells[cid2]['width'], \
                         self.netlist.cells[cid2]['height']

                # Overlap area
                x_overlap = max(0, min(x1+w1, x2+w2) - max(x1, x2))
                y_overlap = max(0, min(y1+h1, y2+h2) - max(y1, y2))
                penalty += x_overlap * y_overlap

        return penalty


class IncrementalPlacementRefinement:
    """Incremental refinement for iterative placement."""

    def __init__(self, netlist, die_width, die_height):
        """Initialize incremental optimizer."""
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.critical_nets = []

    def identify_critical_nets(self, placement, top_k=10):
        """Identify nets with high wirelength (critical).

        Args:
            placement: Current placement
            top_k: Number of critical nets

        Returns:
            List of net IDs sorted by wirelength
        """
        net_lengths = []

        for net_id, net_info in self.netlist.nets.items():
            if not net_info['pins']:
                continue

            xs, ys = [], []
            for cell_id, _ in net_info['pins']:
                if cell_id in placement:
                    x, y = placement[cell_id]
                    xs.append(x)
                    ys.append(y)

            if xs and ys:
                hpwl = (max(xs) - min(xs)) + (max(ys) - min(ys))
                net_lengths.append((net_id, hpwl))

        net_lengths.sort(key=lambda x: x[1], reverse=True)
        self.critical_nets = [n[0] for n in net_lengths[:top_k]]
        return self.critical_nets

    def refine_critical_region(self, placement, num_iterations=5):
        """Refine placement of cells in critical nets.

        Args:
            placement: Current placement
            num_iterations: Refinement iterations

        Returns:
            Refined placement
        """
        if not self.critical_nets:
            return placement

        refined = placement.copy()
        critical_cells = set()

        for net_id in self.critical_nets:
            for cell_id, _ in self.netlist.nets[net_id]['pins']:
                critical_cells.add(cell_id)

        import random
        for _ in range(num_iterations):
            cell = random.choice(list(critical_cells))
            x, y = refined[cell]
            w, h = self.netlist.cells[cell]['width'], \
                   self.netlist.cells[cell]['height']

            # Small displacement
            refined[cell] = (
                max(0, min(x + random.gauss(0, 5), self.die_width - w)),
                max(0, min(y + random.gauss(0, 5), self.die_height - h))
            )

        return refined
