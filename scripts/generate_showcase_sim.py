#!/usr/bin/env python3
"""Generate the Hedron showcase preview from the real runnable application."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "examples" / "showcase" / "app.py"
CSS_SOURCE = ROOT / "examples" / "showcase" / "assets" / "showcase.css"
OUTPUT_PATH = ROOT / "docs" / "includes" / "sim" / "showcase-dashboard.html"
CSS_OUTPUT = ROOT / "docs" / "stylesheets" / "showcase-sim.css"

for _source in (
    ROOT / "packages" / "hedron-core" / "src",
    ROOT / "packages" / "hedron" / "src",
    ROOT / "packages" / "hedron-sim" / "src",
):
    sys.path.insert(0, str(_source))


def _load_app_module():
    spec = importlib.util.spec_from_file_location("showcase_source", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load showcase source: {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sim_navigation(html: str) -> str:
    """Turn the runnable app's internal links into bounded sim navigation."""

    paths = {"/", "/deployments", "/components", "/settings"}
    anchor_re = re.compile(r"<a\b[^>]*>", re.IGNORECASE)

    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        href_match = re.search(r'\bhref="([^\"]+)"', tag, re.IGNORECASE)
        if href_match is None or href_match.group(1) not in paths:
            return tag
        if "data-hedron-nav-link" in tag:
            return tag
        attrs = (
            ' data-hedron-nav-link="true"'
            f' hx-get="{href_match.group(1)}"'
            ' hx-target="[data-hedron-sim-stage]"'
            ' hx-swap="innerHTML"'
        )
        return tag[:-1] + attrs + ">"

    return anchor_re.sub(replace, html)


def build() -> str:
    """Build the docs island by dispatching the actual Hedron callbacks."""
    from hedron_sim import SimApp, embed_demo

    source = _load_app_module()
    sim = SimApp(title="Hedron Showcase", demo_id="showcase-dashboard")
    stage = sim.region(
        "showcase-sim-stage",
        selector="[data-hedron-sim-stage]",
        description="Showcase page content",
    )

    @sim.page("/")
    def overview():
        return source.overview()

    @sim.fragment("/deployments", region=stage, method="GET", explanation="Open deployments")
    def deployments():
        return source.deployments()

    @sim.fragment("/components", region=stage, method="GET", explanation="Open components")
    def components():
        return source.components()

    @sim.fragment("/settings", region=stage, method="GET", explanation="Open settings")
    def settings():
        return source.settings()

    @sim.fragment(
        "/pipeline/refresh",
        region=source.pipeline_region,
        explanation="Refresh the pipeline fragment",
    )
    def refresh_pipeline():
        return source.refresh_pipeline.__wrapped__()

    @sim.action(
        "/approve",
        region=source.approval_region,
        explanation="Approve the release gate",
    )
    def approve():
        return source.approve.handler()

    rendered = embed_demo(sim)
    marker = '<section class="hedron-sim" data-hedron-sim="showcase-dashboard">'
    toolbar = (
        '<button class="hedron-sim__fullscreen" type="button" '
        'data-hedron-sim-fullscreen aria-label="Open showcase in full screen">'
        "Full screen"
        "</button>"
    )
    if marker not in rendered:
        raise RuntimeError("unexpected hedron-sim embed shape; cannot add full-screen control")
    rendered = rendered.replace(marker, marker + toolbar, 1)
    return _sim_navigation(rendered).strip() + "\n"


def _scoped_css() -> str:
    """Scope the live app's composition rules to the embedded docs island."""
    css = CSS_SOURCE.read_text(encoding="utf-8")
    source_comment = (
        "/* The showcase adds composition to Folio's built-in palette and components. */\n"
    )
    first_rule = (
        "body:has(.showcase-shell) {\n  padding: clamp(1rem, 2.5vw, 2rem);\n}\n\n"
    )
    if not css.startswith(source_comment + first_rule):
        raise RuntimeError("showcase.css changed; update the simulator CSS scoping rule")
    css = css[len(source_comment + first_rule) :].replace(
        ".showcase-shell", ".hedron-sim .showcase-shell"
    )
    return (
        "/* Generated from examples/showcase/assets/showcase.css for the docs simulator. */\n"
        + css
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated files are stale.")
    args = parser.parse_args(argv)

    generated = build()
    css = _scoped_css()
    previous = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else None
    previous_css = CSS_OUTPUT.read_text(encoding="utf-8") if CSS_OUTPUT.exists() else None
    preview_changed = previous != generated
    css_changed = previous_css != css
    if args.check:
        if preview_changed:
            print(f"out of date: {OUTPUT_PATH.relative_to(ROOT)}")
        if css_changed:
            print(f"out of date: {CSS_OUTPUT.relative_to(ROOT)}")
        return int(preview_changed or css_changed)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CSS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if preview_changed:
        OUTPUT_PATH.write_text(generated, encoding="utf-8")
        print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if css_changed:
        CSS_OUTPUT.write_text(css, encoding="utf-8")
        print(f"wrote {CSS_OUTPUT.relative_to(ROOT)}")
    if not preview_changed and not css_changed:
        print(f"showcase preview up to date: {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
