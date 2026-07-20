# Results scaffolding

## Quality table
- Use the generated LaTeX scaffold at [docs/quality_table.tex](quality_table.tex).
- Extend it with one row per benchmark and one column per method.

## Runtime table
- Use the `runtime_seconds` field from the experiment logs as the source of truth.
- Summarize each method by benchmark and report mean runtime over repeated seeds.

## Ablation figure
- Use [docs/ablation_sweeps.csv](ablation_sweeps.csv) as the parameter grid.
- Sweep one factor at a time while keeping all others fixed.

## Discussion framing
- Report the DREAMPlace gap plainly.
- Separate formulation effects from solver effects.
- State whether the quantum-inspired backends improve over the classical SA baseline under the same QUBO.
