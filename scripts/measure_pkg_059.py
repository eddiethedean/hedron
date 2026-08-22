#!/usr/bin/env python3
"""Verify the clean phase 0.59 package build without installing dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    wheels = sorted(DIST.glob("*.whl"))
    sdists = sorted(DIST.glob("*.tar.gz"))
    errors: list[str] = []
    package_rows: list[dict[str, object]] = []
    for wheel in wheels:
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            if not any(name.endswith("/WHEEL") for name in names):
                errors.append(f"{wheel.name}: missing WHEEL metadata")
            if not any(name.endswith("/METADATA") for name in names):
                errors.append(f"{wheel.name}: missing METADATA")
            if any(name.startswith(("/", "../")) or "/../" in name for name in names):
                errors.append(f"{wheel.name}: unsafe archive path")
            package_rows.append(
                {
                    "name": wheel.name,
                    "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
                    "bytes": wheel.stat().st_size,
                }
            )
    if len(wheels) < 20 or len(sdists) < 20:
        errors.append(
            f"expected at least 20 wheels and sdists, found {len(wheels)} / {len(sdists)}"
        )
    core = next((item for item in wheels if item.name.startswith("hedron_core-")), None)
    if core is None:
        errors.append("hedron-core wheel missing")
    else:
        with zipfile.ZipFile(core) as archive:
            if not any(name.endswith("hedron-default.css") for name in archive.namelist()):
                errors.append("hedron-core wheel missing default CSS asset")
    result = {
        "schema": "hedron.package-evidence/1",
        "wheel_count": len(wheels),
        "sdist_count": len(sdists),
        "packages": package_rows,
        "errors": errors,
        "pass": not errors,
    }
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
