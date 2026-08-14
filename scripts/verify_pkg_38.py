#!/usr/bin/env python3
"""Verify phase 0.38 high-fidelity chart packet and packaging evidence.

This command never publishes or tags. Use ``--allow-planned`` until every 0.38
row is Verified and the workspace is at the ``v0.38.0`` cut.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_038 import (  # noqa: E402
    DECISIONS,
    EXPECTED_GATES,
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    RELEASE_PACKET,
    REVIEW_BRIEF,
    RFC,
    UPGRADE,
    d066_present,
    rfc_is_accepted,
)

RELEASE_CANDIDATE = "0.38.0"
CHARTS_CANDIDATE = "0.2.0"
PYPROJECT = ROOT / "pyproject.toml"
CHARTS_PROJECT = ROOT / "packages" / "hedron-charts" / "pyproject.toml"


def _check_packet_files() -> None:
    required = (
        GATE,
        RELEASE_PACKET,
        IMPLEMENTATION,
        RFC,
        REVIEW_BRIEF,
        UPGRADE,
        INVENTORY,
        DECISIONS,
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"missing Stage 0 artifacts: {missing}")
    print("ok: 0.38 Stage 0 packet files")


def _check_gate_ids() -> None:
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] required")
    found = {str(row.get("id", "")).strip() for row in rows if isinstance(row, dict)}
    missing = sorted(set(EXPECTED_GATES) - found)
    extra = sorted(found - set(EXPECTED_GATES))
    if missing or extra:
        raise SystemExit(f"{GATE}: gate mismatch; missing={missing}, extra={extra}")
    print("ok: release-gate-0.38.toml gate ids")


def _check_inventory(*, allow_planned: bool) -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    required = {
        "phase": "0.38",
        "hedron_cut": "v0.38.0",
        "charts_cut": CHARTS_CANDIDATE,
        "owning_decision": "D-066",
        "owning_rfc": "RFC-0069",
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    expected_state = "planned" if allow_planned else "verified"
    if str(data.get("state", "")).strip() != expected_state:
        raise SystemExit(f"{INVENTORY}: state must be {expected_state!r}")
    element = data.get("element")
    if not isinstance(element, dict) or element.get("tag") != "hedron-chart":
        raise SystemExit(f"{INVENTORY}: [element] tag must be 'hedron-chart'")
    supported = data.get("supported")
    if not isinstance(supported, dict) or "ChartSpec" not in (supported.get("authoring") or []):
        raise SystemExit(f"{INVENTORY}: supported authoring must include ChartSpec")
    print("ok: chart-capability-inventory-038.toml")


def _workspace_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return str(data.get("project", {}).get("version", "")).strip()


def _check_versions(*, allow_planned: bool) -> None:
    version = _workspace_version()
    if allow_planned:
        if not (version.startswith("0.36.") or version.startswith("0.37.")):
            raise SystemExit(
                f"unexpected workspace version {version!r}; "
                "Stage 0/implementation expects 0.36.x or 0.37.x"
            )
        print(f"ok: living tip {version} (0.38 allow-planned)")
        return
    if version != RELEASE_CANDIDATE:
        raise SystemExit(f"cut requires workspace version {RELEASE_CANDIDATE}; found {version!r}")
    charts = tomllib.loads(CHARTS_PROJECT.read_text(encoding="utf-8"))
    charts_version = str(charts.get("project", {}).get("version", "")).strip()
    if charts_version != CHARTS_CANDIDATE:
        raise SystemExit(f"cut requires hedron-charts {CHARTS_CANDIDATE}; found {charts_version!r}")
    print(f"ok: cut versions Hedron {version} / hedron-charts {charts_version}")


def _check_review(*, allow_planned: bool) -> None:
    if allow_planned:
        print("ok: security-review-038 BRIEF (allow-planned)")
        return
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = REVIEW_BRIEF.parent / name
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path}")
    print("ok: security-review-038 full packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args(argv)

    _check_packet_files()
    _check_gate_ids()
    _check_inventory(allow_planned=args.allow_planned)
    if not rfc_is_accepted():
        raise SystemExit("RFC-0069 must be Accepted")
    if not d066_present():
        raise SystemExit("D-066 must be Accepted in DECISIONS.md")
    print("ok: RFC-0069 Accepted + D-066")
    _check_versions(allow_planned=args.allow_planned)
    _check_review(allow_planned=args.allow_planned)

    import check_release_gate as gate

    if args.allow_planned:
        errors = gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.38.toml (planned shape)")
    else:
        command = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            RELEASE_CANDIDATE,
            "--evidence-manifest",
            str(GATE),
            "--execute-verified",
        ]
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print(f"ok: verify_pkg_38 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
