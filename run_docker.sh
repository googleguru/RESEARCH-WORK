#!/bin/bash

# Quantum VLSI Placement Docker Runner
# This script builds and runs the quantum placement visualization in Docker

set -e

echo "Building Docker image for Quantum VLSI Placement..."
docker build -t quantum-vlsi-placement .

echo "Creating output directory..."
mkdir -p output

echo "Running quantum placement visualization..."
docker run --rm -v $(pwd)/output:/app/output quantum-vlsi-placement \
    python generate_ispd2019_visualization.py \
    --num_cells 50 \
    --algorithm quantum_annealing \
    --out_dir /app/output

echo "Visualization complete! Output files saved to ./output/"
echo "Generated files:"
ls -la output/