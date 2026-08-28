#!/usr/bin/env python3
"""DX-030: CLI check/dry-run, docs, redaction, FWB-* / HED-WB-* catalog."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import (  # noqa: E402
    FWB_PKG,
    HED_WB_PKG,
    require_files,
    run_pytest,
    workbench_pytest_paths,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "guides" / "posit-workbench.md",
            ROOT / "docs" / "packages" / "hedron-workbench.md",
            FWB_PKG / "README.md",
            HED_WB_PKG / "README.md",
            ROOT / "docs" / "guides" / "error-codes.md",
            ROOT / "examples" / "workbench-reference" / "app.py",
            ROOT / "examples" / "workbench-reference" / "app_facade.py",
            ROOT / "examples" / "workbench-reference" / "README.md",
        ],
        errors,
    )
    guide = (ROOT / "docs" / "guides" / "posit-workbench.md").read_text(encoding="utf-8")
    for needle in (
        "HedronWorkbench",
        "hedron-workbench run",
        "hedron-workbench check",
        "HEDRON_ROOT_PATH",
        "fastapi-workbench",
    ):
        if needle not in guide:
            errors.append(f"posit-workbench.md missing {needle!r}")
    fwb_readme = (FWB_PKG / "README.md").read_text(encoding="utf-8")
    if "fastapi-workbench run" not in fwb_readme:
        errors.append("fastapi-workbench README missing run command")
    codes = (ROOT / "docs" / "guides" / "error-codes.md").read_text(encoding="utf-8")
    if "## HED-WB" not in codes or "HED-WB-0001" not in codes:
        errors.append("error-codes.md missing HED-WB table")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    for module in ("fastapi_workbench.cli", "hedron_workbench.cli"):
        check = subprocess.run(
            [sys.executable, "-m", module, "check", "--format", "json", "--mode", "off"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if check.returncode != 0:
            print(check.stderr or check.stdout, file=sys.stderr)
            return 1
        payload = json.loads(check.stdout)
        for key in ("mode", "bind", "browser_mount", "cookie_mount", "source"):
            if key not in payload:
                print(f"{module} check JSON missing {key}", file=sys.stderr)
                return 1
        if payload["browser_mount"] != "":
            print(f"{module} mode=off must clear browser_mount", file=sys.stderr)
            return 1

    paths = ["tests/adapters/workbench/test_cli.py", *workbench_pytest_paths()]
    if run_pytest(list(dict.fromkeys(paths)), "DX-030"):
        return 1
    print("ok: DX-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
