#!/usr/bin/env python3
"""Assemble the release evidence bundle under dist/evidence-bundle/ (SUPPLY-025)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "evidence-bundle"
RELEASE_METADATA = ROOT / "docs" / "release.toml"


def run(script: str) -> None:
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="Release version represented by this bundle")
    args = parser.parse_args()
    release = tomllib.loads(RELEASE_METADATA.read_text(encoding="utf-8"))["release"]
    version = args.version or release["development_version"]
    phase = ".".join(version.split(".")[:2])
    configured_phases = {
        str(release["train"]),
        ".".join(str(release["development_version"]).split(".")[:2]),
    }
    if phase not in configured_phases:
        raise SystemExit(
            f"evidence version {version} is outside configured trains "
            f"{', '.join(sorted(configured_phases))}"
        )
    gate_manifest = f"docs/acceptance/release-gate-{phase}.toml"
    if not (ROOT / gate_manifest).is_file():
        raise SystemExit(f"missing gate manifest: {gate_manifest}")

    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.iterdir():
        if path.is_file():
            path.unlink()
        else:
            raise SystemExit(f"unexpected directory in evidence output: {path}")
    run("generate_sbom.py")
    run("license_inventory.py")
    run("asset_audit.py")
    run("check_stability_inventory.py")

    lock = ROOT / "uv.lock"
    digest = hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else ""
    manifest = {
        "release_version": version,
        "phase": phase,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "uv_lock_sha256": digest,
        "artifacts": sorted(p.name for p in OUT.iterdir() if p.is_file()),
        "gate_manifest": gate_manifest,
    }
    (OUT / "bundle-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"ok: evidence bundle at {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
