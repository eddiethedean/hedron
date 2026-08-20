#!/usr/bin/env python3
"""Verify the phase 0.52 conformance/Posit packet or in-tree cut."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_052 import (  # noqa: E402
    API,
    EXPECTED_GATES,
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    PACKET_FILES,
    POSIT_API,
    POSIT_IMPLEMENTATION,
    PYPROJECT,
    RELEASE,
    RFC,
    ROADMAP,
    STATUS,
    TRACKING_ISSUE,
    accepted_contract_present,
    contract_refine_present,
)

PREDECESSOR = "0.51.2"
RELEASE_CANDIDATE = "0.52.0"


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.52 packet files: {missing}")
    print("ok: 0.52 contract packet files")


def _check_gates(*, allow_planned: bool) -> None:
    rows = _load(GATE).get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
    if found != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected {EXPECTED_GATES}; found {found}")
    if str(_load(GATE).get("planning_baseline", "")).strip() != f"v{PREDECESSOR}":
        raise SystemExit(f"{GATE}: planning_baseline must be v{PREDECESSOR}")
    if str(_load(GATE).get("contract_refine", "")).strip() != "D-090":
        raise SystemExit(f"{GATE}: contract_refine must be D-090")
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
    print("ok: release-gate-0.52.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.52",
        "planning_baseline": f"v{PREDECESSOR}",
        "required_predecessor": f"v{PREDECESSOR}",
        "target": f"v{RELEASE_CANDIDATE}",
        "decision": "D-089",
        "contract_refine": "D-090",
        "owning_rfc": "RFC-0079",
        "tracking": TRACKING_ISSUE,
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    expected_status = "Planned" if allow_planned else "Verified"
    if str(data.get("status", "")).strip() != expected_status:
        raise SystemExit(f"{INVENTORY}: status must be {expected_status!r}")
    print("ok: conformance-capability-inventory-052.toml")


def _check_contract() -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0079 and D-089 must remain Accepted")
    if not contract_refine_present():
        raise SystemExit("D-090 and the frozen 0.52 contract markers must remain present")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION, POSIT_API, POSIT_IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.52", "D-089", "D-090"):
            if marker not in text and path in (ROADMAP, STATUS):
                if marker not in text:
                    raise SystemExit(f"{path}: missing 0.52 traceability marker {marker}")
            elif path in (API, IMPLEMENTATION, POSIT_API, POSIT_IMPLEMENTATION) and "0.52" not in text:
                raise SystemExit(f"{path}: missing 0.52 marker")
    print("ok: RFC-0079 / D-089 / D-090 boundary and traceability")


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
        if published != PREDECESSOR:
            raise SystemExit(f"published baseline must remain {PREDECESSOR}; found {published!r}")
        return
    if published.startswith("0.53.") or published.startswith("0.54."):
        print(f"ok: 0.52 historical under living published {published}")
        return
    if not published.startswith("0.52."):
        raise SystemExit(f"cut published version must be on 0.52.x; found {published!r}")
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
            raise SystemExit(
                "deferred cut requires pypi_version != published_version until upload"
            )
        if not (pypi.startswith("0.51.") or pypi.startswith("0.52.")):
            raise SystemExit(f"deferred pypi_version must stay on 0.51.x or 0.52.x; found {pypi!r}")
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
    _check_contract()
    _check_versions(allow_planned=args.allow_planned)

    import check_release_gate as release_gate

    if args.allow_planned:
        errors = release_gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: 0.52 planned gate shape")
    else:
        published = str(_load(RELEASE).get("release", {}).get("published_version", "")).strip()
        if published.startswith("0.53.") or published.startswith("0.54."):
            print("ok: 0.52 historical packet; skip execute-verified under living tip")
        else:
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
    print(f"ok: verify_pkg_52 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
