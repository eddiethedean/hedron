#!/usr/bin/env python3
"""Generate the Edron showcase preview from the real example application."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "examples" / "edron-showcase" / "app.py"
OUTPUT_PATH = ROOT / "docs" / "includes" / "sim" / "edron-showcase.html"
DEFAULT_CSS_SOURCE = (
    ROOT / "packages" / "hedron" / "src" / "hedron" / "static" / "hedron-default.css"
)
DEFAULT_CSS_OUTPUT = ROOT / "docs" / "stylesheets" / "hedron-default.css"

# Prefer the checkout's Edron stack over an older installed distribution when
# documentation is generated from a source tree.
for _source in (
    ROOT / "packages" / "hedron-core" / "src",
    ROOT / "packages" / "hedron" / "src",
    ROOT / "packages" / "hedron-sim" / "src",
    ROOT / "packages" / "edron" / "src",
    ROOT / "packages" / "edron-sim" / "src",
):
    sys.path.insert(0, str(_source))


def _load_app():
    spec = importlib.util.spec_from_file_location("edron_showcase_source", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Edron showcase source: {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def build() -> str:
    """Build the docs island by dispatching the actual Edron callbacks."""
    from edron_sim import Simulation, SimulationConfig

    artifact = Simulation.from_app(
        _load_app(),
        config=SimulationConfig(
            demo_id="edron-showcase",
            entrypoint="/",
        ),
    ).build()
    return artifact.embed().strip() + "\n"


def _default_css() -> str:
    """Return the exact built-in Edron stylesheet used by a live app."""
    return DEFAULT_CSS_SOURCE.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 when the generated preview is stale.",
    )
    args = parser.parse_args(argv)

    content = build()
    css_content = _default_css()
    previous = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else None
    previous_css = (
        DEFAULT_CSS_OUTPUT.read_text(encoding="utf-8") if DEFAULT_CSS_OUTPUT.exists() else None
    )
    preview_changed = previous != content
    css_changed = previous_css != css_content
    if not preview_changed and not css_changed:
        print(f"edron showcase preview up to date: {OUTPUT_PATH.relative_to(ROOT)}")
        return 0
    if args.check:
        if preview_changed:
            print(f"out of date: {OUTPUT_PATH.relative_to(ROOT)}")
        if css_changed:
            print(f"out of date: {DEFAULT_CSS_OUTPUT.relative_to(ROOT)}")
        return 1

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_CSS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if preview_changed:
        OUTPUT_PATH.write_text(content, encoding="utf-8")
        print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    if css_changed:
        DEFAULT_CSS_OUTPUT.write_text(css_content, encoding="utf-8")
        print(f"synced {DEFAULT_CSS_OUTPUT.relative_to(ROOT)} from Hedron built-in assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
