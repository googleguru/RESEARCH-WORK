"""Netlist parser for VLSI circuits"""


class Netlist:
    """VLSI circuit netlist representation."""

    def __init__(self):
        """Initialize empty netlist."""
        self.cells = {}  # {cell_id: Cell}
        self.nets = {}   # {net_id: Net}
        self.pins = {}   # {pin_id: Pin}

    def add_cell(self, cell_id, width, height, cell_type='standard'):
        """Add cell to netlist.

        Args:
            cell_id: Unique cell identifier
            width: Cell width in microns
            height: Cell height in microns
            cell_type: Cell type (standard, macro, pad, etc.)
        """
        self.cells[cell_id] = {
            'width': width,
            'height': height,
            'type': cell_type,
            'pins': []
        }

    def add_net(self, net_id, net_type='signal'):
        """Add net to netlist.

        Args:
            net_id: Unique net identifier
            net_type: Net type (signal, clock, power, ground)
        """
        self.nets[net_id] = {
            'type': net_type,
            'pins': []
        }

    def add_connection(self, cell_id, net_id, pin_name):
        """Connect cell pin to net.

        Args:
            cell_id: Cell identifier
            net_id: Net identifier
            pin_name: Pin name
        """
        if cell_id in self.cells and net_id in self.nets:
            self.cells[cell_id]['pins'].append((net_id, pin_name))
            self.nets[net_id]['pins'].append((cell_id, pin_name))

    def get_cell_count(self):
        """Return number of cells."""
        return len(self.cells)

    def get_net_count(self):
        """Return number of nets."""
        return len(self.nets)

    def get_cell_area(self, cell_id):
        """Get cell area in square microns."""
        if cell_id in self.cells:
            c = self.cells[cell_id]
            return c['width'] * c['height']
        return 0

    def get_total_area(self):
        """Get total cell area."""
        return sum(self.get_cell_area(cid) for cid in self.cells)
