#!/usr/bin/env python3
"""Verify the phase 0.48 HTMX extension integration packet or in-tree cut.

This command never publishes or tags. Use ``--allow-planned`` only while the 0.48
rows are Planned and the living baseline is 0.47.0.
At the in-tree cut, omit ``--allow-planned`` and require published 0.48.0.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_048 import (  # noqa: E402
    API,
    EXCLUDED_REQUIREMENT_IDS,
    EXPECTED_GATES,
    EXPECTED_REQUIREMENT_RANGES,
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    PACKET_FILES,
    PYPROJECT,
    RELEASE,
    ROADMAP,
    STATUS,
    accepted_contract_present,
    contract_refine_present,
)

PREDECESSOR = "0.47.0"
RELEASE_CANDIDATE = "0.48.0"


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.48 packet files: {missing}")
    print("ok: 0.48 contract packet files")


def _check_gates(*, allow_planned: bool) -> None:
    rows = _load(GATE).get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
    if found != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected {EXPECTED_GATES}; found {found}")
    if allow_planned:
        non_planned = [
            f"{row.get('id')}={row.get('state')}"
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Planned"
        ]
        if non_planned:
            raise SystemExit(f"Stage 0 requires Planned gates: {non_planned}")
    else:
        closing = {"Verified", "Deferred", "Excluded"}
        for row in rows:
            if not isinstance(row, dict):
                continue
            gate_id = str(row.get("id", "")).strip()
            state = str(row.get("state", "")).strip()
            if gate_id == "MORPH-048":
                if state not in closing:
                    raise SystemExit(f"MORPH-048 must be Verified or Deferred; found {state}")
                continue
            if state != "Verified":
                raise SystemExit(f"cut requires Verified {gate_id}; found {state}")
    print("ok: release-gate-0.48.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.48",
        "planning_baseline": "v0.47.0",
        "required_predecessor": "v0.47.0",
        "target": "v0.48.0",
        "decision": "D-080",
        "contract_refine": "D-083",
        "owning_rfc": "RFC-0075",
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    capabilities = data.get("capability")
    if not isinstance(capabilities, list):
        raise SystemExit(f"{INVENTORY}: [[capability]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in capabilities if isinstance(row, dict))
    if found != EXPECTED_REQUIREMENT_RANGES:
        raise SystemExit(
            f"{INVENTORY}: requirement coverage drift; expected "
            f"{EXPECTED_REQUIREMENT_RANGES}; found {found}"
        )
    expected_status = "Planned" if allow_planned else None
    bad_states: list[str] = []
    for row in capabilities:
        if not isinstance(row, dict):
            continue
        requirement_id = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        if requirement_id in EXCLUDED_REQUIREMENT_IDS:
            if state not in {"Excluded", "Deferred", "Planned", "Verified"}:
                bad_states.append(requirement_id)
            continue
        if expected_status is None:
            if state != "Verified":
                bad_states.append(requirement_id)
            continue
        if state != expected_status:
            bad_states.append(requirement_id)
    if bad_states:
        raise SystemExit(f"{INVENTORY}: status mismatch for {bad_states}")
    print("ok: htmx-capability-inventory-048.toml complete requirement coverage")


def _check_contract() -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0075 and D-080 must remain Accepted")
    if not contract_refine_present():
        raise SystemExit("D-083 and the frozen 0.48 contract markers must remain present")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.47", "0.48", "D-080", "D-083"):
            if marker not in text:
                raise SystemExit(f"{path}: missing 0.48 traceability marker {marker}")
    print("ok: RFC-0075 / D-080 / D-083 boundary and traceability")


def _check_versions(*, allow_planned: bool) -> None:
    workspace = str(_load(PYPROJECT).get("project", {}).get("version", "")).strip()
    release = _load(RELEASE).get("release", {})
    if not isinstance(release, dict):
        raise SystemExit(f"{RELEASE}: [release] table required")
    published = str(release.get("published_version", "")).strip()
    development = str(release.get("development_version", "")).strip()
    if allow_planned:
        expected = PREDECESSOR
        if published != PREDECESSOR:
            raise SystemExit(f"published baseline must remain {PREDECESSOR}; found {published!r}")
    else:
        expected = RELEASE_CANDIDATE
        if published != RELEASE_CANDIDATE:
            raise SystemExit(
                f"cut published version must be {RELEASE_CANDIDATE}; found {published!r}"
            )
    if workspace != expected or development != expected:
        raise SystemExit(
            f"workspace/development version must be {expected}; found {workspace}/{development}"
        )
    print(f"ok: version honesty (published {published}, development {development})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args(argv)
    _check_packet_files()
    _check_gates(allow_planned=args.allow_planned)
    _check_inventory(allow_planned=args.allow_planned)
    _check_contract()
    _check_versions(allow_planned=args.allow_planned)

    import check_release_gate as release_gate

    if args.allow_planned:
        errors = release_gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: 0.48 planned gate shape")
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
        morph = [
            sys.executable,
            str(ROOT / "scripts" / "check_morph_048.py"),
        ]
        print("+", *morph)
        subprocess.check_call(morph, cwd=ROOT)
    print(f"ok: verify_pkg_48 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
