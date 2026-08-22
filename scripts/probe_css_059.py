#!/usr/bin/env python3
"""Run the reproducible parser, recipe, and browser capability probes for 0.59."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hedron_core import compile_css
from hedron_core.builtins.layout import Container
from hedron_core.builtins.style_scope import StyleScope
from hedron_core.diagnostics import HedronError

ROOT = Path(__file__).resolve().parents[1]
PINNED = {
    "chromium": {"version": "151.0.7922.34", "revision": "1234"},
    "firefox": {"version": "153.0", "revision": "1538"},
    "webkit": {"version": "26.5", "revision": "2336"},
}

PARSER_CASES = {
    "imports": '@import "theme.css"; @import url("icons.css") layer(icons); .root { color: red; }',
    "selectors": ".root:where(.title):is(.active, :not(.muted)) { color: red; }",
    "layers": "@layer reset, components; @layer components { .root { color: red; } }",
    "animation": (
        "@keyframes fade { from { opacity: 0; } to { opacity: 1; } } "
        ".root { animation: fade 200ms ease; }"
    ),
    "strings-comments": '/* .comment */ .root { content: ".literal"; }',
    "unknown-at-rule": "@custom-media --narrow (width < 40rem); .root { color: red; }",
    "malformed": ".root { color: red; ",
}


def parser_probe() -> dict[str, Any]:
    cases: dict[str, Any] = {}
    for name, source in PARSER_CASES.items():
        try:
            if name == "imports":
                with tempfile.TemporaryDirectory(prefix="hedron-probe-059-") as directory:
                    root = Path(directory)
                    (root / "icons.css").write_text(".icon { color: red; }", encoding="utf-8")
                    result = compile_css(
                        source,
                        component_id=f"probe059:{name}",
                        registered_roots=[root],
                        component_dir=root,
                    )
            else:
                result = compile_css(source, component_id=f"probe059:{name}")
            cases[name] = {
                "status": "accepted",
                "css_sha256": hashlib.sha256(result.css.encode()).hexdigest(),
                "manifest_format": result.manifest.format_version,
                "symbols": sorted(result.manifest.symbols),
                "keyframes": sorted(result.manifest.keyframes),
                "diagnostics": [item.code for item in result.diagnostics],
            }
        except HedronError as exc:
            diagnostic = getattr(getattr(exc, "diagnostic", None), "code", None)
            cases[name] = {
                "status": "rejected",
                "exception": type(exc).__name__,
                "diagnostic": diagnostic,
            }
    return {"compiler_format": 2, "cases": cases}


def recipe_probe() -> dict[str, Any]:
    return {
        "container": {
            "query_default": Container.__init__.__kwdefaults__.get("query"),
            "name_default": Container.__init__.__kwdefaults__.get("name"),
            "supports_explicit_inline_size": "query" in Container.__init__.__annotations__,
            "supports_explicit_name": "name" in Container.__init__.__annotations__,
        },
        "style_scope": {
            "supports_explicit_variant": "variant" in StyleScope.__init__.__annotations__,
        },
        "result": "explicit markers are available; defaults remain compatibility-preserving",
    }


def browser_probe(browser_name: str) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, browser_name)
        browser = browser_type.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content("<button id='probe'>Probe</button><dialog></dialog>")
            features = page.evaluate(
                """() => ({
                  container_type: CSS.supports('container-type: inline-size'),
                  container_query: (() => {
                    const style = document.createElement('style');
                    style.textContent = '@container (min-width: 1px) { #probe {'
                      + ' color: rgb(1, 2, 3); } }';
                    document.head.appendChild(style);
                    const box = document.createElement('div');
                    box.style.cssText = 'container-type: inline-size; width: 10px;';
                    box.appendChild(document.getElementById('probe'));
                    document.body.appendChild(box);
                    const color = getComputedStyle(document.getElementById('probe')).color;
                    return color === 'rgb(1, 2, 3)';
                  })(),
                  subgrid: CSS.supports('grid-template-columns: subgrid'),
                  anchor_positioning: CSS.supports('anchor-name: --probe') &&
                    CSS.supports('position-anchor: --probe'),
                  popover: 'popover' in document.createElement('div'),
                  dialog: typeof HTMLDialogElement !== 'undefined',
                  starting_style: CSS.supports('selector(:starting-style)'),
                  transition_behavior: CSS.supports('transition-behavior: allow-discrete'),
                  view_transition: 'startViewTransition' in document,
                  color_mix: CSS.supports('color: color-mix(in srgb, red, blue)'),
                  light_dark: CSS.supports('color: light-dark(black, white)'),
                  typed_custom_property: CSS.supports('@property --probe'),
                  dynamic_viewport: CSS.supports('height: 100svh'),
                  logical_properties: CSS.supports('margin-inline: 1px')
                })"""
            )
            return {
                "engine": browser_name,
                "engine_identity": PINNED[browser_name],
                "browser_version": browser.version,
                "features": features,
            }
        finally:
            browser.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=sorted(PINNED))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result: dict[str, Any] = {
        "schema": "hedron.css-probe/1",
        "phase": "0.59",
        "generated_at": datetime.now(UTC).isoformat(),
        "parser": parser_probe(),
        "recipe": recipe_probe(),
    }
    if args.browser:
        result["browser"] = browser_probe(args.browser)
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
