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
        build_auth_login_demo,
        build_charts_htmx_demo,
        build_cookbook_oob_demo,
        build_crud_demo,
        build_csrf_guard_demo,
        build_data_table_filter_demo,
        build_forms_invite_demo,
        build_htmx_interactions_demo,
        build_jobs_poll_demo,
        build_live_poll_demo,
        build_minimal_form_demo,
        build_mutations_htmx_demo,
        build_pe_paths_demo,
        build_tenant_deny_demo,
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
        "jobs-poll.html": build_jobs_poll_demo(),
        "cookbook-oob.html": build_cookbook_oob_demo(),
        "allowlist-403.html": build_allowlist_403_demo(),
        "charts-htmx.html": build_charts_htmx_demo(),
        "crud-notes.html": build_crud_demo(),
        "mutations-htmx.html": build_mutations_htmx_demo(),
        "core-concepts-modes.html": build_core_concepts_modes_demo(),
        "minimal-form.html": build_minimal_form_demo(),
        "auth-login.html": build_auth_login_demo(),
        "csrf-guard.html": build_csrf_guard_demo(),
        "data-table-filter.html": build_data_table_filter_demo(),
        "pe-paths.html": build_pe_paths_demo(),
        "tenant-deny.html": build_tenant_deny_demo(),
    }
    for name in sorted(COMPONENT_DEMO_BUILDERS):
        demos[f"{name}.html"] = build_component_demo(name)

    from demos.runnable_code import runnable_path

    missing_runnable = [
        html_name.removesuffix(".html")
        for html_name in demos
        if not runnable_path(html_name.removesuffix(".html")).is_file()
    ]
    if missing_runnable:
        print(
            "missing runnable Demo/Code sources under docs/demos/runnable/: "
            + ", ".join(sorted(missing_runnable))
        )
        return 1

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

    if args.check and not dirty:
        print("sim demos up to date")

    # Keep guide / getting-started Demo/Code tabs aligned with runnable sources.
    from sync_demo_code_tabs import main as sync_tabs

    tab_rc = sync_tabs(["--check"] if args.check else [])
    if args.check and (dirty or tab_rc != 0):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
