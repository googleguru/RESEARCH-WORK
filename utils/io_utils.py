"""I/O utilities for placement data"""

import json


def save_placement(placement, filename):
    """Save placement to JSON file.

    Args:
        placement: Placement dict {cell_id: (x, y)}
        filename: Output filename
    """
    # Convert tuples to lists for JSON serialization
    serializable = {cid: list(pos) for cid, pos in placement.items()}
    with open(filename, 'w') as f:
        json.dump(serializable, f, indent=2)


def load_placement(filename):
    """Load placement from JSON file.

    Args:
        filename: Input filename

    Returns:
        Placement dict
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    # Convert lists back to tuples
    return {cid: tuple(pos) for cid, pos in data.items()}


def save_netlist(netlist, filename):
    """Save netlist to JSON file."""
    data = {
        'cells': netlist.cells,
        'nets': netlist.nets
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def load_netlist(filename):
    """Load netlist from JSON file."""
    from placement_core.netlist import Netlist
    with open(filename, 'r') as f:
        data = json.load(f)

    netlist = Netlist()
    netlist.cells = data['cells']
    netlist.nets = data['nets']
    return netlist
