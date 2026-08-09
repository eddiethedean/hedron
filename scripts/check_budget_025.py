#!/usr/bin/env python3
"""BUDGET-025: phase 0.25 critical-path workloads in PERFORMANCE_BUDGETS.md.

Requires IDs ``W-025-FRAGMENT``, ``W-025-JOB-POLL``, ``W-025-DATAEDITOR``.

* ``--allow-planned`` (packet refine): allow ``pending`` evidence_path cells.
* Cut (omit flag): each evidence_path must be non-empty and not ``pending``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUDGETS = ROOT / "docs" / "PERFORMANCE_BUDGETS.md"
REQUIRED_IDS = ("W-025-FRAGMENT", "W-025-JOB-POLL", "W-025-DATAEDITOR")
SECTION = "## Phase 0.25 critical-path workloads (`BUDGET-025`)"
ROW_RE = re.compile(
    r"\|\s*(W-025-[A-Z0-9-]+)\s*\|\s*([^|]+)\|\s*([^|]+)\|",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Allow pending evidence paths (packet refine / pre-cut).",
    )
    args = parser.parse_args(argv)

    if not BUDGETS.is_file():
        print(f"missing {BUDGETS.relative_to(ROOT)}", file=sys.stderr)
        return 1

    text = BUDGETS.read_text(encoding="utf-8")
    errors: list[str] = []
    if SECTION not in text:
        errors.append(f"PERFORMANCE_BUDGETS.md missing section {SECTION!r}")

    found: dict[str, str] = {}
    for match in ROW_RE.finditer(text):
        wid, _workload, evidence = match.group(1), match.group(2), match.group(3).strip()
        if wid.startswith("W-025-"):
            found[wid] = evidence

    for wid in REQUIRED_IDS:
        if wid not in found:
            errors.append(f"missing workload row {wid}")
            continue
        evidence = found[wid]
        if not args.allow_planned and (not evidence or evidence.lower() == "pending"):
            errors.append(
                f"{wid} evidence_path must be CI path or immutable artifact at cut; "
                f"got {evidence!r}"
            )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    mode = "allow-planned" if args.allow_planned else "cut"
    print(f"ok: BUDGET-025 workloads={list(REQUIRED_IDS)} ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
