from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from hedron_docs import DocsBuildConfig, NavigationItem, compile_site, create_docs_app


def _client(tmp_path: Path, *, release_label: str = "", release_url: str = "") -> TestClient:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n\n## Install\n", encoding="utf-8")
    (docs / "quickstart.md").write_text("# Quickstart\n", encoding="utf-8")
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (docs / "api.md").write_text("# API reference\n", encoding="utf-8")
    (docs / "component.md").write_text("# Component guide\n", encoding="utf-8")
    manifest = compile_site(
        DocsBuildConfig(
            docs_dir=docs,
            output=tmp_path / "site.json",
            release_label=release_label,
            release_url=release_url,
        )
    )
    return TestClient(create_docs_app(manifest))


def test_w5_native_application_shell_and_mobile_navigation(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get("/")

    assert response.status_code == 200
    assert '<a class="hedron-skip-link" href="#main-panel"' in response.text
    assert 'data-hedron-app-shell="true"' in response.text
    assert '<header class="hedron-app-shell-header"' in response.text
    assert '<nav id="main-panel-nav"' in response.text
    assert '<main id="main-panel"' in response.text
    assert 'aria-current="page"' in response.text
    assert 'class="hedron-docs-mobile-nav"' in response.text
    assert "<details" in response.text
    assert '<footer class="hedron-app-shell-footer"' in response.text
    assert 'data-hedron-color-mode="true"' in response.text
    assert response.text.count("<head>") == 1


def test_w5_theme_form_is_an_ordinary_no_javascript_post(tmp_path: Path) -> None:
    client = _client(tmp_path)
    page = client.get("/guide/?q=1")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
    assert csrf_match is not None
    response = client.post(
        "/preferences/theme?return_to=%2Fguide%2F%3Fq%3D1",
        data={"color_mode": "dark", "csrf_token": csrf_match.group(1)},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/guide/?q=1"
    assert "hedron_color_mode=dark" in response.headers["set-cookie"]
    page = client.get("/guide/")
    assert 'data-theme="dark"' in page.text


def test_w5_theme_redirect_rejects_network_path_targets(tmp_path: Path) -> None:
    client = _client(tmp_path)
    page = client.get("/")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
    assert csrf_match is not None
    response = client.post(
        "/preferences/theme?return_to=%2F%2Fattacker.example",
        data={"color_mode": "system", "csrf_token": csrf_match.group(1)},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_w5_manifest_navigation_groups_and_breadcrumbs_are_semantic(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n", encoding="utf-8")
    (docs / "guide.md").write_text("# Start here\n", encoding="utf-8")
    (docs / "deep.md").write_text("# Deep reference\n", encoding="utf-8")
    manifest = compile_site(
        DocsBuildConfig(
            docs_dir=docs,
            output=tmp_path / "site.json",
            navigation=(
                NavigationItem("Home", path="index.md"),
                NavigationItem(
                    "Guides",
                    children=(
                        NavigationItem("Start", path="guide.md"),
                        NavigationItem(
                            "Advanced",
                            children=(NavigationItem("Deep", path="deep.md"),),
                        ),
                    ),
                ),
            ),
        )
    )
    response = TestClient(create_docs_app(manifest)).get("/guide/")

    assert response.status_code == 200
    assert "hedron-docs-nav-section" in response.text
    assert response.text.count('class="hedron-docs-nav-group"') == 4
    assert 'data-hedron-nav-section-current="true"' in response.text
    assert 'aria-label="Breadcrumb"' in response.text
    assert 'aria-current="page">Start</li>' in response.text
    assert response.text.index('aria-label="Breadcrumb"') < response.text.index("<article")


def test_w5_release_banner_uses_manifest_release_facts(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        release_label="v0.5.0",
        release_url="https://example.test/releases/v0.5.0",
    )
    response = client.get("/")

    assert response.status_code == 200
    assert 'data-hedron-app-banner="true"' in response.text
    assert 'class="hedron-docs-release"' in response.text
    assert 'href="https://example.test/releases/v0.5.0"' in response.text
    assert "v0.5.0" in response.text


def test_w5_404_is_rendered_by_the_same_shell(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get("/not-found/")

    assert response.status_code == 404
    assert "Page not found" in response.text
    assert "<title>Page not found</title>" in response.text
    assert 'data-hedron-app-shell="true"' in response.text
    assert '<main id="main-panel"' in response.text


def test_w5_vertical_slice_pages_share_the_shell(tmp_path: Path) -> None:
    client = _client(tmp_path)
    for path in ("/", "/quickstart/", "/guide/", "/api/", "/component/"):
        response = client.get(path)
        assert response.status_code == 200
        assert 'data-hedron-app-shell="true"' in response.text


def test_w5_css_contains_responsive_shell_hooks(tmp_path: Path) -> None:
    client = _client(tmp_path)
    page = client.get("/")
    css_path = next(
        part.split('"', 1)[0]
        for part in page.text.split('href="')
        if part.startswith("/_hedron-docs/docs-")
    )
    css = client.get(css_path)

    assert css.status_code == 200
    assert ".hedron-docs-mobile-nav" in css.text
    assert "@media (max-width: 48rem)" in css.text
