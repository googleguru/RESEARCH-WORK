"""Benchmark evaluation framework"""

import time
from placement_core.metrics import PlacementMetrics


class BenchmarkEvaluator:
    """Evaluate placement algorithm performance."""

    def __init__(self):
        """Initialize evaluator."""
        self.results = []

    def evaluate_algorithm(self, solver, netlist, die_width, die_height, name):
        """Run algorithm and measure performance.

        Args:
            solver: Placement solver object
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            name: Algorithm name for reporting

        Returns:
            Result dict with metrics
        """
        # Measure execution time
        start_time = time.time()
        placement = solver.solve(netlist, die_width, die_height)
        elapsed = time.time() - start_time

        # Compute quality metrics
        hpwl = PlacementMetrics.half_perimeter_wirelength(placement, netlist)
        total_area = netlist.get_total_area()

        result = {
            'algorithm': name,
            'cells': netlist.get_cell_count(),
            'nets': netlist.get_net_count(),
            'hpwl': hpwl,
            'time_sec': elapsed,
            'total_area': total_area,
            'placement': placement
        }

        self.results.append(result)
        return result

    def print_summary(self):
        """Print benchmark summary."""
        if not self.results:
            print("No results to report")
            return

        print("\n" + "="*70)
        print("PLACEMENT BENCHMARK RESULTS")
        print("="*70)

        for result in self.results:
            print(f"\nAlgorithm: {result['algorithm']}")
            print(f"  Cells: {result['cells']}, Nets: {result['nets']}")
            print(f"  HPWL: {result['hpwl']:.2f}")
            print(f"  Time: {result['time_sec']:.4f}s")
            print(f"  Total Area: {result['total_area']:.2f}")

        print("\n" + "="*70)

    def compare_algorithms(self):
        """Compare algorithm performance."""
        if len(self.results) < 2:
            print("Need at least 2 results for comparison")
            return

        baseline = self.results[0]
        print(f"\nComparison relative to {baseline['algorithm']}:")
        baseline_hpwl = baseline['hpwl']

        for result in self.results[1:]:
            hpwl_ratio = result['hpwl'] / baseline_hpwl
            time_ratio = result['time_sec'] / baseline['time_sec']
            print(f"\n{result['algorithm']}:")
            print(f"  HPWL: {hpwl_ratio:.2%}")
            print(f"  Time: {time_ratio:.2%}")
