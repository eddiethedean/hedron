"""The offline explorer exports real themes and stays generation-gated."""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

from hedron_core.theme import (
    FOLIO_ACCENTS,
    aurora_theme,
    classic_theme,
    emit_theme_css,
    folio_theme,
)
from hedron_core.theme_contract import resolve_theme

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "docs/assets/styles-explorer"


def _data() -> dict:
    source = (ASSETS / "index.html").read_text(encoding="utf-8")
    match = re.search(r"<template id=explorer-data>(.*?)</template>", source, re.DOTALL)
    assert match is not None
    return json.loads(html.unescape(match.group(1)))


def test_generated_theme_exports_are_canonical_and_complete() -> None:
    data = _data()
    assert data["schema"] == "hedron.docs-styles-explorer/1"
    assert data["accents"] == list(FOLIO_ACCENTS)
    themes = {
        **{f"folio:{accent}": folio_theme(accent=accent) for accent in FOLIO_ACCENTS},
        "classic": classic_theme(),
        "aurora": aurora_theme(),
    }
    assert set(data["themes"]) == set(themes)
    for name, theme in themes.items():
        exported = data["themes"][name]
        assert exported["css"] == emit_theme_css(theme)
        assert exported["theme"]["tokens"] == dict(resolve_theme(theme).tokens)
        assert exported["resolved_modes"]["light"]["color.bg"] == theme.tokens["color.bg"]
        assert exported["resolved_modes"]["dark"]["color.bg"] == theme.modes["dark"]["color.bg"]
    assert data["components"]["components"]


def test_gallery_routes_and_runtime_assets_are_local() -> None:
    source = (ASSETS / "preview.html").read_text(encoding="utf-8")
    match = re.search(r"<template data-hedron-sim-routes>(.*?)</template>", source, re.DOTALL)
    assert match is not None
    table = json.loads(html.unescape(match.group(1)))
    assert set(table["routes"]) == {f"GET /{section}" for section in _data()["sections"]}
    for route in table["routes"].values():
        assert route["regions"][0]["selector"] == "#style-gallery"
        assert 'hx-target="#style-gallery"' in route["html"]
        assert 'src="/gallery-art.svg"' not in route["html"]
    for name in (
        "hedron-sim.js",
        "hedron-ui.mjs",
        "hedron-default.css",
        "landscape.svg",
    ):
        assert (ASSETS / name).is_file()
    assert (ASSETS / "hedron-default.css").read_bytes() == (
        ROOT / "packages/hedron/src/hedron/static/hedron-default.css"
    ).read_bytes()


def test_styles_explorer_generation_check() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/generate_styles_explorer.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_docs_expose_embedded_and_full_page_explorer() -> None:
    guide = (ROOT / "docs/guides/styles-explorer.md").read_text(encoding="utf-8")
    assert 'src="../../assets/styles-explorer/index.html"' in guide
    assert "[Open the full-page explorer](../assets/styles-explorer/index.html)" in guide
    assert "Styles Explorer: guides/styles-explorer.md" in (ROOT / "mkdocs.yml").read_text()
    assert "styles-explorer.md" in (ROOT / "docs/guides/styling.md").read_text()


def test_component_explorer_reuses_the_visual_qa_app() -> None:
    source = (ASSETS / "components.html").read_text(encoding="utf-8")
    assert "<title>Hedron Component Explorer</title>" in source
    assert 'data-initial-section="components"' in source
    assert '<iframe id="left"' in source and 'src="preview.html"' in source
    match = re.search(r"<template id=explorer-data>(.*?)</template>", source, re.DOTALL)
    assert match is not None
    assert json.loads(html.unescape(match.group(1))) == _data()
    preview = (ASSETS / "preview.html").read_text(encoding="utf-8")
    routes = re.search(r"<template data-hedron-sim-routes>(.*?)</template>", preview, re.DOTALL)
    assert routes is not None
    component_html = json.loads(html.unescape(routes.group(1)))["routes"]["GET /components"]["html"]
    for appearance in ("Solid", "Outline", "Soft", "Ghost", "Plain", "Raised"):
        assert f"{appearance} buttons" in component_html
    guide = (ROOT / "docs/guides/component-explorer.md").read_text(encoding="utf-8")
    assert 'src="../../assets/styles-explorer/components.html"' in guide
    assert (
        "[Open the full-page Component Explorer](../assets/styles-explorer/components.html)"
        in guide
    )
    assert "Component Explorer: guides/component-explorer.md" in (ROOT / "mkdocs.yml").read_text()
