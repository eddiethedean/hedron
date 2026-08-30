from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

ASSET_DIR = Path("docs/assets")
THEMED_ASSETS = (
    "hedron-mark-light.svg",
    "hedron-mark-dark.svg",
    "hedron-logo-light.svg",
    "hedron-logo-dark.svg",
    "edron-logo-light.svg",
    "edron-logo-dark.svg",
)


def test_themed_brand_assets_are_valid_svg_pairs() -> None:
    for name in THEMED_ASSETS:
        root = ElementTree.parse(ASSET_DIR / name).getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.get("viewBox")


def test_readmes_use_dark_sources_with_pypi_safe_light_fallbacks() -> None:
    expected = {
        Path("README.md"): "hedron-logo",
        Path("packages/hedron/README.md"): "hedron-logo",
        Path("packages/edron/README.md"): "edron-logo",
    }

    for path, stem in expected.items():
        text = path.read_text(encoding="utf-8")
        assert f"{stem}-dark.svg" in text
        assert f"{stem}-light.svg" in text
        assert "<picture>" in text


def test_docs_use_explicit_theme_assets() -> None:
    config = Path("mkdocs.yml").read_text(encoding="utf-8")
    styles = Path("docs/stylesheets/extra.css").read_text(encoding="utf-8")
    homepage = Path("docs/index.md").read_text(encoding="utf-8")

    assert "logo: assets/hedron-mark-light.svg" in config
    assert "favicon: assets/hedron-mark-light.svg" in config
    assert 'img[src$="hedron-mark-light.svg"]' in styles
    assert 'url("../assets/hedron-mark-dark.svg")' in styles
    assert 'img[src$="hedron-logo-light.svg"]' in styles
    assert 'url("../assets/hedron-logo-dark.svg")' in styles
    assert 'src="assets/hedron-logo-light.svg"' in homepage


def test_published_surfaces_do_not_reference_legacy_single_theme_names() -> None:
    paths = (
        Path("README.md"),
        Path("mkdocs.yml"),
        Path("packages/hedron/README.md"),
        Path("packages/edron/README.md"),
        Path("docs/index.md"),
        Path("docs/examples/gallery.md"),
        Path("docs/includes/sim/hello-refresh.html"),
        Path("docs/includes/sim/hello-refresh-quickstart.html"),
    )

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "hedron-mark.svg" not in text
        assert "hedron-logo.svg" not in text
        assert "edron-logo.svg" not in text
