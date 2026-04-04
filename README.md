# chuck

<p align="center">
  <img src="assets/chuck.gif" alt="Chuck Gif" width="520" />
</p>

`chuck` is a computational utility that solves 10 high-value data and algorithm tasks.
Benchmarks and regression checks are included to measure how fast each capability is, but solving tasks is the primary purpose.

## Installation

For a quick setup, see [docs/INSTALLATION.md](docs/INSTALLATION.md).

---

## Project direction

This project is intentionally **performance-first**:

- we optimize average-case throughput and latency
- we allow controlled reliability trade-offs where they improve speed
- we use probabilistic methods where exactness is expensive and confidence is acceptable
- we keep deterministic input generation so behavior remains testable and comparable

In short: this is a **solver toolkit with measurable performance**, not a benchmark-only repo.

---

## Core capabilities (10 tasks)

| Capability | Type | Notes |
|---|---|---|
| `io_pipeline` | deterministic | streaming ingest/transform/aggregate |
| `ordering_core` | deterministic | large-scale sorting and merge paths |
| `retrieval_core` | probabilistic | sampled indexing for faster query estimates |
| `data_encoding` | deterministic | compression and round-trip integrity |
| `graph_analytics` | deterministic | iterative graph scoring workload |
| `prime_analytics` | probabilistic | Miller–Rabin based prime discovery |
| `memory_tier` | deterministic | cache/tier behavior simulation |
| `memory_index` | probabilistic | Bloom-filter style membership checks |
| `compute_core` | deterministic | dense numeric compute kernels |
| `relational_fusion` | deterministic | join + aggregation fusion |

Each task has a short design note in `docs/capabilities/` with simple algorithm details.

---

## Native backend bindings

Python is the default runtime.
Native acceleration is organized per task with **C++-first** structure:

- each task owns its native entry at `chuck/tasks/<task>/native_cpp/binding.cpp`
- Python fallback dispatch: `chuck/native_bindings.py`

Runtime behavior:

- if per-task C++ modules in `native/cpp/build/` (for example `chuck_cpp_prime_analytics`) are present, `chuck` can use them
- otherwise it automatically falls back to Python solvers

Build the native modules with the helper script shown in [docs/INSTALLATION.md](docs/INSTALLATION.md): `python scripts/setup_native.py`.

If you use Windows, use WSL2 and follow the Linux helper path.

For native build details and local verification, see [docs/NATIVE_BINDINGS.md](docs/NATIVE_BINDINGS.md).

---

## Quick start

```bash
python -m chuck generate-baselines
python -m chuck regress
python -m chuck bench
python -m chuck bench --task prime_analytics
```

Detailed hands-on usage (task-by-task run, Python vs C++ compare, snapshots):

- [docs/TRY_AND_COMPARE.md](docs/TRY_AND_COMPARE.md)

---

## Why reliability is not forced to 100%

Some tasks expose `confidence` and are marked `probabilistic`.
This allows faster average-case execution while still reporting expected quality.

Snapshot comparisons continue to report both:

- speed changes
- reliability score changes

So trade-offs stay explicit and measurable.

---

## A/B comparison workflow

```bash
python -m chuck snapshot --label old --backend python
python -m chuck snapshot --label current --backend cpp
python -m chuck compare --old data/reports/snapshots/old.json --new data/reports/snapshots/current.json
python -m chuck verify-snapshot --snapshot data/reports/snapshots/current.json
```

`snapshot` and `compare --run-current` support `--backend {auto,python,cpp}`.

---

## Project structure

| Path | Role |
|---|---|
| `chuck/tasks/` | task generators + solvers |
| `chuck/benchmarks/` | per-task benchmark entrypoints |
| `chuck/native_bindings.py` | Python/native backend dispatch |
| `chuck/comparison.py` | snapshot + A/B comparison + verification |
| `data/<capability>/regression.json` | per-task baseline snapshots |
| `docs/capabilities/` | brief docs for each task |
| `chuck/tasks/<task>/native_cpp/binding.cpp` | task-owned C++ native entrypoint |

## Contributing

If you want to change code or docs, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## References for probabilistic direction

- https://staff.science.uva.nl/r.dehaan/complexity2021/files/lecture10.pdf
- https://www.cs.upc.edu/~mjserna/docencia/gm-aic/2021/12-AiC-Proba.pdf
- https://medium.com/pythoneers/randomized-algorithms-and-probabilistic-data-structures-f78691e2991d
- http://www.cs.man.ac.uk/~david/courses/advalgorithms/probabilistic.pdf
