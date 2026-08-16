#!/usr/bin/env python3
"""Verify the phase 0.43 refreshable-view planning packet or release cut.

This command never publishes or tags. Use ``--allow-planned`` only while the 0.43
rows are Planned/Implemented and the published/development baseline is 0.42.0.
At the in-tree cut, omit ``--allow-planned`` and require published 0.43.0.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_043 import (  # noqa: E402
    API,
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
    cross_phase_refinement_present,
)

RELEASE_CANDIDATE = "0.43.0"


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.43 packet files: {missing}")
    print("ok: 0.43 contract packet files")


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
    print("ok: release-gate-0.43.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.43",
        "baseline": "v0.42.0",
        "target": "v0.43.0",
        "decision": "D-071",
        "cross_phase_refinement": "D-073",
        "owning_rfc": "RFC-0070",
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
    unknown_gates = sorted(
        {
            str(row.get("gate", "")).strip()
            for row in capabilities
            if isinstance(row, dict) and str(row.get("gate", "")).strip() not in EXPECTED_GATES
        }
    )
    if unknown_gates:
        raise SystemExit(f"{INVENTORY}: unknown capability gates {unknown_gates}")
    expected_status = "Planned" if allow_planned else "Verified"
    if str(data.get("status", "")).strip() != expected_status:
        raise SystemExit(f"{INVENTORY}: status must be {expected_status!r}")
    bad_states = [
        str(row.get("id"))
        for row in capabilities
        if isinstance(row, dict) and str(row.get("state", "")).strip() != expected_status
    ]
    if bad_states:
        raise SystemExit(f"{INVENTORY}: {expected_status} state required for {bad_states}")
    print("ok: interaction-capability-inventory-043.toml complete requirement coverage")


def _check_contract() -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0070 and D-071 must remain Accepted")
    if not cross_phase_refinement_present():
        raise SystemExit("D-073 and the frozen 0.43/0.44 boundary must remain present")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.42", "0.43", "D-071"):
            if marker not in text:
                raise SystemExit(f"{path}: missing 0.43 traceability marker {marker}")
    print("ok: RFC-0070 / D-071 / D-073 boundary and traceability")


def _check_versions(*, allow_planned: bool) -> None:
    workspace = str(_load(PYPROJECT).get("project", {}).get("version", "")).strip()
    release = _load(RELEASE).get("release", {})
    if not isinstance(release, dict):
        raise SystemExit(f"{RELEASE}: [release] table required")
    published = str(release.get("published_version", "")).strip()
    development = str(release.get("development_version", "")).strip()
    if allow_planned:
        if published != "0.42.0":
            raise SystemExit(f"published baseline must remain 0.42.0; found {published!r}")
        expected = "0.42.0"
    else:
        if published != RELEASE_CANDIDATE:
            raise SystemExit(f"cut published version must be {RELEASE_CANDIDATE}; found {published!r}")
        expected = RELEASE_CANDIDATE
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
        print("ok: 0.43 planned gate shape")
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
    print(f"ok: verify_pkg_43 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
