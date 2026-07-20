# Academic revision note

This project is best positioned as a quantum-inspired placement prototype for
research and education rather than as a production-scale placement engine.
The core contribution is an end-to-end workflow for translating placement
objectives into a compact QUBO formulation, exploring solver behavior across
QAOA, VQE, and annealing-inspired search strategies, and producing interpretable
visualizations of intermediate placements.

## Technical contribution
- The framework builds a modular pipeline from netlist representation to QUBO
  construction, solver execution, placement decoding, legalization, and
  refinement.
- It exposes solver behavior through explicit metrics such as HPWL, overlap,
  and boundary violations, which makes it suitable for controlled experiments
  and qualitative analysis.
- The implementation is intentionally lightweight and transparent so that the
  underlying optimization structure can be studied directly.

## Suggested framing for reviewers and readers
- Emphasize the methodological value of the QUBO formulation and the modular
  solver stack.
- Highlight the reproducibility of the workflow through synthetic benchmark
  generation, configurable seeds, and transparent metrics.
- State limitations clearly: the current implementation does not claim to
  outperform established placers such as DREAMPlace, Cadence Innovus, or
  Synopsys ICC, nor to represent practical deployment on real quantum hardware
  at industrial scale.

## Suggested paper-style positioning
The proposed framework is a modular testbed for studying quantum-inspired
optimization for global placement. It is particularly useful for algorithmic
exploration, visualization, and benchmarking of QUBO formulations on small to
medium-sized synthetic instances. The work is best framed as complementary to,
rather than a replacement for, the mature analytical placement flows used in
industry.
