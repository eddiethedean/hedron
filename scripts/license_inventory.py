#!/usr/bin/env python3
"""Inventory first-party and pinned browser-asset licenses."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    rows: list[dict[str, str]] = []

    root_license = ROOT / "LICENSE"
    if not root_license.is_file():
        errors.append("missing root LICENSE")
    else:
        text = root_license.read_text(encoding="utf-8")
        if "MIT" not in text:
            errors.append("root LICENSE does not appear to be MIT")
        rows.append({"name": "hedron-workspace", "license": "MIT", "path": "LICENSE"})

    for pkg in sorted((ROOT / "packages").glob("*")):
        lic = pkg / "LICENSE"
        if not lic.is_file():
            errors.append(f"missing {pkg.name}/LICENSE")
            continue
        rows.append(
            {
                "name": pkg.name,
                "license": "MIT",
                "path": str(lic.relative_to(ROOT)),
            }
        )

    # Bundled HTMX is BSD-style / Zero-Clause BSD per upstream; record pin path.
    htmx = ROOT / "packages" / "hedron" / "src" / "hedron" / "static" / "htmx.min.js"
    if htmx.is_file():
        rows.append(
            {
                "name": "htmx",
                "license": "BSD-Zero-Clause (upstream HTMX)",
                "path": str(htmx.relative_to(ROOT)),
                "version": "2.0.10",
            }
        )
    else:
        errors.append("missing bundled htmx.min.js")

    disclose = ROOT / "packages" / "hedron" / "src" / "hedron" / "static" / "hedron-disclose.mjs"
    if disclose.is_file():
        rows.append(
            {
                "name": "hedron-disclose",
                "license": "MIT",
                "path": str(disclose.relative_to(ROOT)),
            }
        )

    out_dir = ROOT / "dist" / "evidence-bundle"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "license-inventory.json"
    out.write_text(json.dumps({"licenses": rows}, indent=2) + "\n", encoding="utf-8")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: license inventory ({len(rows)} entries) -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
