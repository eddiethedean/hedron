#!/usr/bin/env python3
"""Assemble the release evidence bundle under dist/evidence-bundle/ (SUPPLY-025)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "evidence-bundle"
# Living train evidence index after the 0.25 cut (SUPPLY-025 attach on train tags).
PHASE = "0.25"
GATE_MANIFEST = "docs/acceptance/release-gate-0.25.toml"


def run(script: str) -> None:
    subprocess.check_call([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    run("generate_sbom.py")
    run("license_inventory.py")
    run("asset_audit.py")
    run("check_stability_inventory.py")

    lock = ROOT / "uv.lock"
    digest = hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else ""
    manifest = {
        "phase": PHASE,
        "generated_at": datetime.now(UTC).isoformat(),
        "uv_lock_sha256": digest,
        "artifacts": sorted(p.name for p in OUT.iterdir() if p.is_file()),
        "gate_manifest": GATE_MANIFEST,
    }
    (OUT / "bundle-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"ok: evidence bundle at {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
