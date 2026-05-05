"""
ISPD 2019 Benchmark Loader.

Supports the Bookshelf format used by ISPD 2019 placement contest:
  .nodes  — cell dimensions and fixed/movable flags
  .nets   — netlist connectivity (pin list per net)
  .pl     — initial placement (x, y, orientation)
  .scl    — site/row definitions → die dimensions
  .wts    — optional net weights

Reference circuits (all movable-cell counts are approximate):
  ispd2019_test1  ~  10k cells
  ispd2019_test2  ~  25k cells
  ispd2019_test3  ~  50k cells
  ispd2019_test4  ~  100k cells
  ispd2019_test5  ~  200k cells
  ispd2019_test6  ~  500k cells
  ispd2019_test7  ~  1M cells
  ispd2019_test8  ~  2M cells
  ispd2019_test9  ~  5M cells
"""

import os
from quantum_placement_database.netlist import QuantumNetlist


ISPD2019_BENCHMARKS = [
    "ispd2019_test1", "ispd2019_test2", "ispd2019_test3",
    "ispd2019_test4", "ispd2019_test5", "ispd2019_test6",
    "ispd2019_test7", "ispd2019_test8", "ispd2019_test9",
]


class ISPD2019BenchmarkLoader:
    """Load ISPD 2019 benchmark in Bookshelf format."""

    @staticmethod
    def benchmark_names() -> list[str]:
        return list(ISPD2019_BENCHMARKS)

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
                        # "NetDegree : <deg> <net_id>"
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

        # Fall back: derive die from max placement coords
        if die_width == 0 and init_placement:
            xs = [v[0] for v in init_placement.values()]
            ys = [v[1] for v in init_placement.values()]
            die_width = max(xs) * 1.2
            die_height = max(ys) * 1.2

        return netlist, die_width, die_height, init_placement
