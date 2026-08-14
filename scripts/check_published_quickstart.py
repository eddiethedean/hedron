#!/usr/bin/env python3
"""Install an exact PyPI release and smoke the documented scaffold path."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_TOML = ROOT / "docs" / "release.toml"


def run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def expected_hedron_scaffold_pin(version: str, *, release_toml: Path = RELEASE_TOML) -> str:
    """Pin the published scaffold must contain (matches ``hedron new`` / release.toml)."""
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"invalid release version: {version!r}")
    if release_toml.is_file():
        release = tomllib.loads(release_toml.read_text(encoding="utf-8"))["release"]
        floor = str(release["pin_floor"]).strip()
        ceiling = str(release["pin_ceiling"]).strip()
        if floor != version:
            raise ValueError(
                f"release.toml pin_floor {floor!r} does not match published version {version!r}"
            )
        return f">={floor},<{ceiling}"
    train = ".".join(version.split(".")[:2])
    next_minor = f"0.{int(train.split('.')[1]) + 1}"
    return f">={version},<{next_minor}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--retry-seconds", type=float, default=20.0)
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        raise SystemExit(f"invalid release version: {args.version!r}")

    with tempfile.TemporaryDirectory(prefix="hedron-published-") as raw_tmp:
        tmp = Path(raw_tmp)
        environment = tmp / ".venv"
        run(["uv", "venv", str(environment), "--python", sys.executable], cwd=tmp)
        python = environment / "bin" / "python"
        if sys.platform == "win32":
            python = environment / "Scripts" / "python.exe"

        install = [
            "uv",
            "pip",
            "install",
            "--refresh",
            "--python",
            str(python),
            f"hedron=={args.version}",
            "uvicorn[standard]>=0.30",
        ]
        for attempt in range(1, args.attempts + 1):
            result = subprocess.run(install, cwd=tmp)
            if result.returncode == 0:
                break
            if attempt == args.attempts:
                raise SystemExit("published Hedron artifact was not installable")
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

    print(f"ok: PyPI hedron=={args.version} installs and its scaffold imports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
