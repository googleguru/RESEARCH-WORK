FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create output directory
RUN mkdir -p docs

# Set the default command to run the visualization script
CMD ["python", "generate_ispd2019_visualization.py", "--num_cells", "50", "--algorithm", "quantum_annealing"]