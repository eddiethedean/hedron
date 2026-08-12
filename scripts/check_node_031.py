#!/usr/bin/env python3
"""NODE-031: Node conformance evaluator packaging + parity."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import fail_errors, require_files, require_inventory_supported  # noqa: E402

PKG = ROOT / "packages" / "hedron-runtime-node"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            PKG / "package.json",
            PKG / "bin" / "run-conformance.mjs",
            PKG / "lib" / "runtime.mjs",
            PKG / "fixtures" / "portable_v1.json",
            ROOT / "docs" / "packages" / "hedron-runtime-node.md",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-runtime-node",
        (
            "published_signed_evaluator",
            "runtime_matrix",
            "python_reference_parity",
            "offline_conformance",
        ),
        errors,
    )
    meta = json.loads((PKG / "package.json").read_text(encoding="utf-8"))
    if meta.get("private") is True:
        errors.append("package.json must not be private for NODE-031 publish readiness")
    if str(meta.get("version", "")) != "0.31.0":
        errors.append(f"expected version 0.31.0, found {meta.get('version')!r}")
    if fail_errors(errors, "NODE-031"):
        return 1
    node = shutil.which("node")
    if node is None:
        print("NODE-031: node not installed", file=sys.stderr)
        return 1
    cmd = [node, str(PKG / "bin" / "run-conformance.mjs")]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"NODE-031 parity failed ({exc.returncode})", file=sys.stderr)
        return 1
    # Packaging dry-run when npm is available
    npm = shutil.which("npm")
    if npm is not None:
        pack = [npm, "pack", "--dry-run"]
        print("+", *pack)
        try:
            subprocess.check_call(pack, cwd=PKG)
        except subprocess.CalledProcessError as exc:
            print(f"NODE-031 npm pack dry-run failed ({exc.returncode})", file=sys.stderr)
            return 1
    print("ok: NODE-031")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
