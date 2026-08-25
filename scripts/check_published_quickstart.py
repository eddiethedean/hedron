#!/usr/bin/env python3
"""Smoke the documented scaffold path from PyPI or locally built wheels."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def expected_hedron_scaffold_pin(version: str) -> str:
    """Return the pin a standalone wheel of ``version`` must scaffold.

    Published wheels derive this window from their own version, not from the
    checkout's ``docs/release.toml``. Keeping this verifier artifact-relative
    prevents stale public-release facts from breaking a new minor release after
    immutable packages have already been uploaded.
    """
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid release version: {version!r}")
    major, minor, _patch = (int(part) for part in version.split("."))
    return f">={version},<{major}.{minor + 1}"


def find_wheel(dist_dir: Path, distribution: str, version: str) -> Path:
    """Resolve one pure-Python wheel for an exact local distribution version."""
    normalized = distribution.replace("-", "_")
    matches = sorted(dist_dir.glob(f"{normalized}-{version}-py3-none-any.whl"))
    if len(matches) != 1:
        found = ", ".join(path.name for path in matches) or "none"
        raise ValueError(
            f"expected exactly one {distribution}=={version} wheel in {dist_dir}; found {found}"
        )
    return matches[0].resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--retry-seconds", type=float, default=20.0)
    parser.add_argument(
        "--dist-dir",
        type=Path,
        help="Install the exact hedron and hedron-core wheels from this directory instead of PyPI",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        raise SystemExit(f"invalid release version: {args.version!r}")
    if args.attempts < 1:
        raise SystemExit("--attempts must be at least 1")

    local_wheels: list[Path] = []
    if args.dist_dir is not None:
        dist_dir = args.dist_dir.resolve()
        try:
            local_wheels = [
                find_wheel(dist_dir, "hedron-core", args.version),
                find_wheel(dist_dir, "hedron", args.version),
            ]
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

    with tempfile.TemporaryDirectory(prefix="hedron-published-") as raw_tmp:
        tmp = Path(raw_tmp)
        environment = tmp / ".venv"
        run(["uv", "venv", str(environment), "--python", sys.executable], cwd=tmp)
        python = environment / "bin" / "python"
        if sys.platform == "win32":
            python = environment / "Scripts" / "python.exe"

        requirement = [str(path) for path in local_wheels] or [f"hedron=={args.version}"]
        install = ["uv", "pip", "install", "--refresh", "--python", str(python)]
        install.extend([*requirement, "uvicorn[standard]>=0.30"])
        attempts = 1 if local_wheels else args.attempts
        for attempt in range(1, attempts + 1):
            result = subprocess.run(install, cwd=tmp)
            if result.returncode == 0:
                break
            if attempt == attempts:
                source = "local Hedron wheels" if local_wheels else "published Hedron artifact"
                raise SystemExit(f"{source} was not installable")
            print(f"PyPI not ready (attempt {attempt}); retrying", flush=True)
            time.sleep(args.retry_seconds)

        run(
            [
                str(python),
                "-c",
                (f"import importlib.metadata as m; assert m.version('hedron') == '{args.version}'"),
            ],
            cwd=tmp,
        )
        project = tmp / "my-hedron-app"
        run([str(python), "-m", "hedron", "new", project.name], cwd=tmp)
        run(
            [
                str(python),
                "-c",
                "import sys; sys.path.insert(0, '.'); import app; assert app.app.routes",
            ],
            cwd=project,
        )
        pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
        expected = f'"hedron{expected_hedron_scaffold_pin(args.version)}"'
        if expected not in pyproject:
            raise SystemExit(
                f"published scaffold contains the wrong Hedron train pin (expected {expected})"
            )

    source = "local wheels" if local_wheels else "PyPI"
    print(f"ok: {source} hedron=={args.version} installs and its scaffold imports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
