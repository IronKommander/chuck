from __future__ import annotations

import argparse
import pathlib
import platform
import shutil
import subprocess
import sys
import sysconfig


TASKS = [
    "io_pipeline",
    "ordering_core",
    "retrieval_core",
    "data_encoding",
    "graph_analytics",
    "prime_analytics",
    "memory_tier",
    "memory_index",
    "compute_core",
    "relational_fusion",
]


def _run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def _compiler() -> str:
    env = shutil.which("c++") or shutil.which("clang++") or shutil.which("g++")
    if env:
        return env
    raise SystemExit("No C++ compiler found. Install c++/clang++/g++ first.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install pybind11 and build chuck native modules")
    parser.add_argument("--skip-install", action="store_true", help="Skip pip install of pybind11")
    parser.add_argument("--clean", action="store_true", help="Remove existing compiled modules before building")
    args = parser.parse_args()

    root = pathlib.Path(__file__).resolve().parents[1]
    build_dir = root / "native" / "cpp" / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    if args.clean:
        for file_path in build_dir.glob("chuck_cpp_*"):
            file_path.unlink()

    if not args.skip_install:
        _run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "pybind11"])

    import pybind11  # noqa: WPS433

    pyinc = sysconfig.get_paths()["include"]
    pbinc = pybind11.get_include()
    ext = sysconfig.get_config_var("EXT_SUFFIX")
    compiler = _compiler()

    if platform.system() == "Windows":
        raise SystemExit(
            "Windows native builds are not wired in this helper yet. Use Linux/macOS or add a Windows build toolchain first."
        )

    for task in TASKS:
        src = root / "chuck" / "tasks" / task / "native_cpp" / "binding.cpp"
        out = build_dir / f"chuck_cpp_{task}{ext}"
        _run([
            compiler,
            "-O3",
            "-Wall",
            "-shared",
            "-std=c++17",
            "-fPIC",
            f"-I{pyinc}",
            f"-I{pbinc}",
            str(src),
            "-o",
            str(out),
        ])

    print(f"Built {len(TASKS)} native modules in {build_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
