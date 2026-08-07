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
    from demos.components import COMPONENT_DEMO_BUILDERS, build_component_demo
    from demos.core_concepts import build_core_concepts_modes_demo
    from demos.guides import (
        build_allowlist_403_demo,
        build_charts_htmx_demo,
        build_cookbook_oob_demo,
        build_crud_demo,
        build_forms_invite_demo,
        build_htmx_interactions_demo,
        build_live_poll_demo,
        build_mutations_htmx_demo,
    )
    from demos.hello_refresh import build_hello_refresh_demo

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
        "htmx-interactions.html": build_htmx_interactions_demo(),
        "forms-invite.html": build_forms_invite_demo(),
        "live-poll.html": build_live_poll_demo(),
        "cookbook-oob.html": build_cookbook_oob_demo(),
        "allowlist-403.html": build_allowlist_403_demo(),
        "charts-htmx.html": build_charts_htmx_demo(),
        "crud-notes.html": build_crud_demo(),
        "mutations-htmx.html": build_mutations_htmx_demo(),
        "core-concepts-modes.html": build_core_concepts_modes_demo(),
    }
    for name in sorted(COMPONENT_DEMO_BUILDERS):
        demos[f"{name}.html"] = build_component_demo(name)

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
