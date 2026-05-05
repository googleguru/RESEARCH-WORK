"""Placement configuration"""


class PlacementConfig:
    """Configuration parameters for placement algorithms."""

    def __init__(self):
        """Initialize default configuration."""
        # Die configuration
        self.die_width = 1000.0
        self.die_height = 1000.0
        self.grid_unit = 1.0

        # Quantum algorithm parameters
        self.qaoa_depth = 5
        self.qaoa_iterations = 100
        self.vqe_ansatz_depth = 3
        self.vqe_max_iterations = 1000

        # Classical algorithm parameters
        self.genetic_pop_size = 100
        self.genetic_generations = 50
        self.sa_initial_temp = 1000
        self.sa_cooling_rate = 0.95

        # Optimization weights
        self.wirelength_weight = 1.0
        self.overlap_weight = 10.0
        self.boundary_weight = 0.1

    def from_dict(self, config_dict):
        """Load configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """Convert configuration to dictionary."""
        return {
            'die_width': self.die_width,
            'die_height': self.die_height,
            'grid_unit': self.grid_unit,
            'qaoa_depth': self.qaoa_depth,
            'qaoa_iterations': self.qaoa_iterations,
            'vqe_ansatz_depth': self.vqe_ansatz_depth,
            'vqe_max_iterations': self.vqe_max_iterations,
            'genetic_pop_size': self.genetic_pop_size,
            'genetic_generations': self.genetic_generations,
            'sa_initial_temp': self.sa_initial_temp,
            'sa_cooling_rate': self.sa_cooling_rate,
            'wirelength_weight': self.wirelength_weight,
            'overlap_weight': self.overlap_weight,
            'boundary_weight': self.boundary_weight,
        }
