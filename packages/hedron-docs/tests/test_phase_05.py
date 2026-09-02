from __future__ import annotations

import re
from pathlib import Path

from fastapi.testclient import TestClient

from hedron_docs import DocsBuildConfig, compile_site, create_docs_app


def _client(tmp_path: Path, *, release_label: str = "", release_url: str = "") -> TestClient:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n\n## Install\n", encoding="utf-8")
    (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")
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
    page = client.get("/guide/")
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', page.text)
    assert csrf_match is not None
    response = client.post(
        "/preferences/theme",
        data={"color_mode": "dark", "csrf_token": csrf_match.group(1)},
        headers={"referer": "http://testserver/guide/?q=1"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/guide/?q=1"
    assert "hedron_color_mode=dark" in response.headers["set-cookie"]
    page = client.get("/guide/")
    assert 'data-theme="dark"' in page.text


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
    assert 'data-hedron-app-shell="true"' in response.text
    assert '<main id="main-panel"' in response.text


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
