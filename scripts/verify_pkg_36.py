#!/usr/bin/env python3
"""Verify phase 0.36 packaging / packet evidence for Web Component ABI foundation.

Does **not** publish or tag. Does **not** require ``packages/hedron-elements`` during
Stage 0 refine.

* ``--allow-planned``: validate the 0.36 evidence manifest shape while rows may
  still be Planned and the living tip remains on ``0.35.x`` (packet refine).
* Omit ``--allow-planned`` at ``v0.36.0`` cut once every evidence row is
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
from _gate_036 import (  # noqa: E402
    DECISIONS,
    EXPECTED_GATES,
    GATE,
    IMPLEMENTATION,
    RELEASE_PACKET,
    REVIEW_BRIEF,
    RFC,
    UPGRADE,
    d064_present,
    elements_package_absent,
    rfc_is_accepted,
)

EVIDENCE = GATE
RELEASE_CANDIDATE = "0.36.0"
PYPROJECT = ROOT / "pyproject.toml"


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
    print("ok: 0.36 Stage 0 packet files")


def _check_gate_ids() -> None:
    data = tomllib.loads(EVIDENCE.read_text(encoding="utf-8"))
    rows = data.get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{EVIDENCE}: [[evidence]] required")
    found = {
        str(row.get("id", "")).strip()
        for row in rows
        if isinstance(row, dict)
    }
    missing = [gid for gid in EXPECTED_GATES if gid not in found]
    if missing:
        raise SystemExit(f"{EVIDENCE}: missing gate ids {missing}")
    extra = sorted(found - set(EXPECTED_GATES))
    if extra:
        raise SystemExit(f"{EVIDENCE}: unexpected gate ids {extra}")
    print("ok: release-gate-0.36.toml gate ids")


def _check_living_tip_035(*, allow_planned: bool) -> None:
    """During refine, workspace train version must remain 0.35.x."""
    if not allow_planned:
        return
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    version = str(data.get("project", {}).get("version", "")).strip()
    if not version.startswith("0.35."):
        raise SystemExit(
            f"Stage 0 refine requires living tip on 0.35.x; found workspace version {version!r}"
        )
    print(f"ok: living tip remains {version}")


def _check_review_packet(*, allow_planned: bool) -> None:
    if not REVIEW_BRIEF.is_file():
        raise SystemExit(f"missing review brief: {REVIEW_BRIEF}")
    if allow_planned:
        print("ok: security-review-036 BRIEF (allow-planned)")
        return
    packet = REVIEW_BRIEF.parent
    for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
        path = packet / name
        if not path.is_file():
            raise SystemExit(f"missing review artifact: {path}")
    if elements_package_absent():
        raise SystemExit("cut requires packages/hedron-elements")
    print("ok: security-review-036 full packet")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help=(f"Allow Planned rows (pre-cut / packet refine). Omit at v{RELEASE_CANDIDATE} cut."),
    )
    args = parser.parse_args(argv)

    _check_packet_files()
    _check_gate_ids()
    if not rfc_is_accepted():
        raise SystemExit("RFC-0060 must be Accepted")
    if not d064_present():
        raise SystemExit("D-064 must be Accepted in DECISIONS.md")
    print("ok: RFC-0060 Accepted + D-064")

    if args.allow_planned:
        if not elements_package_absent():
            raise SystemExit(
                "Stage 0 forbids packages/hedron-elements; remove before --allow-planned"
            )
        print("ok: packages/hedron-elements absent (Stage 0)")
        _check_living_tip_035(allow_planned=True)
        _check_review_packet(allow_planned=True)
        import check_release_gate as gate

        errors = gate.check_evidence_manifest_lenient(EVIDENCE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: release-gate-0.36.toml (planned shape)")
    else:
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
    print(f"ok: verify_pkg_36 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
