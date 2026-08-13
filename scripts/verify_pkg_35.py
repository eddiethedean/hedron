#!/usr/bin/env python3
"""Verify phase 0.35 packaging / packet evidence for whole-fleet closure.

Does **not** publish or tag.

* ``--allow-planned``: validate the 0.35 evidence manifest shape while rows may
  still be Planned and the living tip remains on ``0.34.x`` (packet refine).
* Omit ``--allow-planned`` at ``v0.35.0`` cut once every evidence row is
  ``Verified``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "acceptance" / "release-gate-0.35.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-035.toml"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-035" / "BRIEF.md"
RELEASE_CANDIDATE = "0.35.0"
EXPECTED_PACKAGES = (
    "hedron",
    "hedron-core",
    "hedron-explorer",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-extras",
    "hedron-conformance",
    "hedron-charts",
    "hedron-native",
    "hedron-sample-kit",
    "hedron-sim",
    "hedron-notebook",
    "hedron-mcp",
    "hedron-gradio",
    "hedron-workbench",
    "hedron-posit",
    "fastapi-workbench",
    "hedron-runtime-node",
    "hedron-runtime-java",
)


def _check_inventory() -> None:
    if not INVENTORY.is_file():
        raise SystemExit(f"missing inventory: {INVENTORY}")
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, list):
        raise SystemExit(f"{INVENTORY}: packages list required")
    missing = [name for name in EXPECTED_PACKAGES if name not in packages]
    if missing:
        raise SystemExit(f"{INVENTORY}: missing packages {missing}")
    if str(data.get("baseline", "")).strip() != "v0.34.0":
        raise SystemExit(f"{INVENTORY}: baseline must be v0.34.0")
    print("ok: production-grade-inventory-035.toml")


def _check_review_packet(*, allow_planned: bool) -> None:
    if not REVIEW_BRIEF.is_file():
        raise SystemExit(f"missing review brief: {REVIEW_BRIEF}")
    if allow_planned:
        print("ok: security-review-035 BRIEF (allow-planned)")
        return
    packet = REVIEW_BRIEF.parent
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = packet / name
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path}")
    print("ok: security-review-035 full packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help=(f"Allow Planned rows (pre-cut / packet refine). Omit at v{RELEASE_CANDIDATE} cut."),
    )
    args = parser.parse_args(argv)

    _check_inventory()
    _check_review_packet(allow_planned=args.allow_planned)

    if args.allow_planned:
        sys.path.insert(0, str(ROOT / "scripts"))
        import check_release_gate as gate

        errors = gate.check_evidence_manifest_lenient(EVIDENCE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.35.toml (planned shape)")
    else:
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            RELEASE_CANDIDATE,
            "--evidence-manifest",
            str(EVIDENCE),
            "--execute-verified",
        ]
        print("+", *gate_cmd)
        subprocess.check_call(gate_cmd, cwd=ROOT)
    print(f"ok: verify_pkg_35 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
