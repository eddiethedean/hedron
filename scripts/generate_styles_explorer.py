#!/usr/bin/env python3
"""Build the backend-free docs Styles Explorer from the real theme gallery.

Only generation executes Python. The published artifact uses hedron-sim's
pre-rendered route table and the same CSS/theme exports as a running app.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import replace
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/assets/styles-explorer"
GALLERY = ROOT / "examples/theme-gallery"
STATIC = ROOT / "packages/hedron/src/hedron/static"
SECTIONS = (
    "dashboard",
    "components",
    "forms",
    "surfaces",
    "content",
    "settings",
    "orders",
    "support",
    "media",
)

for _source in ("hedron-core", "hedron", "hedron-sim", "hedron-charts", "hedron-maps"):
    sys.path.insert(0, str(ROOT / f"packages/{_source}/src"))


class _OfflineMarkup(HTMLParser):
    """Convert gallery navigation to declared sim routes, never remote links."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "a":
            url = urlsplit(values.get("href") or "")
            path = url.path
            section = "dashboard" if path == "/" else path.removeprefix("/")
            if section in SECTIONS and not url.scheme and not url.netloc:
                values.update(
                    {
                        "href": f"/{section}",
                        "hx-get": f"/{section}",
                        "hx-target": "#style-gallery",
                        "hx-swap": "innerHTML",
                    }
                )
        if values.get("src") == "/gallery-art.svg":
            values["src"] = "landscape.svg"
        # Native capture is intentionally not granted by an in-docs style preview.
        if (tag == "input" and "capture" in values) or (
            tag == "button" and any("geolocation" in key for key in values)
        ):
            values.update(
                {"disabled": None, "title": "Capture requires a real app and device permission."}
            )
        rendered = " ".join(
            key if value is None else f'{key}="{escape(value, quote=True)}"'
            for key, value in values.items()
        )
        self.parts.append(f"<{tag}{' ' if rendered else ''}{rendered}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")


def build_files() -> dict[Path, str]:
    from hedron import Page, html
    from hedron_core import render
    from hedron_core.theme import (
        FOLIO_ACCENTS,
        aurora_theme,
        classic_theme,
        derived_theme_tokens,
        folio_theme,
    )
    from hedron_core.theme_contract import component_contract_manifest, export_theme
    from hedron_sim import SimApp, embed_demo

    spec = importlib.util.spec_from_file_location("hedron_docs_style_gallery", GALLERY / "app.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load theme gallery")
    gallery = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gallery)
    app = SimApp(title="Styles Explorer gallery", demo_id="styles-explorer")
    region = app.region("style-gallery")

    def section_markup(name: str) -> str:
        document = render(getattr(gallery, name)()).html
        body = re.search(r"<body[^>]*>(.*?)</body>", document, re.DOTALL)
        if body is None:
            raise ValueError(f"Missing gallery body: {name}")
        # Theme/mode selectors live in the explorer shell, not in stale page chrome.
        content = re.sub(r"<header\b.*?</header>", "", body.group(1), count=1, flags=re.DOTALL)
        content = re.sub(
            r"A real-world composition of Hedron built-ins, rendered against the .*? palette\.",
            "Real Hedron built-ins rendered with the theme and mode selected above.",
            content,
        )
        parser = _OfflineMarkup()
        parser.feed(content)
        return "".join(parser.parts)

    # Raw HTML is already rendered by Hedron; sim freezes it as fragment payloads.
    from hedron_core.security import TrustedHtml

    def raw(content: str):
        return html.raw(TrustedHtml.reviewed(content, source="in-tree theme gallery"))

    pages = {name: section_markup(name) for name in SECTIONS}

    def home() -> Page:
        return Page(html.div(raw(pages["dashboard"]), id=region.id))

    app.page("/")(home)

    for name, content in pages.items():
        app.fragment(f"/{name}", region=region)(lambda content=content: raw(content))

    themes = {
        **{f"folio:{accent}": folio_theme(accent=accent) for accent in FOLIO_ACCENTS},
        "classic": classic_theme(),
        "aurora": aurora_theme(),
    }
    exports = {}
    for name, theme in themes.items():
        exported = export_theme(theme).to_dict()
        exported["resolved_modes"] = {}
        for mode in ("light", "dark"):
            resolved = replace(theme, tokens={**theme.tokens, **theme.modes.get(mode, {})})
            exported["resolved_modes"][mode] = {
                **derived_theme_tokens(resolved),
                **resolved.tokens,
            }
        exports[name] = exported
    data = {
        "schema": "hedron.docs-styles-explorer/1",
        "themes": exports,
        "accents": list(FOLIO_ACCENTS),
        "components": component_contract_manifest(),
        "sections": list(SECTIONS),
    }
    payload = escape(json.dumps(data, sort_keys=True, separators=(",", ":")))
    shell = (ROOT / "docs/demos/styles-explorer.html").read_text(encoding="utf-8")
    # RTD/CDN caches shared static assets independently of newly deployed HTML.
    # Couple each shell to the exact controller and stylesheet it was built with.
    for asset in ("javascript/styles-explorer.js", "stylesheets/styles-explorer.css"):
        digest = hashlib.sha256((ROOT / "docs" / asset).read_bytes()).hexdigest()[:16]
        shell = shell.replace(f'../../{asset}"', f'../../{asset}?v={digest}"')
    shell = shell.replace(
        "<!-- EXPLORER_DATA -->", f"<template id=explorer-data>{payload}</template>"
    )
    # A direct entrance to the same visual QA app, not a second approximation of
    # its components. Both entrances share the gallery routes and theme runtime.
    component_shell = (
        shell.replace("Styles Explorer", "Component Explorer")
        .replace('data-initial-section="dashboard"', 'data-initial-section="components"')
        .replace(
            "Real components. Canonical themes. No backend.",
            "The visual QA app: appearances, emphases, sizes, and component states. No backend.",
        )
    )
    preview = (
        '<!doctype html><html lang="en" data-theme="light" data-hedron-theme="folio"><head>'
        '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Hedron style preview</title><link rel="stylesheet" href="hedron-default.css">'
        '<style id="theme-css"></style>'
        "<style>body{margin:0;padding:1rem} footer{margin-top:2rem}"
        "[data-hedron-sim-trace]{font-size:.8rem}</style></head><body>"
        + embed_demo(app, class_="styles-gallery")
        + '<script src="hedron-sim.js"></script><script type="module" src="hedron-ui.mjs"></script>'
        "</body></html>\n"
    )
    from hedron_sim.assets import javascript_text

    return {
        OUTPUT / "index.html": shell,
        OUTPUT / "components.html": component_shell,
        OUTPUT / "preview.html": preview,
        OUTPUT / "hedron-default.css": (STATIC / "hedron-default.css").read_text(encoding="utf-8"),
        OUTPUT / "hedron-ui.mjs": (STATIC / "hedron-ui.mjs").read_text(encoding="utf-8"),
        OUTPUT / "hedron-sim.js": javascript_text(),
        OUTPUT / "landscape.svg": (GALLERY / "landscape.svg").read_text(encoding="utf-8"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated assets are stale.")
    args = parser.parse_args(argv)
    dirty = False
    for path, content in build_files().items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        dirty = True
        if args.check:
            print(f"out of date: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")
    return int(args.check and dirty)


if __name__ == "__main__":
    raise SystemExit(main())
