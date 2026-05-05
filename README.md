# Quantum-based VLSI Placement Algorithms

Quantum algorithms for VLSI physical design placement optimization using variational quantum approaches.

## Project Structure

- `quantum_placement/` - Core quantum placement algorithms
  - `qaoa/` - Quantum Approximate Optimization Algorithm implementation
  - `vqe/` - Variational Quantum Eigensolver approaches
  - `ansatz/` - Quantum circuit ansatzes for placement
- `classical_solver/` - Classical solvers for benchmarking and hybrid approaches
- `placement_core/` - VLSI placement logic and netlists
  - `legalization/` - Legalization algorithms
  - `netlist/` - Circuit netlist processing
  - `metrics/` - Placement quality metrics
- `benchmarks/` - VLSI test cases and evaluation
- `config/` - Configuration files and parameters
- `utils/` - Utility functions for optimization

## Features

- Variational Quantum Algorithms (QAOA, VQE)
- Hybrid classical-quantum optimization
- VLSI netlist parsing and processing
- Placement legalization and validation
- Performance metrics and benchmarking

## References

- VLSI Placement Optimization using quantum computing principles
- Framework inspiration: DREAMPlace architecture
