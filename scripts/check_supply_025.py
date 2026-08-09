#!/usr/bin/env python3
"""SUPPLY-025: RELEASE runbook requires SBOM/evidence-bundle attach on train tags.

Process gate for phase 0.25. Regenerate instructions may live with Evidence pack
scripts (``build_evidence_bundle.py``, ``generate_sbom.py``).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs" / "RELEASE.md"
EVIDENCE = ROOT / "docs" / "acceptance" / "EVIDENCE.md"

REQUIRED_PHRASES = (
    "SBOM",
    "evidence-bundle",
    "train tag",
)
REQUIRED_SCRIPT_MENTIONS = (
    "build_evidence_bundle.py",
    "generate_sbom.py",
)


def main() -> int:
    errors: list[str] = []
    if not RELEASE.is_file():
        print(f"missing {RELEASE.relative_to(ROOT)}", file=sys.stderr)
        return 1

    text = RELEASE.read_text(encoding="utf-8")
    lower = text.lower()

    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lower and phrase not in text:
            errors.append(f"RELEASE.md missing required phrase: {phrase!r}")

    # Explicit attach obligation (not just optional build steps).
    attach_ok = any(
        needle in lower
        for needle in (
            "attach on train tag",
            "attach on every train tag",
            "sbom/evidence-bundle attach",
            "sbom and evidence-bundle attach",
            "require sbom",
            "requires sbom",
        )
    )
    if not attach_ok:
        errors.append(
            "RELEASE.md must require SBOM/evidence-bundle attach on train tags "
            "(SUPPLY-025 process gate)"
        )

    for script in REQUIRED_SCRIPT_MENTIONS:
        if script not in text:
            # Allow script mention only in adjacent Evidence pack doc if RELEASE links it.
            if EVIDENCE.is_file() and script in EVIDENCE.read_text(encoding="utf-8"):
                continue
            if script not in text:
                errors.append(f"RELEASE.md (or acceptance/EVIDENCE.md) must mention {script}")

    if "SUPPLY-025" not in text and "0.25" not in text:
        errors.append("RELEASE.md should reference phase 0.25 / SUPPLY-025 supply process")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("ok: SUPPLY-025 RELEASE SBOM/evidence-bundle attach requirement")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
