"""ISPD 2019 Benchmark loader and utilities"""

import os
from placement_core.netlist import Netlist


class ISPD2019Loader:
    """Load ISPD 2019 benchmark files (bookshelf format)."""

    @staticmethod
    def load_benchmark(benchmark_dir, benchmark_name):
        """Load ISPD 2019 benchmark.

        Args:
            benchmark_dir: Directory containing benchmark files
            benchmark_name: Benchmark name (e.g., 'superblue1')

        Returns:
            Tuple of (netlist, die_width, die_height, initial_placement)
        """
        nodes_file = f"{benchmark_dir}/{benchmark_name}.nodes"
        nets_file = f"{benchmark_dir}/{benchmark_name}.nets"
        pl_file = f"{benchmark_dir}/{benchmark_name}.pl"
        scl_file = f"{benchmark_dir}/{benchmark_name}.scl"

        netlist = Netlist()
        node_sizes = {}

        # Parse .nodes file
        if os.path.exists(nodes_file):
            with open(nodes_file) as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        cell_id = parts[0]
                        width, height = float(parts[1]), float(parts[2])
                        node_sizes[cell_id] = (width, height)
                        netlist.add_cell(cell_id, width, height)

        # Parse .nets file
        if os.path.exists(nets_file):
            with open(nets_file) as f:
                current_net = None
                for line in f:
                    if line.startswith('NetDegree'):
                        parts = line.strip().split()
                        current_net = parts[1].rstrip(':')
                        netlist.add_net(current_net)
                    elif line.startswith('\t') and current_net:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            cell_id = parts[0]
                            netlist.add_connection(cell_id, current_net, parts[1])

        # Parse .scl file for die size
        die_width, die_height = 0, 0
        if os.path.exists(scl_file):
            with open(scl_file) as f:
                for line in f:
                    if line.startswith('Columns'):
                        die_width = float(line.split()[-1])
                    elif line.startswith('Rows'):
                        die_height = float(line.split()[-1])

        # Parse .pl file for initial placement
        initial_placement = {}
        if os.path.exists(pl_file):
            with open(pl_file) as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        cell_id = parts[0]
                        x, y = float(parts[1]), float(parts[2])
                        initial_placement[cell_id] = (x, y)

        return netlist, die_width, die_height, initial_placement

    @staticmethod
    def get_ispd2019_benchmarks():
        """Return list of ISPD 2019 benchmark names."""
        return [
            'superblue1', 'superblue2', 'superblue3', 'superblue4',
            'superblue5', 'superblue7', 'superblue10', 'superblue16',
            'superblue18', 'superblue19'
        ]
