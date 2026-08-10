#!/usr/bin/env python3
"""Install an exact PyPI release and smoke the documented scaffold path."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def run(command: list[str], *, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


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
        train = ".".join(args.version.split(".")[:2])
        next_minor = f"0.{int(train.split('.')[1]) + 1}"
        if f'"hedron>={train}.0,<{next_minor}"' not in pyproject:
            raise SystemExit("published scaffold contains the wrong Hedron train pin")

    print(f"ok: PyPI hedron=={args.version} installs and its scaffold imports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
