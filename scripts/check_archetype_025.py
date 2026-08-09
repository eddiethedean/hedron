#!/usr/bin/env python3
"""ARCHETYPE-025: production archetype SSOT + ingredient checklist for phase 0.25.

Reads ``docs/api/PRODUCTION_ARCHETYPE.md``.

* ``--allow-draft`` (packet refine): require SSOT + ingredient fence + reference-app
  pin; do not yet require public guide links.
* Cut (omit flag): also require production-quality and production-readiness guides
  to link the archetype / ``examples/reference-app``.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "docs" / "api" / "PRODUCTION_ARCHETYPE.md"
PROD_QUALITY = ROOT / "docs" / "guides" / "production-quality.md"
PROD_READY = ROOT / "docs" / "guides" / "production-readiness.md"
INGREDIENT_HEADING = "### Ingredient checklist (machine-checked)"
FENCE_RE = re.compile(r"```text\n(.*?)```", re.S)
REQUIRED_INGREDIENTS = (
    "reverse-proxy subpath",
    "Redis job/cache",
    "sticky sessions or external session store",
    "HEDRON_ENV=production",
    "CSP",
    "Explorer off",
    "multi-worker",
)


def _parse_ingredients(text: str) -> list[str]:
    idx = text.find(INGREDIENT_HEADING)
    if idx < 0:
        raise ValueError(f"missing heading {INGREDIENT_HEADING!r}")
    match = FENCE_RE.search(text[idx:])
    if not match:
        raise ValueError("missing ```text ingredient fence after machine-checked heading")
    lines: list[str] = []
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Allow draft SSOT without completed guide links (packet refine).",
    )
    args = parser.parse_args(argv)

    errors: list[str] = []
    if not SSOT.is_file():
        print(f"missing {SSOT.relative_to(ROOT)}", file=sys.stderr)
        return 1

    text = SSOT.read_text(encoding="utf-8")
    if "examples/reference-app" not in text:
        errors.append("PRODUCTION_ARCHETYPE.md must pin examples/reference-app")
    if "ARCHETYPE-025" not in text:
        errors.append("PRODUCTION_ARCHETYPE.md missing ARCHETYPE-025")

    try:
        ingredients = _parse_ingredients(text)
    except ValueError as exc:
        errors.append(str(exc))
        ingredients = []

    missing = [item for item in REQUIRED_INGREDIENTS if item not in ingredients]
    if missing:
        errors.append(f"ingredient checklist missing: {missing}")

    if not args.allow_draft:
        for path, label in (
            (PROD_QUALITY, "production-quality.md"),
            (PROD_READY, "production-readiness.md"),
        ):
            if not path.is_file():
                errors.append(f"missing {path.relative_to(ROOT)}")
                continue
            body = path.read_text(encoding="utf-8")
            if "examples/reference-app" not in body and "PRODUCTION_ARCHETYPE" not in body:
                errors.append(
                    f"{label} must link examples/reference-app or PRODUCTION_ARCHETYPE at cut"
                )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    mode = "allow-draft" if args.allow_draft else "cut"
    print(f"ok: ARCHETYPE-025 ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
