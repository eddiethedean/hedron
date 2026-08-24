#!/usr/bin/env python3
"""Verify phase 0.37 packaging / packet evidence for form-associated elements.

Does **not** publish or tag.

* ``--allow-planned``: validate the 0.37 evidence manifest shape while rows may
  still be Planned (packet refine / mid-implementation).
* Omit ``--allow-planned`` at ``v0.37.0`` cut once every evidence row is
  ``Verified``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_037 import (  # noqa: E402
    DECISIONS,
    EXPECTED_GATES,
    GATE,
    IMPLEMENTATION,
    INVENTORY,
    RELEASE_PACKET,
    REVIEW_BRIEF,
    RFC,
    UPGRADE,
    d064_present,
    d065_present,
    elements_package_present,
    missing_high_severity_citations,
    rfc_is_accepted,
)

EVIDENCE = GATE
RELEASE_CANDIDATE = "0.37.0"
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
    required = (
        EVIDENCE,
        RELEASE_PACKET,
        IMPLEMENTATION,
        RFC,
        REVIEW_BRIEF,
        UPGRADE,
        DECISIONS,
    )
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit(f"missing Stage 0 artifacts: {missing}")
    print("ok: 0.37 Stage 0 packet files")


def _check_high_severity_issues() -> None:
    errors = missing_high_severity_citations()
    if errors:
        raise SystemExit("\n".join(errors))
    print("ok: 0.37 high-severity issue citations (#230–#237)")


def _check_gate_ids() -> None:
    data = tomllib.loads(EVIDENCE.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{EVIDENCE}: [[evidence]] required")
    found = {str(row.get("id", "")).strip() for row in rows if isinstance(row, dict)}
    missing = [gid for gid in EXPECTED_GATES if gid not in found]
    if missing:
        raise SystemExit(f"{EVIDENCE}: missing gate ids {missing}")
    extra = sorted(found - set(EXPECTED_GATES))
    if extra:
        raise SystemExit(f"{EVIDENCE}: unexpected gate ids {extra}")
    print("ok: release-gate-0.37.toml gate ids")


def _check_inventory() -> None:
    if not INVENTORY.is_file():
        raise SystemExit(f"missing inventory: {INVENTORY}")
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    packages = data.get("packages")
    if not isinstance(packages, list):
        raise SystemExit(f"{INVENTORY}: packages list required")
    missing = [name for name in EXPECTED_PACKAGES if name not in packages]
    if missing:
        raise SystemExit(f"{INVENTORY}: missing packages {missing}")
    if str(data.get("baseline", "")).strip() != "v0.37.0":
        raise SystemExit(f"{INVENTORY}: baseline must be v0.37.0")
    elements = data.get("hedron-elements")
    if not isinstance(elements, dict):
        raise SystemExit(f"{INVENTORY}: hedron-elements table required")
    if str(elements.get("disposition", "")).strip() != "incubator":
        raise SystemExit(f"{INVENTORY}: hedron-elements disposition must be incubator")
    print("ok: production-grade-inventory-037.toml")


def _check_living_tip(*, allow_planned: bool) -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    version = str(data.get("project", {}).get("version", "")).strip()
    if allow_planned:
        if version.startswith(("0.60.", "0.61.", "0.62.")):
            print(f"ok: living tip {version} (allow-planned)")
            return
        if not (
            version.startswith("0.36.")
            or version.startswith("0.37.")
            or version.startswith("0.38.")
            or version.startswith("0.39.")
            or version.startswith("0.40.")
            or version.startswith("0.41.")
            or version.startswith("0.42.")
            or version.startswith("0.43.")
            or version.startswith("0.44.")
            or version.startswith("0.45.")
            or version.startswith(
                (
                    "0.46.",
                    "0.47.",
                    "0.48.",
                    "0.49.",
                    "0.50.",
                    "0.51.",
                    "0.52.",
                    "0.53.",
                    "0.54.",
                    "0.55.",
                    "0.56.",
                    "0.57.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                    "0.58.",
                    "0.59.",
                )
            )
        ):
            raise SystemExit(
                f"unexpected workspace version {version!r} "
                "(expected 0.36.x–0.60.x during refine/history)"
            )
        print(f"ok: living tip {version} (allow-planned)")
        return
    if version != RELEASE_CANDIDATE:
        raise SystemExit(f"cut requires workspace version {RELEASE_CANDIDATE}; found {version!r}")
    print(f"ok: living tip {version}")


def _check_review_packet(*, allow_planned: bool) -> None:
    if not REVIEW_BRIEF.is_file():
        raise SystemExit(f"missing review brief: {REVIEW_BRIEF}")
    if allow_planned:
        print("ok: security-review-037 BRIEF (allow-planned)")
        return
    packet = REVIEW_BRIEF.parent
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = packet / name
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path}")
    if not elements_package_present():
        raise SystemExit("cut requires packages/hedron-elements")
    print("ok: security-review-037 full packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help=(f"Allow Planned rows (pre-cut). Omit at v{RELEASE_CANDIDATE} cut."),
    )
    args = parser.parse_args(argv)

    _check_packet_files()
    _check_high_severity_issues()
    _check_gate_ids()
    if not rfc_is_accepted():
        raise SystemExit("RFC-0060 must be Accepted")
    if not d064_present():
        raise SystemExit("D-064 must be Accepted in DECISIONS.md")
    if not d065_present():
        raise SystemExit("D-065 must be Accepted in DECISIONS.md")
    print("ok: RFC-0060 Accepted + D-064 + D-065")
    _check_living_tip(allow_planned=args.allow_planned)

    if args.allow_planned:
        _check_review_packet(allow_planned=True)
        import check_release_gate as gate

        errors = gate.check_evidence_manifest_lenient(EVIDENCE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.37.toml (planned shape)")
    else:
        _check_inventory()
        _check_review_packet(allow_planned=False)
        gate_cmd = [
            sys.executable,
            str(ROOT / "scripts" / "check_release_gate.py"),
            RELEASE_CANDIDATE,
            "--evidence-manifest",
            str(EVIDENCE),
            "--execute-verified",
        ]
        print("+", *gate_cmd)
        subprocess.check_call(gate_cmd, cwd=ROOT)
    print(f"ok: verify_pkg_37 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
