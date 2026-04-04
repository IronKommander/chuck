# Installation

This project runs as a Python package and can also use task-local C++ modules.

## Recommended setup

- Linux and macOS: use the native setup helper in [scripts/setup_native.py](../scripts/setup_native.py)
- WSL2: use the Linux/macOS helper, just like Linux
- If you use Windows, use WSL2

## Linux/macOS quick setup

```bash
python scripts/setup_native.py
```

## Native build prerequisites

Native C++ builds need a compiler, Python development headers, and `pybind11`.

On Fedora:

```bash
sudo dnf install -y gcc-c++ python3-devel
python -m pip install pybind11
```

`scripts/setup_native.py` installs `pybind11` and builds all 10 native modules into `native/cpp/build/`.

The loader checks `native/cpp/build/` first, so the compiled files do not need to sit in the repo root.

Supported platforms:

- Python package: Linux, macOS, Windows
- Native C++ helper: Linux and macOS today
- WSL2 native build: supported through the Linux helper
- Windows native work: use WSL2

## Verify the install

```bash
python -m chuck regress
python -m chuck bench
python -m chuck snapshot --label local-test --backend cpp
```

If native modules are not built yet, `backend="cpp"` falls back to Python.
