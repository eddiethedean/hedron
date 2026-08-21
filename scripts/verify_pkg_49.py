#!/usr/bin/env python3
"""Verify the phase 0.49 FastAPI/Pydantic convergence packet or in-tree cut.

This command never publishes or tags. Use ``--allow-planned`` only while the 0.49
rows are Planned and the living baseline is 0.48.0.
At the in-tree cut, omit ``--allow-planned`` and require published 0.49.x.
PKG evidence is ``scripts/check_pkg_049.py`` so ``--execute-verified`` cannot recurse here.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_049 import (  # noqa: E402
    API,
    EVALUATE_REQUIREMENT_IDS,
    EXCLUDED_REQUIREMENT_IDS,
    EXPECTED_GATES,
    EXPECTED_REQUIREMENT_RANGES,
    EXPERIMENTAL_REQUIREMENT_IDS,
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    PACKET_FILES,
    PYPROJECT,
    RELEASE,
    ROADMAP,
    STATUS,
    TRACKING_ISSUE,
    accepted_contract_present,
    contract_refine_present,
)

PREDECESSOR = "0.48.0"
RELEASE_CANDIDATE = "0.49.0"


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.49 packet files: {missing}")
    print("ok: 0.49 contract packet files")


def _check_gates(*, allow_planned: bool) -> None:
    rows = _load(GATE).get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
    if found != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected {EXPECTED_GATES}; found {found}")
    if str(_load(GATE).get("planning_baseline", "")).strip() != f"v{PREDECESSOR}":
        raise SystemExit(f"{GATE}: planning_baseline must be v{PREDECESSOR}")
    if str(_load(GATE).get("contract_refine", "")).strip() != "D-084":
        raise SystemExit(f"{GATE}: contract_refine must be D-084")
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
    print("ok: release-gate-0.49.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.49",
        "planning_baseline": f"v{PREDECESSOR}",
        "required_predecessor": f"v{PREDECESSOR}",
        "target": f"v{RELEASE_CANDIDATE}",
        "decision": "D-081",
        "contract_refine": "D-084",
        "owning_rfc": "RFC-0076",
        "lifetime_lock": "docs/acceptance/fastapi-lifetime-049.toml",
        "binding_lock": "docs/acceptance/fastapi-binding-049.toml",
        "typeschema_v2_lock": "docs/acceptance/typeschema-v2-049.toml",
        "unions_openapi_lock": "docs/acceptance/fastapi-unions-openapi-049.toml",
        "settings_research_lock": "docs/acceptance/fastapi-settings-research-049.toml",
        "tracking": TRACKING_ISSUE,
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
    adapter = next(
        (
            row
            for row in capabilities
            if isinstance(row, dict) and row.get("id") == "FP-ADAPTER-001..008"
        ),
        None,
    )
    if adapter is None:
        raise SystemExit(f"{INVENTORY}: FP-ADAPTER-001..008 missing")
    adopt = adapter.get("adopt_if_measured")
    if not isinstance(adopt, list) or "fail-fast-batch" in {str(item) for item in adopt}:
        raise SystemExit(f"{INVENTORY}: FailFast must not appear on FP-ADAPTER adopt_if_measured")
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
        if requirement_id in EVALUATE_REQUIREMENT_IDS:
            if state != "Evaluate":
                bad_states.append(requirement_id)
            continue
        if requirement_id in EXPERIMENTAL_REQUIREMENT_IDS:
            if state != "Experimental":
                bad_states.append(requirement_id)
            continue
        if state != expected_status:
            bad_states.append(requirement_id)
    if bad_states:
        raise SystemExit(f"{INVENTORY}: expected states missing for {bad_states}")
    print("ok: fastapi-pydantic-capability-inventory-049.toml complete requirement coverage")


def _check_contract() -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0076 and D-081 must remain Accepted")
    if not contract_refine_present():
        raise SystemExit("D-084 and the frozen 0.49 contract markers must remain present")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.48", "0.49", "D-081", "D-084"):
            if marker not in text:
                raise SystemExit(f"{path}: missing 0.49 traceability marker {marker}")
    print("ok: RFC-0076 / D-081 / D-084 boundary and traceability")


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
    elif published.startswith(("0.50.", "0.51.", "0.52.", "0.53.", "0.54.", "0.55.", "0.56.")):
        print(f"ok: 0.49 historical under living published {published}")
        return
    else:
        if not published.startswith("0.49."):
            raise SystemExit(f"cut published version must be on 0.49.x; found {published!r}")
        expected = published
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
        print("ok: 0.49 planned gate shape")
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
    print(f"ok: verify_pkg_49 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
