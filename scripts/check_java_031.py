#!/usr/bin/env python3
"""JAVA-031: Java conformance evaluator packaging + parity."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import fail_errors, require_files, require_inventory_supported  # noqa: E402

PKG = ROOT / "packages" / "hedron-runtime-java"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            PKG / "pom.xml",
            PKG / "scripts" / "run-conformance.sh",
            PKG / "src" / "main" / "java" / "io" / "hedron" / "runtime" / "ConformanceRuntime.java",
            ROOT / "docs" / "packages" / "hedron-runtime-java.md",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-runtime-java",
        (
            "published_signed_evaluator",
            "runtime_matrix",
            "python_reference_parity",
            "offline_conformance",
        ),
        errors,
    )
    pom = (PKG / "pom.xml").read_text(encoding="utf-8")
    if "<version>0.31.0</version>" not in pom:
        errors.append("pom.xml must declare version 0.31.0")
    if fail_errors(errors, "JAVA-031"):
        return 1
    script = PKG / "scripts" / "run-conformance.sh"
    cmd = ["bash", str(script)]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"JAVA-031 parity failed ({exc.returncode})", file=sys.stderr)
        return 1
    mvn = shutil.which("mvn")
    if mvn is not None:
        pack = [mvn, "-q", "-DskipTests", "package"]
        print("+", *pack)
        try:
            subprocess.check_call(pack, cwd=PKG)
        except subprocess.CalledProcessError as exc:
            print(f"JAVA-031 mvn package failed ({exc.returncode})", file=sys.stderr)
            return 1
    print("ok: JAVA-031")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
