#!/usr/bin/env python3
"""Verify phase 0.42 production-grade Web Component platform packet.

This command never publishes or tags. Use ``--allow-planned`` until every 0.42
row is Verified and the workspace is at the ``v0.42.0`` cut.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_042 import (  # noqa: E402
    AT_DISPOSITION,
    AT_PROTOCOL,
    EXPECTED_GATES,
    FLEET_INVENTORY,
    GATE,
    INVENTORY,
    PACKET_FILES,
    REVIEW_BRIEF,
    d070_present,
    living_published_baseline,
    missing_refine_citations,
    rfc_is_accepted,
    rfc_resolved_questions_present,
)

RELEASE_CANDIDATE = "0.42.0"
PYPROJECT = ROOT / "pyproject.toml"
RELEASE_TOML = ROOT / "docs" / "release.toml"
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
SUPPORTED_TAGS = (
    "hedron-example",
    "hedron-field-text",
    "hedron-field-choice",
    "hedron-field-file",
    "hedron-disclosure",
    "hedron-dialog",
    "hedron-action-async",
    "hedron-data-editor",
)


def _check_packet_files() -> None:
    missing = [str(path) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing Stage 0 artifacts: {missing}")
    print("ok: 0.42 Stage 0 packet files")


def _check_refine_citations() -> None:
    errors = missing_refine_citations()
    if errors:
        raise SystemExit("\n".join(errors))
    print("ok: 0.42 tracking #97 and medium-issue citations")


def _check_gate_ids(*, allow_planned: bool) -> None:
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] required")
    found = [str(row.get("id", "")).strip() for row in rows]
    if tuple(found) != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected gates {EXPECTED_GATES}; found {found}")
    for row in rows:
        state = str(row.get("state", "")).strip()
        if state not in {"Planned", "Implemented", "Verified"}:
            raise SystemExit(f"{GATE}: unexpected state for {row.get('id')}")
        if allow_planned and state != "Planned":
            raise SystemExit(f"{GATE}: Stage 0 requires Planned; found {row.get('id')}={state}")
    print("ok: release-gate-0.42.toml gate ids")


def _check_inventory(*, allow_planned: bool) -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    required = {
        "phase": "0.42",
        "hedron_cut": "v0.42.0",
        "owning_decision": "D-070",
        "owning_rfc": "RFC-0060",
        "living_published_baseline": "v0.41.0",
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    expected_state = "planned" if allow_planned else "verified"
    state = str(data.get("state", "")).strip()
    if allow_planned:
        if state not in {"planned", "verified"}:
            raise SystemExit(f"{INVENTORY}: state must be planned or verified (post-cut)")
        if state != "planned":
            raise SystemExit(f"{INVENTORY}: Stage 0 requires state planned")
    elif state != expected_state:
        raise SystemExit(f"{INVENTORY}: state must be {expected_state!r}")
    tags = data.get("supported_tags")
    if not isinstance(tags, list) or tuple(tags) != SUPPORTED_TAGS:
        raise SystemExit(f"{INVENTORY}: supported_tags must equal locked D-070 list")
    npm = data.get("npm_mirror")
    if not isinstance(npm, dict) or npm.get("react_runtime") is not False:
        raise SystemExit(f"{INVENTORY}: npm_mirror.react_runtime must be false")
    bridge = data.get("react_migration_bridge")
    if not isinstance(bridge, dict) or bridge.get("in_hedron_elements") is not False:
        raise SystemExit(f"{INVENTORY}: react_migration_bridge.in_hedron_elements must be false")
    remediations = data.get("remediations")
    if not isinstance(remediations, dict):
        raise SystemExit(f"{INVENTORY}: remediations table required")
    issues = remediations.get("issues")
    if not isinstance(issues, list) or len(issues) != 32:
        raise SystemExit(f"{INVENTORY}: remediations.issues must list exactly 32 issues")
    print("ok: supported-element-inventory-042.toml")


def _check_fleet_inventory(*, allow_planned: bool) -> None:
    data = tomllib.loads(FLEET_INVENTORY.read_text(encoding="utf-8"))
    if str(data.get("baseline", "")).strip() != "v0.41.0":
        raise SystemExit(f"{FLEET_INVENTORY}: baseline must be v0.41.0")
    if str(data.get("hedron_cut", "")).strip() != "v0.42.0":
        raise SystemExit(f"{FLEET_INVENTORY}: hedron_cut must be v0.42.0")
    state = str(data.get("state", "")).strip()
    if allow_planned:
        if state != "planned":
            raise SystemExit(f"{FLEET_INVENTORY}: Stage 0 requires state planned")
    elif state != "verified":
        raise SystemExit(f"{FLEET_INVENTORY}: cut requires state verified")
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
    if allow_planned:
        if str(elements.get("disposition", "")).strip() != "incubator":
            raise SystemExit(f"{FLEET_INVENTORY}: hedron-elements disposition must be incubator")
        if str(elements.get("maturity", "")).strip() != "alpha":
            raise SystemExit(f"{FLEET_INVENTORY}: Stage 0 hedron-elements maturity must be alpha")
        if str(elements.get("pin", "")).strip() != ">=0.41.0,<0.42":
            raise SystemExit(
                f"{FLEET_INVENTORY}: Stage 0 hedron-elements pin must stay >=0.41.0,<0.42"
            )
        if elements.get("supported") not in ([], None):
            raise SystemExit(f"{FLEET_INVENTORY}: Stage 0 hedron-elements.supported must be empty")
        excluded = elements.get("excluded") or []
        if "production_grade_until_0_42" not in excluded:
            raise SystemExit(
                f"{FLEET_INVENTORY}: excluded must include production_grade_until_0_42"
            )
    else:
        if str(elements.get("disposition", "")).strip() != "production_grade":
            raise SystemExit(
                f"{FLEET_INVENTORY}: cut hedron-elements disposition must be production_grade"
            )
        if str(elements.get("maturity", "")).strip() != "beta":
            raise SystemExit(f"{FLEET_INVENTORY}: cut hedron-elements maturity must be beta")
        if str(elements.get("pin", "")).strip() != ">=0.42.0,<0.43":
            raise SystemExit(f"{FLEET_INVENTORY}: cut hedron-elements pin must be >=0.42.0,<0.43")
        supported_tags = elements.get("supported") or []
        if set(supported_tags) != set(SUPPORTED_TAGS):
            raise SystemExit(
                f"{FLEET_INVENTORY}: cut hedron-elements.supported must equal locked tags"
            )
    print("ok: production-grade-inventory-042.toml")


def _workspace_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    return str(data.get("project", {}).get("version", "")).strip()


def _check_versions(*, allow_planned: bool) -> None:
    version = _workspace_version()
    published = living_published_baseline()
    release = tomllib.loads(RELEASE_TOML.read_text(encoding="utf-8")).get("release") or {}
    published_version = str(release.get("published_version", "")).strip()
    if allow_planned:
        if published != "v0.41.0" or published_version != "0.41.0":
            raise SystemExit(
                f"Stage 0 living tip must remain Published v0.41.0; found {published!r}"
            )
        if not version.startswith("0.41."):
            raise SystemExit(
                f"unexpected workspace version {version!r}; Stage 0 expects 0.41.x living tip"
            )
        print(f"ok: living tip {version} / Published {published} (0.42 allow-planned)")
        return
    if version != RELEASE_CANDIDATE and not version.startswith(("0.43.", "0.44.", "0.45.", "0.46.", "0.47.")):
        raise SystemExit(
            f"cut requires workspace version {RELEASE_CANDIDATE} or post-cut "
            f"0.43.x/0.44.x/0.45.x; found {version!r}"
        )
    if version.startswith(("0.43.", "0.44.", "0.45.", "0.46.", "0.47.")):
        print(f"ok: post-cut living tip {version} (0.42 packet verified)")
        return
    print(f"ok: cut version Hedron {version}")


def _check_review(*, allow_planned: bool) -> None:
    if allow_planned:
        brief = REVIEW_BRIEF.read_text(encoding="utf-8")
        if "Stage 0 brief only" not in brief:
            raise SystemExit(f"{REVIEW_BRIEF}: must be Stage 0 brief only")
        for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
            path = REVIEW_BRIEF.parent / name
            if path.is_file():
                raise SystemExit(f"Stage 0 must not include cut review artifact yet: {path}")
        print("ok: security-review-042 BRIEF (allow-planned)")
        return
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = REVIEW_BRIEF.parent / name
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path}")
    print("ok: security-review-042 full packet")


def _check_at_skeleton(*, allow_planned: bool) -> None:
    protocol = AT_PROTOCOL.read_text(encoding="utf-8")
    if "does **not** claim product-wide Supported human AT" not in protocol and (
        "does not claim product-wide Supported human AT" not in protocol
    ):
        raise SystemExit(f"{AT_PROTOCOL}: must disclaim product-wide Supported human AT")
    if "SR-021" not in protocol or "#86" not in protocol:
        raise SystemExit(f"{AT_PROTOCOL}: must reference SR-021 / #86 as distinct")
    data = tomllib.loads(AT_DISPOSITION.read_text(encoding="utf-8"))
    if str(data.get("gate", "")).strip() != "AT-042":
        raise SystemExit(f"{AT_DISPOSITION}: gate must be AT-042")
    expected = "planned" if allow_planned else "verified"
    state = str(data.get("state", "")).strip()
    if allow_planned:
        if state != "planned":
            raise SystemExit(f"{AT_DISPOSITION}: Stage 0 state must be planned")
        summary = data.get("summary") or {}
        if int(summary.get("sessions_recorded", -1)) != 0:
            raise SystemExit(f"{AT_DISPOSITION}: Stage 0 sessions_recorded must be 0")
    elif state != expected:
        raise SystemExit(f"{AT_DISPOSITION}: state must be {expected}")
    print("ok: human-at/042 AT-042 skeleton")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args(argv)

    _check_packet_files()
    _check_refine_citations()
    _check_gate_ids(allow_planned=args.allow_planned)
    _check_inventory(allow_planned=args.allow_planned)
    _check_fleet_inventory(allow_planned=args.allow_planned)
    _check_at_skeleton(allow_planned=args.allow_planned)
    if not rfc_is_accepted():
        raise SystemExit("RFC-0060 must be Accepted")
    if not rfc_resolved_questions_present():
        raise SystemExit("RFC-0060 must include Resolved questions (D-070)")
    if not d070_present():
        raise SystemExit("D-070 must be Accepted in DECISIONS.md")
    print("ok: RFC-0060 Accepted + D-070 + resolved questions")
    _check_versions(allow_planned=args.allow_planned)
    _check_review(allow_planned=args.allow_planned)

    import check_release_gate as gate

    if args.allow_planned:
        errors = gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.42.toml (planned shape)")
    elif _workspace_version().startswith(("0.43.", "0.44.", "0.45.", "0.46.", "0.47.")):
        errors = gate.check_evidence_manifest(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.42.toml (verified historical packet)")
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
    print(f"ok: verify_pkg_42 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
