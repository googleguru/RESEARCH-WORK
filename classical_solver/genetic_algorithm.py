"""Genetic algorithm for VLSI placement"""

import random


class GeneticPlacementSolver:
    """Genetic algorithm-based placement optimizer."""

    def __init__(self, population_size=100, generations=50):
        """Initialize GA solver.

        Args:
            population_size: Number of individuals per generation
            generations: Number of generations to evolve
        """
        self.pop_size = population_size
        self.generations = generations

    def solve(self, netlist, die_width, die_height):
        """Solve placement using genetic algorithm.

        Args:
            netlist: Circuit netlist
            die_width: Die width
            die_height: Die height

        Returns:
            Best placement found
        """
        # Initialize population
        population = self._initialize_population(netlist, die_width, die_height)

        # Evolve for specified generations
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_scores = [self._evaluate_fitness(ind, netlist)
                            for ind in population]

            # Selection
            parents = self._selection(population, fitness_scores)

            # Crossover and mutation
            offspring = []
            for _ in range(self.pop_size):
                parent1, parent2 = random.sample(parents, 2)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child, netlist, die_width, die_height)
                offspring.append(child)

            population = offspring

        # Return best solution
        best_idx = min(range(len(population)),
                      key=lambda i: self._evaluate_fitness(population[i], netlist))
        return population[best_idx]

    def _initialize_population(self, netlist, die_width, die_height):
        """Generate initial population."""
        population = []
        for _ in range(self.pop_size):
            placement = {}
            for cell_id in netlist.cells:
                x = random.uniform(0, die_width)
                y = random.uniform(0, die_height)
                placement[cell_id] = (x, y)
            population.append(placement)
        return population

    def _evaluate_fitness(self, placement, netlist):
        """Evaluate placement fitness (cost)."""
        from placement_core.metrics import PlacementMetrics
        cost = PlacementMetrics.half_perimeter_wirelength(placement, netlist)
        return cost

    def _selection(self, population, fitness):
        """Select parents via tournament selection."""
        parents = []
        for _ in range(len(population)):
            # Tournament of size 3
            idx = min(random.sample(range(len(population)), 3),
                     key=lambda i: fitness[i])
            parents.append(population[idx])
        return parents

    def _crossover(self, parent1, parent2):
        """Uniform crossover."""
        child = {}
        for cell_id in parent1:
            if random.random() < 0.5:
                child[cell_id] = parent1[cell_id]
            else:
                child[cell_id] = parent2[cell_id]
        return child

    def _mutate(self, placement, netlist, die_width, die_height):
        """Gaussian mutation of positions."""
        mutated = placement.copy()
        for cell_id in mutated:
            if random.random() < 0.2:  # 20% mutation rate
                x, y = mutated[cell_id]
                x += random.gauss(0, die_width * 0.05)
                y += random.gauss(0, die_height * 0.05)
                x = max(0, min(x, die_width))
                y = max(0, min(y, die_height))
                mutated[cell_id] = (x, y)
        return mutated
