from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hedron_docs import (
    DocsBuildConfig,
    DocsError,
    compile_site,
    create_docs_app,
    import_mkdocs,
    load_config,
    load_manifest,
    parse_markdown,
    search,
)


def _config(tmp_path: Path) -> DocsBuildConfig:
    docs = tmp_path / "docs"
    docs.mkdir()
    return DocsBuildConfig(
        docs_dir=docs, output=tmp_path / "build" / "site.json", site_title="Test docs"
    )


def test_compile_is_deterministic_and_round_trips(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config = DocsBuildConfig(
        docs_dir=config.docs_dir,
        output=config.output,
        site_title=config.site_title,
        max_query_length=32,
    )
    (config.docs_dir / "index.md").write_text("# Home\n\nWelcome **friend**.\n", encoding="utf-8")
    (config.docs_dir / "guide.md").write_text(
        "# Guide\n\nRead [home](index.md) and [root](/index.md).\n", encoding="utf-8"
    )
    manifest = compile_site(config)
    output = manifest.write(config.output)
    assert manifest.dumps() == output.read_text(encoding="utf-8")
    assert load_manifest(output) == manifest
    assert manifest.pages[1].path == "/guide/"
    links = [node for node in manifest.pages[1].nodes if node.kind == "paragraph"][0].children
    assert [node.attr("href") for node in links if node.kind == "link"] == ["/", "/"]
    assert json.loads(manifest.dumps())["schema_version"] == "hedron-docs-manifest-1"


def test_native_constructs_and_security_boundary(tmp_path: Path) -> None:
    config = _config(tmp_path)
    source = """# Home

Paragraph with **strong** and `code`.

=== "Python"
    ```python
    print(1)
    ```
=== "Shell"
    ```sh
    echo ok
    ```

!!! warning "Careful"
    Watch out.
"""
    (config.docs_dir / "index.md").write_text(source, encoding="utf-8")
    nodes = parse_markdown(source, source_path=config.docs_dir / "index.md")
    kinds = {node.kind for node in nodes}
    assert {"heading", "paragraph", "tabs", "alert"} <= kinds
    with pytest.raises(DocsError, match="raw HTML"):
        parse_markdown("<script>alert(1)</script>", source_path=config.docs_dir / "index.md")


def test_external_links_can_be_disabled(tmp_path: Path) -> None:
    config = _config(tmp_path)
    config = DocsBuildConfig(
        docs_dir=config.docs_dir,
        output=config.output,
        site_title=config.site_title,
        allow_external_links=False,
    )
    (config.docs_dir / "index.md").write_text("[external](https://example.com)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="external documentation URL is disabled"):
        compile_site(config)


def test_app_pages_search_and_metadata(tmp_path: Path) -> None:
    config = _config(tmp_path)
    (config.docs_dir / "index.md").write_text("# Home\n\nWelcome to docs.\n", encoding="utf-8")
    manifest = compile_site(config)
    app = create_docs_app(manifest)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to docs." in response.text
    assert "<h1" in response.text
    assert client.get("/missing").status_code == 404
    search_response = client.get("/search", params={"q": "home"})
    assert search_response.status_code == 200
    assert "1 result" in search_response.text
    assert client.get("/robots.txt").status_code == 200
    assert client.get("/sitemap.xml").status_code == 200
    assert client.get("/healthz").json()["status"] == "ok"
    assert client.get("/readyz").json()["status"] == "ready"


def test_search_is_bounded() -> None:
    from hedron_docs import PageRecord, SiteManifest

    page = PageRecord("index.md", "/", "Home", "Install docs", (), (), "install docs", "hash")
    manifest = SiteManifest("Docs", "", "", (page,))
    assert search(manifest, "install")[0].path == "/"
    with pytest.raises(ValueError):
        search(manifest, "x" * 201)


def test_config_rejects_unknown_keys_and_imports_mkdocs(tmp_path: Path) -> None:
    bad = tmp_path / "bad.toml"
    bad.write_text("[site]\nunknown = true\n", encoding="utf-8")
    with pytest.raises(DocsError, match="unknown configuration keys"):
        load_config(bad)
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "\n".join(
            (
                "site_name: Example",
                "docs_dir: docs",
                "site_url: !ENV [URL, default]",
                "exclude_docs: |",
                "  private/**",
                "",
            )
        ),
        encoding="utf-8",
    )
    imported = import_mkdocs(mkdocs)
    assert imported.site_title == "Example"
    assert imported.exclude == ("private/**",)
