#!/usr/bin/env python3
"""Generate docs HTMX simulation islands from hedron-sim demos.

Writes HTML snippets under ``docs/includes/sim/`` and syncs JS/CSS assets.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INCLUDES = DOCS / "includes" / "sim"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when generated files would change.",
    )
    args = parser.parse_args(argv)

    sys.path.insert(0, str(DOCS))
    from demos.hello_refresh import build_hello_refresh_demo  # noqa: WPS433
    from hedron_sim.assets import copy_assets

    copy_assets(DOCS / "javascript", DOCS / "stylesheets")

    demos = {
        "hello-refresh.html": build_hello_refresh_demo(
            status_id="service-status",
            logo_src="assets/hedron-mark.svg",
        ),
        "hello-refresh-quickstart.html": build_hello_refresh_demo(
            status_id="qs-service-status",
            logo_src="../assets/hedron-mark.svg",
            caption=(
                "Docs simulation — click <strong>Refresh status</strong> for an "
                "HTMX-style fragment swap (no server)."
            ),
        ),
    }

    INCLUDES.mkdir(parents=True, exist_ok=True)
    dirty = False
    for name, html in demos.items():
        path = INCLUDES / name
        previous = path.read_text(encoding="utf-8") if path.exists() else None
        content = html.strip() + "\n"
        if previous != content:
            dirty = True
            if not args.check:
                path.write_text(content, encoding="utf-8")
                print(f"wrote {path.relative_to(ROOT)}")
            else:
                print(f"out of date: {path.relative_to(ROOT)}")

    if args.check and dirty:
        return 1
    if args.check:
        print("sim demos up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
