#!/usr/bin/env python3
"""CHARTS-025: Matplotlib-default Supported path + Plotly/Altair honesty for 0.25.

Validates docs honesty and the graduation checklist in
``docs/api/PRODUCTION_ARCHETYPE.md``. Does **not** require full Plotly/Altair graduation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "docs" / "api" / "PRODUCTION_ARCHETYPE.md"
WHATS_READY = ROOT / "docs" / "guides" / "whats-ready.md"
WHATS_READY_EVIDENCE = ROOT / "docs" / "guides" / "whats-ready-evidence.md"
GRAD_HEADING = "### Graduation checklist (Plotly / Altair)"
FENCE_RE = re.compile(r"```text\n(.*?)```", re.S)
REQUIRED_GRAD = (
    "pinned dependency versions",
    "CSP-compatible asset policy",
    "accessibility evidence matching DataTable bar",
)


def main() -> int:
    errors: list[str] = []
    for path in (SSOT, WHATS_READY, WHATS_READY_EVIDENCE):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    ssot = SSOT.read_text(encoding="utf-8")
    whats = WHATS_READY.read_text(encoding="utf-8")
    evidence = WHATS_READY_EVIDENCE.read_text(encoding="utf-8")
    corpus = f"{ssot}\n{whats}\n{evidence}"

    for needle in (
        "Matplotlib",
        "Supported",
        "Plotly",
        "Altair",
        "experimental",
        "CHARTS-025",
        "DataTable",
    ):
        if needle not in ssot:
            errors.append(f"PRODUCTION_ARCHETYPE.md missing required mention: {needle}")

    # Honesty: Plotly/Altair must not be unqualified Supported in the SSOT.
    forbidden = (
        "Plotly is **Supported**",
        "Altair is **Supported**",
        "Plotly/Altair are Supported",
    )
    for phrase in forbidden:
        if phrase in corpus:
            errors.append(f"forbidden Supported charts claim: {phrase!r}")

    idx = ssot.find(GRAD_HEADING)
    if idx < 0:
        errors.append(f"missing heading {GRAD_HEADING!r}")
    else:
        match = FENCE_RE.search(ssot[idx:])
        if not match:
            errors.append("missing graduation checklist ```text fence")
        else:
            items = [
                line.strip()
                for line in match.group(1).splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            missing = [item for item in REQUIRED_GRAD if item not in items]
            if missing:
                errors.append(f"graduation checklist missing: {missing}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("ok: CHARTS-025 Matplotlib-default + Plotly/Altair experimental honesty")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
