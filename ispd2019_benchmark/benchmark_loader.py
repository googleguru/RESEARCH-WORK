"""
Benchmark loader for Bookshelf-style placement files.

This repository does not ship the official ISPD contest suite. The loader
accepts user-provided benchmark directories containing Bookshelf-style files
such as .nodes, .nets, .pl and .scl. For reproducible experiments without
external files, use SyntheticISPD2019.
"""

import os
from quantum_placement_database.netlist import QuantumNetlist


SUPPORTED_BENCHMARKS = [
    "ispd2019_test1", "ispd2019_test2", "ispd2019_test3",
    "ispd2019_test4", "ispd2005_test1", "ispd2005_test2",
    "ispd2005_test3", "ispd2005_test4",
]


class ISPD2019BenchmarkLoader:
    """Load benchmark files in Bookshelf-style format."""

    @staticmethod
    def benchmark_names() -> list[str]:
        return list(SUPPORTED_BENCHMARKS)

    @staticmethod
    def load(benchmark_dir: str, name: str):
        """
        Load benchmark from directory.

        Returns
        -------
        netlist       : QuantumNetlist
        die_width     : float
        die_height    : float
        init_placement: dict {cell_id: (x, y)}
        """
        base = os.path.join(benchmark_dir, name)
        required_files = [base + ext for ext in (".nodes", ".nets", ".pl", ".scl")]
        present_files = [path for path in required_files if os.path.isfile(path)]
        if not present_files:
            raise FileNotFoundError(
                f"No benchmark files for '{name}' were found in '{benchmark_dir}'. "
                f"Expected one of: {', '.join(os.path.basename(path) for path in required_files)}"
            )

        netlist = QuantumNetlist()
        die_width = die_height = 0.0
        init_placement: dict[str, tuple[float, float]] = {}

        # ---- .nodes ----
        nodes_path = base + ".nodes"
        if os.path.isfile(nodes_path):
            with open(nodes_path) as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.lower().startswith("numnodes") or \
                       line.lower().startswith("numterminals"):
                        continue
                    parts = line.split()
                    if len(parts) >= 3:
                        cid = parts[0]
                        w, h = float(parts[1]), float(parts[2])
                        fixed = len(parts) >= 4 and parts[3] == "terminal"
                        netlist.add_cell(cid, w, h, fixed=fixed)

        # ---- .nets ----
        nets_path = base + ".nets"
        if os.path.isfile(nets_path):
            with open(nets_path) as f:
                current_net = None
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.lower().startswith("numnet") or \
                       line.lower().startswith("numpins"):
                        continue
                    if line.lower().startswith("netdegree"):
                        parts = line.split()
                        current_net = parts[-1].rstrip(":")
                        if current_net == ":":
                            current_net = None
                        else:
                            netlist.add_net(current_net)
                    elif current_net and (line.startswith("\t") or
                                          not line[0].isalpha() or
                                          len(line.split()) >= 2):
                        parts = line.split()
                        if parts:
                            cid = parts[0]
                            pin = parts[1] if len(parts) > 1 else ""
                            netlist.add_pin(cid, current_net, pin)

        # ---- .scl ----
        scl_path = base + ".scl"
        if os.path.isfile(scl_path):
            cols = rows = 0
            with open(scl_path) as f:
                for raw in f:
                    line = raw.strip()
                    parts = line.split()
                    if len(parts) >= 2:
                        if parts[0].lower() in ("columns", "cols"):
                            cols = int(parts[-1])
                        elif parts[0].lower() in ("rows",):
                            rows = int(parts[-1])
            die_width = float(cols) if cols else float(rows) * 2
            die_height = float(rows)

        # ---- .pl ----
        pl_path = base + ".pl"
        if os.path.isfile(pl_path):
            with open(pl_path) as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    if len(parts) >= 3:
                        cid, x, y = parts[0], float(parts[1]), float(parts[2])
                        init_placement[cid] = (x, y)

        if not netlist.cells:
            raise FileNotFoundError(
                f"No movable cells were parsed from benchmark '{name}' in '{benchmark_dir}'."
            )

        # Fall back: derive die from max placement coords
        if die_width == 0 and init_placement:
            xs = [v[0] for v in init_placement.values()]
            ys = [v[1] for v in init_placement.values()]
            die_width = max(xs) * 1.2
            die_height = max(ys) * 1.2

        return netlist, die_width, die_height, init_placement
