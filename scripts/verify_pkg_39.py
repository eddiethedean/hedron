#!/usr/bin/env python3
"""Verify phase 0.39 rich-surface / OptimisticMutation packet and packaging evidence.

This command never publishes or tags. Use ``--allow-planned`` until every 0.39
row is Verified and the workspace is at the ``v0.39.0`` cut.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_039 import (  # noqa: E402
    AT_DISPOSITION,
    AT_PROTOCOL,
    EXPECTED_GATES,
    FLEET_INVENTORY,
    GATE,
    INVENTORY,
    PACKET_FILES,
    REVIEW_BRIEF,
    RICH_SURFACE,
    d067_present,
    missing_refine_citations,
    rfc_is_accepted,
    rfc_resolved_questions_present,
)

RELEASE_CANDIDATE = "0.39.0"
PYPROJECT = ROOT / "pyproject.toml"
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
    "hedron-elements",
    "fastapi-workbench",
    "hedron-runtime-node",
    "hedron-runtime-java",
)


def _check_packet_files() -> None:
    missing = [str(path) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing Stage 0 artifacts: {missing}")
    print("ok: 0.39 Stage 0 packet files")


def _check_refine_citations() -> None:
    errors = missing_refine_citations()
    if errors:
        raise SystemExit("\n".join(errors))
    print("ok: 0.39 tracking #94 and medium-issue citations")


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
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("state", "")).strip() not in {"Planned", "Implemented", "Verified"}:
            raise SystemExit(f"{GATE}: unexpected state for {row.get('id')}")
    print("ok: release-gate-0.39.toml gate ids")


def _check_inventory(*, allow_planned: bool) -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    required = {
        "phase": "0.39",
        "hedron_cut": "v0.39.0",
        "owning_decision": "D-067",
        "owning_rfc": "RFC-0060",
        "living_published_baseline": "v0.38.0",
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    expected_state = "planned" if allow_planned else "verified"
    state = str(data.get("state", "")).strip()
    if allow_planned:
        if state not in {"planned", "verified"}:
            raise SystemExit(f"{INVENTORY}: state must be planned or verified (post-cut)")
    elif state != expected_state:
        raise SystemExit(f"{INVENTORY}: state must be {expected_state!r}")
    optimistic = data.get("optimistic")
    if not isinstance(optimistic, dict):
        raise SystemExit(f"{INVENTORY}: [optimistic] required")
    first = optimistic.get("first_inventory") or []
    if "DataEditor" not in first:
        raise SystemExit(f"{INVENTORY}: optimistic.first_inventory must include DataEditor")
    chartlink = data.get("chartlink")
    if not isinstance(chartlink, dict) or chartlink.get("parallel_renderer") is not False:
        raise SystemExit(f"{INVENTORY}: chartlink.parallel_renderer must be false")
    print("ok: rich-surface-inventory-039.toml")


def _check_fleet_inventory() -> None:
    data = tomllib.loads(FLEET_INVENTORY.read_text(encoding="utf-8"))
    if str(data.get("baseline", "")).strip() != "v0.38.0":
        raise SystemExit(f"{FLEET_INVENTORY}: baseline must be v0.38.0")
    if str(data.get("state", "")).strip() not in {"planned", "verified"}:
        raise SystemExit(f"{FLEET_INVENTORY}: state must be planned or verified")
    packages = data.get("packages")
    if not isinstance(packages, list):
        raise SystemExit(f"{FLEET_INVENTORY}: packages list required")
    missing = [name for name in EXPECTED_PACKAGES if name not in packages]
    if missing:
        raise SystemExit(f"{FLEET_INVENTORY}: missing packages {missing}")
    charts = data.get("hedron-charts")
    if not isinstance(charts, dict):
        raise SystemExit(f"{FLEET_INVENTORY}: hedron-charts table required")
    supported = charts.get("supported") or []
    for item in ("matplotlib_static", "chart_spec", "hedron_chart"):
        if item not in supported:
            raise SystemExit(f"{FLEET_INVENTORY}: hedron-charts.supported must include {item}")
    elements = data.get("hedron-elements")
    if not isinstance(elements, dict):
        raise SystemExit(f"{FLEET_INVENTORY}: hedron-elements table required")
    if str(elements.get("disposition", "")).strip() != "incubator":
        raise SystemExit(f"{FLEET_INVENTORY}: hedron-elements disposition must be incubator")
    data_pkg = data.get("hedron-data")
    if not isinstance(data_pkg, dict):
        raise SystemExit(f"{FLEET_INVENTORY}: hedron-data table required")
    print("ok: production-grade-inventory-039.toml")


def _workspace_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return str(data.get("project", {}).get("version", "")).strip()


def _check_versions(*, allow_planned: bool) -> None:
    version = _workspace_version()
    if allow_planned:
        if not (
            version.startswith("0.38.")
            or version.startswith("0.39.")
            or version.startswith("0.40.")
            or version.startswith("0.41.")
            or version.startswith("0.42.")
            or version.startswith("0.43.")
            or version.startswith("0.44.")
            or version.startswith("0.45.")
            or version.startswith("0.46.")
        ):
            raise SystemExit(
                f"unexpected workspace version {version!r}; Stage 0/implementation expects 0.38.x–0.45.x"
            )
        print(f"ok: living tip {version} (0.39 allow-planned)")
        return
    if version != RELEASE_CANDIDATE and not version.startswith(("0.40.", "0.41.", "0.42.", "0.43.", "0.44.", "0.45.", "0.46.")):
        raise SystemExit(f"cut requires workspace version {RELEASE_CANDIDATE}; found {version!r}")
    if version.startswith(("0.40.", "0.41.", "0.42.", "0.43.", "0.44.", "0.45.", "0.46.")):
        # Post-0.39 tip: packet already Verified; skip workspace pin equality.
        print(f"ok: post-cut living tip {version} (0.39 packet verified)")
        return
    print(f"ok: cut version Hedron {version}")


def _check_review(*, allow_planned: bool) -> None:
    if allow_planned:
        print("ok: security-review-039 BRIEF (allow-planned)")
        return
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = REVIEW_BRIEF.parent / name
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path}")
    print("ok: security-review-039 full packet")


def _check_at_skeleton(*, allow_planned: bool) -> None:
    protocol = AT_PROTOCOL.read_text(encoding="utf-8")
    if "does not claim Supported human AT" not in protocol:
        raise SystemExit(f"{AT_PROTOCOL}: must disclaim Supported human AT")
    data = tomllib.loads(AT_DISPOSITION.read_text(encoding="utf-8"))
    if str(data.get("gate", "")).strip() != "A11Y-039":
        raise SystemExit(f"{AT_DISPOSITION}: gate must be A11Y-039")
    expected = "planned" if allow_planned else "verified"
    state = str(data.get("state", "")).strip()
    if allow_planned:
        if state not in {"planned", "verified"}:
            raise SystemExit(f"{AT_DISPOSITION}: state must be planned or verified")
    elif state != expected:
        raise SystemExit(f"{AT_DISPOSITION}: state must be {expected}")
    print("ok: human-at/039 scoped skeleton")


def _check_rich_surface_catalog() -> None:
    text = RICH_SURFACE.read_text(encoding="utf-8")
    for marker in (
        "OptimisticMutation first inventory",
        "Experimental exception policy",
        "Chart link",
        "Worker / remote bounds",
    ):
        if marker not in text:
            raise SystemExit(f"{RICH_SURFACE}: missing section {marker!r}")
    print("ok: RICH_SURFACE_039.md catalogs")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args(argv)

    _check_packet_files()
    _check_refine_citations()
    _check_gate_ids()
    _check_inventory(allow_planned=args.allow_planned)
    _check_fleet_inventory()
    _check_rich_surface_catalog()
    _check_at_skeleton(allow_planned=args.allow_planned)
    if not rfc_is_accepted():
        raise SystemExit("RFC-0060 must be Accepted")
    if not rfc_resolved_questions_present():
        raise SystemExit("RFC-0060 must include Resolved questions (D-067)")
    if not d067_present():
        raise SystemExit("D-067 must be Accepted in DECISIONS.md")
    print("ok: RFC-0060 Accepted + D-067 + resolved questions")
    _check_versions(allow_planned=args.allow_planned)
    _check_review(allow_planned=args.allow_planned)

    import check_release_gate as gate

    if args.allow_planned:
        errors = gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.39.toml (planned shape)")
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
    print(f"ok: verify_pkg_39 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
