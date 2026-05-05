"""Generate synthetic VLSI circuits for benchmarking"""

import random
from placement_core.netlist import Netlist


class CircuitGenerator:
    """Generate synthetic circuits with controlled properties."""

    @staticmethod
    def generate_random_circuit(num_cells, num_nets, avg_fanout=3, seed=None):
        """Generate random circuit for testing.

        Args:
            num_cells: Number of cells
            num_nets: Number of nets
            avg_fanout: Average net fanout
            seed: Random seed for reproducibility

        Returns:
            Netlist object
        """
        if seed is not None:
            random.seed(seed)

        netlist = Netlist()

        # Create cells with random sizes
        for i in range(num_cells):
            width = random.uniform(1, 10)
            height = random.uniform(1, 10)
            netlist.add_cell(f'cell_{i}', width, height)

        # Create nets with random connections
        for net_idx in range(num_nets):
            netlist.add_net(f'net_{net_idx}')
            # Random fanout
            fanout = max(2, int(random.gauss(avg_fanout, 1)))
            cells_in_net = random.sample(range(num_cells), min(fanout, num_cells))
            for cell_idx in cells_in_net:
                netlist.add_connection(f'cell_{cell_idx}',
                                      f'net_{net_idx}',
                                      f'pin_{cell_idx}')

        return netlist

    @staticmethod
    def generate_grid_circuit(rows, cols, spacing=2.0):
        """Generate grid-structured circuit.

        Args:
            rows: Number of rows
            cols: Number of columns
            spacing: Spacing between cells

        Returns:
            Netlist object
        """
        netlist = Netlist()
        cell_size = 1.0
        cell_count = 0

        # Create cells in grid
        for r in range(rows):
            for c in range(cols):
                netlist.add_cell(f'cell_{cell_count}', cell_size, cell_size)
                cell_count += 1

        # Connect adjacent cells
        net_count = 0
        for r in range(rows):
            for c in range(cols):
                cell_idx = r * cols + c
                netlist.add_net(f'net_{net_count}')
                netlist.add_connection(f'cell_{cell_idx}', f'net_{net_count}', 'pin')

                # Right neighbor connection
                if c < cols - 1:
                    netlist.add_connection(f'cell_{cell_idx + 1}',
                                          f'net_{net_count}', 'pin')
                # Bottom neighbor connection
                if r < rows - 1:
                    netlist.add_connection(f'cell_{cell_idx + cols}',
                                          f'net_{net_count}', 'pin')
                net_count += 1

        return netlist
