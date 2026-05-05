"""Placement visualization utilities"""


class PlacementVisualizer:
    """Visualize placement results."""

    def __init__(self):
        """Initialize visualizer."""
        pass

    def plot_placement(self, placement, netlist, die_width, die_height,
                      filename=None, show=True):
        """Plot placement with matplotlib.

        Args:
            placement: Cell placement dict
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height
            filename: Output filename (if None, display only)
            show: Whether to display plot
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
        except ImportError:
            print("matplotlib required for visualization")
            return

        fig, ax = plt.subplots(figsize=(12, 10))

        # Draw die boundary
        die_patch = patches.Rectangle((0, 0), die_width, die_height,
                                     linewidth=2, edgecolor='black',
                                     facecolor='white', alpha=0.1)
        ax.add_patch(die_patch)

        # Draw cells
        for cell_id, (x, y) in placement.items():
            if cell_id in netlist.cells:
                w = netlist.cells[cell_id]['width']
                h = netlist.cells[cell_id]['height']
                cell_patch = patches.Rectangle((x, y), w, h,
                                              linewidth=1, edgecolor='blue',
                                              facecolor='cyan', alpha=0.5)
                ax.add_patch(cell_patch)
                ax.text(x + w/2, y + h/2, cell_id, ha='center', va='center',
                       fontsize=8)

        ax.set_xlim(-die_width*0.05, die_width*1.05)
        ax.set_ylim(-die_height*0.05, die_height*1.05)
        ax.set_aspect('equal')
        ax.set_xlabel('X (microns)')
        ax.set_ylabel('Y (microns)')
        ax.set_title('VLSI Cell Placement')
        ax.grid(True, alpha=0.3)

        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
        if show:
            plt.show()
        plt.close()

    def plot_wirelength_distribution(self, netlist, placement, filename=None):
        """Plot net wirelength distribution."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("matplotlib required for visualization")
            return

        wirelengths = []
        for net_id, net_info in netlist.nets.items():
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
                wirelengths.append(hpwl)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(wirelengths, bins=50, edgecolor='black', alpha=0.7)
        ax.set_xlabel('Wirelength')
        ax.set_ylabel('Number of Nets')
        ax.set_title('Net Wirelength Distribution')
        ax.grid(True, alpha=0.3)

        if filename:
            plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.show()
        plt.close()
