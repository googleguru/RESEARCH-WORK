"""Generate an ablation sweep configuration template for paper experiments."""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def write_ablation_template(out_path: str):
    rows = [
        {"name": "density_weight", "values": "1.0, 4.0, 8.0, 16.0"},
        {"name": "bits_per_dim", "values": "2, 3, 4"},
        {"name": "qaoa_depth", "values": "1, 2, 3"},
        {"name": "ansatz_family", "values": "hardware_efficient, problem_inspired"},
        {"name": "refinement_budget", "values": "1, 3, 5"},
    ]
    with open(out_path, "w") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "values"])
        writer.writeheader()
        writer.writerows(rows)


def main():
    out_dir = "docs"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ablation_sweeps.csv")
    write_ablation_template(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
