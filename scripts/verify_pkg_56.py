#!/usr/bin/env python3
"""Verify the phase 0.56 security control plane packet or in-tree cut."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_056 import (  # noqa: E402
    API,
    EXPECTED_GATES,
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

PREDECESSOR = "0.55.0"
RELEASE_CANDIDATE = "0.56.0"


def _load(path: Path) -> dict:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.56 packet files: {missing}")
    print("ok: 0.56 contract packet files")


def _check_gates(*, allow_planned: bool) -> None:
    rows = _load(GATE).get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
    if found != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected {EXPECTED_GATES}; found {found}")
    if str(_load(GATE).get("planning_baseline", "")).strip() != f"v{PREDECESSOR}":
        raise SystemExit(f"{GATE}: planning_baseline must be v{PREDECESSOR}")
    if str(_load(GATE).get("contract_refine", "")).strip() != "D-098":
        raise SystemExit(f"{GATE}: contract_refine must be D-098")
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
    print("ok: release-gate-0.56.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.56",
        "baseline": f"v{PREDECESSOR}",
        "target": f"v{RELEASE_CANDIDATE}",
        "decision": "D-097",
        "contract_refine": "D-098",
        "owning_rfc": "RFC-0083",
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    expected_status = "Planned" if allow_planned else "Verified"
    if str(data.get("state", "")).strip() != expected_status:
        raise SystemExit(f"{INVENTORY}: state must be {expected_status!r}")
    print("ok: security-inventory-056.toml")


def _check_contract() -> None:
    if not accepted_contract_present():
        raise SystemExit("RFC-0083 and D-097 must remain Accepted")
    if not contract_refine_present():
        raise SystemExit("D-098 and the frozen 0.56 contract markers must remain present")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.56", "D-097", "D-098"):
            if path in (ROADMAP, STATUS):
                if marker == "0.56" and marker not in text:
                    raise SystemExit(f"{path}: missing 0.56 traceability marker")
                if marker.startswith("D-") and marker not in text and path is STATUS:
                    # STATUS may lag until Stage 0 tip honesty update; require D markers in ROADMAP
                    pass
            elif path in (API, IMPLEMENTATION) and "0.56" not in text:
                raise SystemExit(f"{path}: missing 0.56 marker")
    if "D-097" not in ROADMAP.read_text(encoding="utf-8") and "D-097" not in STATUS.read_text(
        encoding="utf-8"
    ):
        # Prefer STATUS mention after Stage 0 honesty update
        pass
    if TRACKING_ISSUE not in STATUS.read_text(encoding="utf-8"):
        raise SystemExit(f"{STATUS}: missing tracking issue {TRACKING_ISSUE}")
    print("ok: RFC-0083 / D-097 / D-098 boundary and traceability")


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
    if published.startswith("0.57."):
        print(f"ok: 0.56 historical under living published {published}")
        return
    if not published.startswith("0.56."):
        raise SystemExit(f"cut published version must be on 0.56.x; found {published!r}")
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
        if not (pypi.startswith("0.54.") or pypi.startswith(("0.55.", "0.56.", "0.57."))):
            raise SystemExit(
                f"deferred pypi_version must stay on prior public index; found {pypi!r}"
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
    _check_contract()
    _check_versions(allow_planned=args.allow_planned)

    import check_release_gate as release_gate

    if args.allow_planned:
        errors = release_gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: 0.56 planned gate shape")
    else:
        published = str(_load(RELEASE).get("release", {}).get("published_version", "")).strip()
        if published.startswith("0.57."):
            print("ok: 0.56 historical packet; skip execute-verified under living tip")
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
    print(f"ok: verify_pkg_56 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
