"""W4 manifest, navigation, and routing regressions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hedron_docs import (
    DocsBuildConfig,
    NavigationItem,
    SiteManifest,
    compile_site,
    create_docs_app,
    import_mkdocs,
)


def test_unicode_routes_are_reachable_in_both_url_forms(tmp_path: Path) -> None:
    (tmp_path / "café.md").write_text("# Café\n", encoding="utf-8")
    manifest = compile_site(DocsBuildConfig(docs_dir=tmp_path))
    client = TestClient(create_docs_app(manifest))
    assert client.get("/caf%C3%A9/").status_code == 200
    assert client.get("/café/").status_code == 200


def test_content_hash_covers_serialized_page_content(tmp_path: Path) -> None:
    (tmp_path / "index.md").write_text("# Home\n", encoding="utf-8")
    manifest = compile_site(DocsBuildConfig(docs_dir=tmp_path))
    data = json.loads(manifest.dumps())
    data["pages"][0]["title"] = "Tampered"
    with pytest.raises(ValueError, match="content_hash"):
        SiteManifest.from_dict(data)


def test_mkdocs_import_preserves_metadata_and_root_exclusions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "mkdocs.yml"
    config_path.write_text(
        "site_url: !ENV [DOCS_URL, 'https://docs.example.test']\n"
        "repo_url: https://github.com/acme/docs\n"
        "edit_uri: edit/main/docs/\n"
        "exclude_docs: |\n  /STATUS.md\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DOCS_URL", raising=False)
    config = import_mkdocs(config_path)
    assert config.base_url == "https://docs.example.test"
    assert config.edit_url_template.endswith("/edit/main/docs/{path}")
    assert config.source_url_template.endswith("/blob/main/{path}")
    assert config.exclude == ("/STATUS.md",)


def test_duplicate_navigation_target_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "index.md").write_text("# Home\n", encoding="utf-8")
    config = DocsBuildConfig(
        docs_dir=tmp_path,
        navigation=(NavigationItem("One", "index.md"), NavigationItem("Two", "index.md")),
    )
    with pytest.raises(Exception, match="listed more than once"):
        compile_site(config)


def test_reserved_route_check_is_case_insensitive(tmp_path: Path) -> None:
    (tmp_path / "Search.md").write_text("# Search\n", encoding="utf-8")
    with pytest.raises(Exception, match="route is reserved"):
        compile_site(DocsBuildConfig(docs_dir=tmp_path))


def test_fragment_validation_is_case_sensitive(tmp_path: Path) -> None:
    (tmp_path / "index.md").write_text("# Home\n\n[bad](#HOME)\n", encoding="utf-8")
    with pytest.raises(Exception, match="anchor does not resolve"):
        compile_site(DocsBuildConfig(docs_dir=tmp_path))
