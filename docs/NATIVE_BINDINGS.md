# Native bindings

`chuck` uses a task-owned native layout designed for larger codebases.

## Structure

Each capability owns its native C++ entrypoint:

- `chuck/tasks/<task>/task.py` → Python reference implementation
- `chuck/tasks/<task>/native_cpp/binding.cpp` → C++ native binding entry

This keeps ownership local: task logic and task-native logic evolve together.

## Dispatch behavior

`chuck/native_bindings.py` resolves backends in this order for `backend="auto"`:

1. C++ per-task module (for example `chuck_cpp_prime_analytics`)
2. Python reference implementation

## How to build locally

Build requirements:

- a C++ compiler
- Python development headers
- `pybind11`

Once those are installed, build each task module as an importable extension named like `chuck_cpp_<task>`.
Use the helper script:

```bash
python scripts/setup_native.py
```

That script places the compiled modules in `native/cpp/build/`; `chuck` adds that folder to the import path automatically.
If the native module is missing, `chuck` falls back to Python automatically.

If you want to skip the dependency install and only rebuild, use:

```bash
python scripts/setup_native.py --skip-install
```

Platform note:

- Linux/macOS native builds are supported with this helper.
- Windows support is still pending for the native helper.

## Why this layout

- clearer ownership boundaries per capability
- easier incremental migration from Python to C++
- easier code reviews: one task folder contains all relevant artifacts
- aligns better with industry monorepo patterns for mixed-language systems

## Current status

Task-local C++ binding scaffolds exist for all 10 capabilities.
Current implementation coverage:

- implemented for all 10 tasks:
	- `io_pipeline`
	- `ordering_core`
	- `retrieval_core`
	- `data_encoding`
	- `graph_analytics`
	- `prime_analytics`
	- `memory_tier`
	- `memory_index`
	- `compute_core`
	- `relational_fusion`

CI now includes a C++ compile-smoke job that syntax-checks every task-local `binding.cpp` with `pybind11` headers.

## Snapshot and compare with backend control

You can now choose backend preference in snapshots:

```bash
python -m chuck snapshot --label py-baseline --backend python
python -m chuck snapshot --label cpp-run --backend cpp
python -m chuck compare --old data/reports/snapshots/py-baseline.json --new data/reports/snapshots/cpp-run.json
```

Comparison output reports backend preference metadata from both snapshots.

Important: a snapshot with `--backend cpp` only proves that the C++ path was requested.
To confirm true native runtime use, the `backend_counts` fields in the snapshot should show `cpp`.

## Next step

- Add a build helper or packaging script for native modules.
- Add explicit Python-vs-C++ parity tests for deterministic tasks.
- Add tolerance-based parity checks for probabilistic tasks.
