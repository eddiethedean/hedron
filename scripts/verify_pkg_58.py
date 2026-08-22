#!/usr/bin/env python3
"""Verify the phase 0.58 progressive feature and styling packet or in-tree cut."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_058 import (  # noqa: E402
    EXPECTED_GATES,
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    PACKET_FILES,
    PLANNING_BASELINE,
    PREDECESSOR,
    PYPROJECT,
    RELEASE,
    RELEASE_CANDIDATE,
    ROADMAP,
    STATUS,
    STYLING_INVENTORY,
    WHATS_NEW,
    accepted_contract_present,
    contract_refine_present,
)


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.58 packet files: {missing}")
    print("ok: 0.58 contract packet files")


def _check_gates(*, allow_planned: bool) -> None:
    data = _load(GATE)
    rows = data.get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
    if found != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected {EXPECTED_GATES}; found {found}")
    if str(data.get("planning_baseline", "")).strip() != PLANNING_BASELINE:
        raise SystemExit(f"{GATE}: planning_baseline must be {PLANNING_BASELINE}")
    refines = data.get("contract_refines")
    if not isinstance(refines, list) or set(refines) != {"D-102", "D-105"}:
        raise SystemExit(f"{GATE}: contract_refines must be [D-102, D-105]")
    if allow_planned:
        non_planned = [
            f"{row.get('id')}={row.get('state')}"
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Planned"
        ]
        if non_planned:
            raise SystemExit(f"Stage 0 requires Planned gates: {non_planned}")
    else:
        non_verified = [
            f"{row.get('id')}={row.get('state')}"
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Verified"
        ]
        if non_verified:
            raise SystemExit(f"cut requires Verified gates: {non_verified}")
        if str(data.get("status", "")).strip() != "Verified":
            raise SystemExit(f"{GATE}: top-level status must be Verified at cut")
    print("ok: release-gate-0.58.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.58",
        "baseline": f"v{PREDECESSOR}",
        "target": f"v{RELEASE_CANDIDATE}",
        "decision": "D-101",
        "contract_refine": "D-102",
        "owning_rfc": "RFC-0085",
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    expected_status = "planned" if allow_planned else "verified"
    if str(data.get("state", "")).strip().lower() != expected_status:
        raise SystemExit(f"{INVENTORY}: state must be {expected_status!r}")
    styling = _load(STYLING_INVENTORY)
    if str(styling.get("phase", "")).strip() != "0.58":
        raise SystemExit(f"{STYLING_INVENTORY}: phase must be 0.58")
    if str(styling.get("state", "")).strip().lower() != expected_status:
        raise SystemExit(f"{STYLING_INVENTORY}: state must be {expected_status!r}")
    print("ok: progressive/styling authoring inventories")


def _check_contract(*, allow_planned: bool) -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0085 and D-101 must remain Accepted")
    if not contract_refine_present():
        raise SystemExit("D-102 / D-105 and the frozen 0.58 contract markers must remain present")
    if allow_planned:
        print("ok: RFC-0085 / D-101 / D-102 / D-105 Stage 0 contract")
        return
    for path in (ROADMAP, STATUS, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        if "0.58" not in text:
            raise SystemExit(f"{path}: missing 0.58 traceability marker")
    if not WHATS_NEW.is_file():
        raise SystemExit(f"missing {WHATS_NEW}")
    print("ok: RFC-0085 / D-101 / D-102 / D-105 boundary and traceability")


def _check_versions(*, allow_planned: bool) -> None:
    workspace = str(_load(PYPROJECT).get("project", {}).get("version", "")).strip()
    release = _load(RELEASE).get("release", {})
    if not isinstance(release, dict):
        raise SystemExit(f"{RELEASE}: [release] table required")
    published = str(release.get("published_version", "")).strip()
    development = str(release.get("development_version", "")).strip()
    pypi = str(release.get("pypi_version", "")).strip()
    status = str(release.get("registry_status", "")).strip()
    if allow_planned:
        if not published.startswith("0.57."):
            raise SystemExit(f"published baseline must remain on 0.57.x; found {published!r}")
        return
    if not published.startswith("0.58."):
        raise SystemExit(f"cut published version must be on 0.58.x; found {published!r}")
    if workspace != published or development != published:
        raise SystemExit(
            f"workspace/development must match published {published}; "
            f"found {workspace}/{development}"
        )
    if status == "uploaded":
        if pypi != published:
            raise SystemExit(
                f"pypi_version must match published {published} after upload; found {pypi!r}"
            )
    elif status == "deferred":
        if pypi == published:
            raise SystemExit("deferred cut requires pypi_version != published_version until upload")
        if not (
            pypi.startswith("0.56.")
            or pypi.startswith("0.57.")
            or (pypi.startswith("0.58.") and pypi != published)
        ):
            raise SystemExit(
                f"deferred pypi_version must stay on an earlier public cut; found {pypi!r}"
            )
    else:
        raise SystemExit(f"registry_status must be uploaded or deferred; found {status!r}")
    print(f"ok: version honesty (published {published}, pypi {pypi}, {status})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args(argv)
    _check_packet_files()
    _check_gates(allow_planned=args.allow_planned)
    _check_inventory(allow_planned=args.allow_planned)
    _check_contract(allow_planned=args.allow_planned)
    _check_versions(allow_planned=args.allow_planned)

    import check_release_gate as release_gate

    if args.allow_planned:
        errors = release_gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: 0.58 planned gate shape")
    else:
        published = str(_load(RELEASE).get("release", {}).get("published_version", "")).strip()
        command = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            published,
            "--evidence-manifest",
            str(GATE),
            "--execute-verified",
        ]
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print(f"ok: verify_pkg_58 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
