"""
Quantum VLSI Placer — main placement engine.

Architecture mirrors DREAMPlace but with quantum operators:
  1. Build QUBO from wirelength + density operators
  2. Solve QUBO with QAOA / VQE / Quantum Annealing
  3. Decode bitstring to grid placement
  4. Legalize with QuantumLegalizer
  5. Iteratively refine critical-net regions
"""

import random
from quantum_placement_config import QuantumPlacerConfig
from quantum_placement_operators import (
    QUBOWirelengthOperator,
    QUBODensityOperator,
    QuantumLegalizer,
)
from quantum_placement_algorithms.qaoa import QAOAPlacer
from quantum_placement_algorithms.vqe import VQEPlacer
from quantum_placement_algorithms.quantum_annealing import QuantumAnnealer
from quantum_placement_metrics import QuantumPlacementMetrics


class QuantumVLSIPlacer:
    """
    Main quantum placement engine.

    Parameters
    ----------
    netlist    : QuantumNetlist
    die_width  : float
    die_height : float
    config     : QuantumPlacerConfig
    """

    def __init__(self, netlist, die_width: float, die_height: float,
                 config: QuantumPlacerConfig | None = None):
        self.netlist = netlist
        self.die_width = die_width
        self.die_height = die_height
        self.cfg = config or QuantumPlacerConfig()
        self._history: list[dict] = []

    # ------------------------------------------------------------------ public

    def run(self) -> dict[str, tuple[float, float]]:
        """Full quantum placement flow. Returns final legal placement."""
        print(f"\n{'Quantum VLSI Placement':=^60}")
        print(f"  Cells     : {self.netlist.cell_count}")
        print(f"  Nets      : {self.netlist.net_count}")
        print(f"  Die       : {self.die_width:.1f} × {self.die_height:.1f}")
        print(f"  Algorithm : {self.cfg.algorithm.upper()}")

        # Step 1 — Build QUBO
        wl_op = QUBOWirelengthOperator(
            self.netlist, self.die_width, self.die_height,
            bits_per_dim=self.cfg.bits_per_dim)
        dn_op = QUBODensityOperator(
            self.netlist, self.die_width, self.die_height,
            bits_per_dim=self.cfg.bits_per_dim)

        Q_wl = wl_op.build(self.cfg.wl_weight)
        Q_dn = dn_op.build(self.cfg.density_weight)
        Q_wl.merge(Q_dn, weight=1.0)
        combined_Q = Q_wl
        num_qubits = wl_op.num_qubits

        print(f"  QUBO size : {num_qubits} qubits, {combined_Q.nnz()} terms")

        # Step 2 — Quantum solve
        bits = self._quantum_solve(combined_Q.Q, num_qubits)

        # Step 3 — Decode to continuous placement
        placement = wl_op.decode_placement(bits)
        self._log("Global (Quantum)", placement)

        # Step 4 — Legalize
        legalizer = QuantumLegalizer(row_height=self.cfg.row_height)
        placement = legalizer.legalize(
            placement, self.netlist, self.die_width, self.die_height)
        self._log("Legalised", placement)

        # Step 5 — Critical-net refinement
        for it in range(self.cfg.refinement_iterations):
            placement = self._refine_critical_nets(placement, it)
            placement = legalizer.legalize(
                placement, self.netlist, self.die_width, self.die_height)
            self._log(f"Refinement iter {it+1}", placement)

        print("=" * 60)
        return placement

    # ------------------------------------------------------------------ internals

    def _quantum_solve(self, Q: dict, num_qubits: int) -> str:
        algo = self.cfg.algorithm.lower()

        if algo == "qaoa":
            solver = QAOAPlacer(
                Q, num_qubits,
                p_depth=self.cfg.qaoa_depth,
                shots=self.cfg.qaoa_shots)
            result = solver.run(max_iter=self.cfg.qaoa_max_iter)
        elif algo == "vqe":
            solver = VQEPlacer(
                Q, num_qubits,
                ansatz_type=self.cfg.vqe_ansatz,
                depth=self.cfg.vqe_depth,
                shots=self.cfg.vqe_shots)
            result = solver.run(max_iter=self.cfg.vqe_max_iter)
        elif algo == "quantum_annealing":
            solver = QuantumAnnealer(Q, num_qubits,
                                     num_replicas=self.cfg.qa_num_replicas)
            result = solver.run(
                num_sweeps=self.cfg.qa_sweeps,
                T_start=self.cfg.qa_T_start, T_end=self.cfg.qa_T_end,
                Gamma_start=self.cfg.qa_Gamma_start,
                Gamma_end=self.cfg.qa_Gamma_end)
        else:
            raise ValueError(f"Unknown algorithm: {self.cfg.algorithm}")

        return result.placement.get("_bitstring", "0" * num_qubits)

    def _refine_critical_nets(self, placement: dict, iteration: int) -> dict:
        """Move cells connected to high-HPWL nets toward their net centroid."""
        # Identify top-10 critical nets by HPWL
        net_hpwl = []
        for net_id, net_info in self.netlist.nets.items():
            xs = [placement[c][0] for c, _ in net_info["pins"] if c in placement]
            ys = [placement[c][1] for c, _ in net_info["pins"] if c in placement]
            if len(xs) >= 2:
                net_hpwl.append((net_id, (max(xs) - min(xs)) + (max(ys) - min(ys))))
        net_hpwl.sort(key=lambda x: x[1], reverse=True)
        critical = {n for n, _ in net_hpwl[:10]}

        refined = dict(placement)
        rng = random.Random(iteration)

        for net_id in critical:
            pins = self.netlist.nets[net_id]["pins"]
            movable = [c for c, _ in pins
                       if c in placement and not self.netlist.cells[c]["fixed"]]
            if not movable:
                continue
            cx = sum(placement[c][0] for c in movable) / len(movable)
            cy = sum(placement[c][1] for c in movable) / len(movable)

            for cid in movable:
                x, y = refined[cid]
                w = self.netlist.cells[cid]["width"]
                h = self.netlist.cells[cid]["height"]
                step = rng.gauss(0, 2.0)
                new_x = max(0.0, min(x + (cx - x) * 0.3 + step,
                                     self.die_width - w))
                new_y = max(0.0, min(y + (cy - y) * 0.3 + step,
                                     self.die_height - h))
                refined[cid] = (new_x, new_y)

        return refined

    def _log(self, label: str, placement: dict):
        hpwl = QuantumPlacementMetrics.hpwl(placement, self.netlist)
        ov = QuantumPlacementMetrics.total_overlap_area(placement, self.netlist)
        bv = QuantumPlacementMetrics.boundary_violations(
            placement, self.netlist, self.die_width, self.die_height)
        entry = {"stage": label, "hpwl": hpwl, "overlap": ov, "boundary": bv}
        self._history.append(entry)
        print(f"  {label:30s}  HPWL={hpwl:10.2f}  "
              f"Overlap={ov:8.2f}  BndViol={bv:8.2f}")
