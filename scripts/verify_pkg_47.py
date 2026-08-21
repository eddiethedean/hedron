#!/usr/bin/env python3
"""Verify the phase 0.47 first-class maps planning packet or release cut.

This command never publishes or tags. Use ``--allow-planned`` only while the 0.47
rows are Planned and the published/development baseline is 0.46.0.
At the in-tree cut, omit ``--allow-planned`` and require published 0.47.0.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_047 import (  # noqa: E402
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

PREDECESSOR = "0.46.0"
RELEASE_CANDIDATE = "0.47.0"


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.47 packet files: {missing}")
    print("ok: 0.47 contract packet files")


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
        non_verified = [
            f"{row.get('id')}={row.get('state')}"
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Verified"
        ]
        if non_verified:
            raise SystemExit(f"cut requires Verified gates: {non_verified}")
    print("ok: release-gate-0.47.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.47",
        "planning_baseline": "v0.46.0",
        "required_predecessor": "v0.46.0",
        "target": "v0.47.0",
        "decision": "D-078",
        "contract_refine": "D-082",
        "owning_rfc": "RFC-0074",
        "map_spec_plan": "docs/acceptance/map-spec-plan-047.toml",
        "map_provider_policy": "docs/acceptance/map-provider-policy-047.toml",
        "map_offline": "docs/acceptance/map-offline-047.toml",
        "map_interaction_compat": "docs/acceptance/map-interaction-compat-047.toml",
        "form_inventory": "docs/acceptance/type-form-inventory-044.toml",
        "catalog_entry": "docs/acceptance/catalog-entry-045.toml",
        "host_portable_facts": "docs/acceptance/host-portable-facts-045.toml",
        "adapter_dispositions": "docs/acceptance/adapter-disposition-044.toml",
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
    bad_states: list[str] = []
    for row in capabilities:
        if not isinstance(row, dict):
            continue
        requirement_id = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        if requirement_id in EXCLUDED_REQUIREMENT_IDS:
            if state != "Excluded":
                bad_states.append(requirement_id)
            continue
        if state != expected_status:
            bad_states.append(requirement_id)
    if bad_states:
        raise SystemExit(f"{INVENTORY}: {expected_status} state required for {bad_states}")
    print("ok: map-capability-inventory-047.toml complete requirement coverage")


def _check_contract() -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0074 and D-078 must remain Accepted")
    if not contract_refine_present():
        raise SystemExit("D-082 and the frozen 0.47 contract markers must remain present")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.46", "0.47", "D-078", "D-082"):
            if marker not in text:
                raise SystemExit(f"{path}: missing 0.47 traceability marker {marker}")
    print("ok: RFC-0074 / D-078 / D-082 boundary and traceability")


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
    elif published.startswith(("0.48.", "0.49.", "0.50.", "0.51.", "0.52.", "0.53.", "0.54.", "0.55.")):
        print(f"ok: 0.47 historical under living published {published}")
        return
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
        print("ok: 0.47 planned gate shape")
    elif str(_load(PYPROJECT).get("project", {}).get("version", "")).startswith(
        ("0.48.", "0.49.", "0.50.", "0.51.", "0.52.", "0.53.", "0.54.", "0.55.")
    ):
        errors = release_gate.check_evidence_manifest(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: 0.47 verified historical packet")
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
    print(f"ok: verify_pkg_47 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
