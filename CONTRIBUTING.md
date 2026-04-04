# Contributing to chuck

## Mission alignment

Every contribution should improve at least one of:

- average-case throughput
- average-case latency
- operational reliability
- portability across execution backends

## AI and LLM usage

- AI and LLM assistance is allowed.
- The final changes, reasoning, and submitted work must be your own.
- Do not attribute the contribution to AI during review or if questioned.
- Irresponsible AI use, including low-quality or unverified output, may be treated as spam.
- Contributions that do not follow this policy may be ignored and a PR may be closed without further justification.

## Structure

- put task logic in `chuck/tasks/<task>/task.py`
- put task-native C++ code in `chuck/tasks/<task>/native_cpp/binding.cpp`
- put benchmark wrappers in `chuck/benchmarks/`

The project uses task-owned native code, so Python and C++ changes for one capability should stay together.

## Performance and reliability policy

- optimize for average-case behavior first
- keep deterministic seeds for reproducible outputs
- when trading reliability for speed, document rationale and expected blast radius

## Pull request checklist

- [ ] updated or added relevant benchmark impact notes
- [ ] regenerated baselines if output changed
- [ ] passed regression tests
- [ ] updated docs (`README.md`, `docs/capabilities/*` as needed)

## Local commands

- `pre-commit install`
- `pre-commit run --all-files`
- `python -m pip install -e .`
- `python -m pip install pybind11`
- build native modules with `python scripts/setup_native.py`
- `python -m chuck generate-baselines`
- `python -m chuck regress`
- `python -m chuck bench`
- `python -m chuck snapshot --label local --backend auto`
- `python -m chuck compare --old data/reports/snapshots/old.json --new data/reports/snapshots/current.json`

If native modules are not built yet, `--backend cpp` falls back to Python.
When native code is involved, check that the compiled modules are present in `native/cpp/build/`.

For native changes, rebuild the modules before running regression or snapshot commands.

Platform note:

- Python-only workflows are fine on Linux, macOS, and Windows.
- Native C++ build helper is currently supported on Linux and macOS.
- Windows developers should use WSL2.
- For native C++ work on Windows, use WSL2 or a Linux/macOS environment.
- In WSL, use [scripts/setup_native.py](scripts/setup_native.py).


## A/B comparison workflow

Before claiming performance wins:

1. create old snapshot from reference commit: `python -m chuck snapshot --label old --backend python`
2. create current snapshot from your branch: `python -m chuck snapshot --label current --backend cpp`
3. compare: `python -m chuck compare --old data/reports/snapshots/old.json --new data/reports/snapshots/current.json`

Include the comparison output (speedup and reliability delta) in your PR summary.

If you are testing native code, note whether the snapshot actually used the C++ backend.

## Snapshot trust checks

Before trusting old-vs-new claims, run:

- `python -m chuck verify-snapshot --snapshot <snapshot.json>`

Only snapshots that pass verification should be used in performance/reliability comparisons.

## Pull request expectations

For code changes, please include:

- updated docs if behavior changed
- regression output if task results changed
- a note if native execution was tested or if it fell back to Python
- parity notes for deterministic tasks when C++ code is involved
