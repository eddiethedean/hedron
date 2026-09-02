from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree

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


def test_inline_content_order_and_duplicate_heading_ids(tmp_path: Path) -> None:
    source = "# Same *heading*\n\nBefore **bold** after and `code`.\n\n## Same heading\n"
    nodes = parse_markdown(source, source_path=tmp_path / "index.md")
    paragraph = next(node for node in nodes if node.kind == "paragraph")
    assert [child.kind for child in paragraph.children] == [
        "text",
        "strong",
        "text",
        "inline-code",
        "text",
    ]
    assert paragraph.text == "Before bold after and code."
    headings = [node.attr("id") for node in nodes if node.kind == "heading"]
    assert headings == ["same-heading", "same-heading-2"]


def test_multiline_paragraphs_and_lists_preserve_block_structure(tmp_path: Path) -> None:
    source = "First line\nsecond line.\n\n- one\n- two\n"
    nodes = parse_markdown(source, source_path=tmp_path / "index.md")
    assert [node.kind for node in nodes] == ["paragraph", "list"]
    assert nodes[0].text == "First line\nsecond line."
    assert [item.text for item in nodes[1].children] == ["one", "two"]


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


def test_unsafe_url_scheme_fails_during_compilation(tmp_path: Path) -> None:
    config = _config(tmp_path)
    (config.docs_dir / "index.md").write_text("[unsafe](javascript:alert(1))\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe or invalid documentation URL"):
        compile_site(config)


def test_image_fragment_is_not_treated_as_a_safe_anchor(tmp_path: Path) -> None:
    config = _config(tmp_path)
    (config.docs_dir / "index.md").write_text("![image](#sprite)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="documentation asset does not exist"):
        compile_site(config)


def test_external_image_is_validated_and_rendered(tmp_path: Path) -> None:
    config = _config(tmp_path)
    (config.docs_dir / "index.md").write_text(
        "# Home\n\n![External](https://example.com/image.png)\n", encoding="utf-8"
    )
    manifest = compile_site(config)
    response = TestClient(create_docs_app(manifest)).get("/")
    assert response.status_code == 200
    assert 'src="https://example.com/image.png"' in response.text


def test_source_symlink_cannot_escape_docs_root(tmp_path: Path) -> None:
    config = _config(tmp_path)
    outside = tmp_path / "outside.txt"
    outside.write_text("# Secret\n\nnot public\n", encoding="utf-8")
    try:
        (config.docs_dir / "leak.md").symlink_to(outside)
    except OSError:
        pytest.skip("filesystem does not permit symlinks")
    with pytest.raises(DocsError, match="escapes the documentation root"):
        compile_site(config)


@pytest.mark.parametrize(
    "source",
    [
        "search.md",
        "robots.txt.md",
        "sitemap.xml.md",
        "healthz.md",
        "readyz.md",
        "_hedron-docs/page.md",
    ],
)
def test_reserved_application_routes_are_rejected(tmp_path: Path, source: str) -> None:
    config = _config(tmp_path)
    path = config.docs_dir / source
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Reserved\n", encoding="utf-8")
    with pytest.raises(DocsError, match="route is reserved"):
        compile_site(config)


def test_app_pages_search_and_metadata(tmp_path: Path) -> None:
    base = _config(tmp_path)
    config = DocsBuildConfig(
        docs_dir=base.docs_dir,
        output=base.output,
        site_title=base.site_title,
        base_url="https://docs.example.test",
    )
    (config.docs_dir / "index.md").write_text(
        "# Home\n\nBefore **bold** after.\n\n![Logo](logo.png)\n", encoding="utf-8"
    )
    (config.docs_dir / "guide.md").write_text("# Guide\n\nSecond page.\n", encoding="utf-8")
    (config.docs_dir / "logo.png").write_bytes(b"test-png")
    manifest = compile_site(config)
    assert len(manifest.pages) == 2
    assert len(manifest.assets) == 1
    app = create_docs_app(manifest)
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Before " in response.text
    assert "bold" in response.text
    assert " after." in response.text
    assert manifest.assets[0].path in response.text
    assert "<h1" in response.text
    assert 'property="og:title"' in response.text
    assert 'rel="canonical"' in response.text
    assert client.get("/guide/").status_code == 200
    asset_response = client.get(manifest.assets[0].path)
    assert asset_response.content == b"test-png"
    assert asset_response.headers["etag"] == f'"{manifest.assets[0].source_hash}"'
    assert asset_response.headers["x-content-type-options"] == "nosniff"
    assert client.get("/missing").status_code == 404
    search_response = client.get("/search", params={"q": "home"})
    assert search_response.status_code == 200
    assert "1 result" in search_response.text
    assert client.get("/robots.txt").status_code == 200
    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    root = ElementTree.fromstring(sitemap.content)
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    assert [item.text for item in root.findall("s:url/s:loc", namespace)] == [
        "https://docs.example.test/",
        "https://docs.example.test/guide/",
    ]
    assert client.get("/healthz").json()["status"] == "ok"
    assert client.get("/readyz").json()["status"] == "ready"


def test_search_is_bounded() -> None:
    from hedron_docs import PageRecord, SiteManifest

    page = PageRecord("index.md", "/", "Home", "Install docs", (), (), "install docs", "hash")
    manifest = SiteManifest("Docs", "", "", (page,))
    assert search(manifest, "install")[0].path == "/"
    with pytest.raises(ValueError):
        search(manifest, "x" * 201)
    with pytest.raises(ValueError):
        search(manifest, "install", limit=-1)


def test_manifest_rejects_unsafe_routes_and_base_urls() -> None:
    from hedron_docs import PageRecord, SiteManifest

    page = PageRecord("index.md", "/", "Home", "", (), (), "home", "hash")
    for route in ("//evil/", "/../escape/", "/search"):
        with pytest.raises(ValueError):
            SiteManifest("Docs", "", "", (PageRecord("x.md", route, "X", "", (), (), "x", "hash"),))
    with pytest.raises(ValueError):
        SiteManifest("Docs", "", "https://user:pass@example.test", (page,))


def test_manifest_rejects_unsafe_render_nodes() -> None:
    from hedron_docs import DocNode, PageRecord, SiteManifest

    unsafe = DocNode(
        "paragraph", children=(DocNode("link", text="x", attrs=(("href", "javascript:alert(1)"),)),)
    )
    page = PageRecord("index.md", "/", "Home", "", (), (unsafe,), "x", "hash")
    with pytest.raises(ValueError, match="unsafe"):
        SiteManifest("Docs", "", "", (page,))


def test_manifest_node_depth_is_bounded() -> None:
    from hedron_docs import DocNode

    value: dict[str, object] = {"kind": "text"}
    for _ in range(257):
        value = {"kind": "span", "children": [value]}
    with pytest.raises(ValueError, match="nesting"):
        DocNode.from_dict(value)


def test_config_rejects_non_integral_limits(tmp_path: Path) -> None:
    config = tmp_path / "hedron-docs.toml"
    config.write_text("[build]\nmax_nodes = 1.5\n", encoding="utf-8")
    with pytest.raises(DocsError, match="HED-DOCS-0005"):
        load_config(config)


def test_config_rejects_non_string_paths_and_metadata(tmp_path: Path) -> None:
    config = tmp_path / "hedron-docs.toml"
    config.write_text("[site]\ntitle = 42\n", encoding="utf-8")
    with pytest.raises(DocsError, match="HED-DOCS-0005"):
        load_config(config)


def test_import_mkdocs_accepts_exclusion_arrays(tmp_path: Path) -> None:
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "site_name: Example\nexclude_docs: [private/**, draft.md]\n", encoding="utf-8"
    )
    assert import_mkdocs(mkdocs).exclude == ("private/**", "draft.md")


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


def test_import_mkdocs_rebases_docs_dir_for_native_config(tmp_path: Path) -> None:
    from hedron_docs.cli import main

    project = tmp_path / "nested"
    docs = project / "docs"
    docs.mkdir(parents=True)
    mkdocs = project / "mkdocs.yml"
    mkdocs.write_text("site_name: Example\ndocs_dir: docs\n", encoding="utf-8")
    output = tmp_path / "hedron-docs.toml"
    assert main(["import-mkdocs", str(mkdocs), "--output", str(output)]) == 0
    imported = load_config(output)
    assert imported.resolved(root=output.parent).docs_dir == docs.resolve()


def test_deployable_proving_app() -> None:
    repository = Path(__file__).resolve().parents[3]
    app_root = repository / "apps" / "hedron-docs"
    config = load_config(app_root / "hedron-docs.toml")
    manifest = compile_site(config)
    assert len(manifest.pages) == 2
    assert len(manifest.assets) == 1
    client = TestClient(create_docs_app(manifest))
    assert client.get("/").status_code == 200
    assert client.get("/guide/").status_code == 200
    assert client.get(manifest.assets[0].path).status_code == 200
