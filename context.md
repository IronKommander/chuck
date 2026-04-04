# chuck context

## Current status (completed in this revamp)

1. Repositioned project direction
   - `chuck` is now documented as a solver utility for 10 computational tasks.
   - Benchmarks are supporting tooling, not the primary product.

2. Replaced an unsuitable capability
   - `execution_orchestrator` has been replaced by `prime_analytics`.
   - Prime task uses probabilistic Miller–Rabin style checking.

3. Added probabilistic reliability semantics
   - `TaskSpec` now includes `algorithm_style` and `reliability_floor` metadata.
   - Snapshot reliability scoring now supports confidence-weighted probabilistic tasks.

4. Added native backend binding path
   - Python dispatch layer: `chuck/native_bindings.py`.
   - C++ support moved into each task package at `chuck/tasks/<task>/native_cpp/binding.cpp`.
   - Backend lookup is now C++-first and task-local.
   - Auto-fallback to Python when native modules are unavailable.
   - real C++ implementations now exist for all 10 tasks (`io_pipeline`, `ordering_core`, `retrieval_core`, `data_encoding`, `graph_analytics`, `prime_analytics`, `memory_tier`, `memory_index`, `compute_core`, `relational_fusion`).

5. Updated docs
   - README fully rewritten for the new ideology.
   - capability docs updated for all 10 tasks with simple algorithm-design sections.
   - added `docs/TRY_AND_COMPARE.md` with task-by-task run, Python-vs-C++ compare, snapshot, compare, and verify steps.

6. Updated comparison flow for new backend design
   - `snapshot` now supports explicit `--backend {auto,python,cpp}`.
   - `compare --run-current` now supports explicit `--backend {auto,python,cpp}`.
   - snapshot metadata now records backend preference and comparison output reports it.

## What is still needed

1. Harden and optimize C++ kernels
   - Add cross-checked parity tests against Python outputs for non-probabilistic tasks.
   - Optimize hot kernels (compute/graph/retrieval) for throughput and memory locality.

2. C++ backend build automation
   - Add build scripts/wheels for Linux/macOS/Windows.
   - CI now includes a compile-smoke job (`pybind11` header + `-fsyntax-only`) for all task-local C++ bindings.
   - Add runtime-linked module build/test jobs per OS as next step.

3. Accuracy/performance guardrails for probabilistic tasks
   - Define per-task minimum confidence thresholds.
   - Add tests for acceptable error envelopes and drift limits.

4. Optional: add more probabilistic tasks
   - approximate quantiles
   - heavy-hitter sketches
   - cardinality estimation (HyperLogLog style)

5. Optional: benchmark profile tiers
   - `exact` mode (higher reliability)
   - `fast` mode (probabilistic/high throughput)

## Notes for next contributors

- Run these after task changes:
  - `python -m chuck generate-baselines`
  - `python -m chuck regress`
  - `python -m chuck bench`
- If native backends are not compiled, Python fallback is expected behavior.
