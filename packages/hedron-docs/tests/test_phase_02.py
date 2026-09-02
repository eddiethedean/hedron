from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hedron_docs import (
    DocNode,
    DocsBuildConfig,
    DocsError,
    NavigationItem,
    SiteManifest,
    compile_site,
    create_docs_app,
    import_mkdocs,
    load_config,
    parse_markdown,
)

REQUIRED_SOURCE = """# Héllo *world* {#welcome}

Paragraph with **strong**, `code`, [link](guide.md), and ![logo](logo.svg).

3. first
4. second

> Quoted text.

Term
: Definition.

| Name | Value |
|---|---|
| alpha | one |

!!! warning "Careful"
    Alert body.

???+ note "More"
    Detail body.

=== "Python"
    ```python
    print("hello")
    ```
=== "Shell"
    ```sh
    echo hello
    ```

Read the note[^note].

[^note]: Footnote body.

::: hedron.Hedron
    show_source: false

::: demo form-validation
"""


def _walk(nodes: tuple[DocNode, ...]) -> list[DocNode]:
    result: list[DocNode] = []
    pending = list(reversed(nodes))
    while pending:
        node = pending.pop()
        result.append(node)
        pending.extend(reversed(node.children))
    return result


def test_phase_02_required_syntax_has_explicit_source_located_nodes(tmp_path: Path) -> None:
    source_path = tmp_path / "index.md"
    nodes = parse_markdown(REQUIRED_SOURCE, source_path=source_path, source_name="index.md")
    all_nodes = _walk(nodes)
    kinds = {node.kind for node in all_nodes}
    assert {
        "heading",
        "paragraph",
        "strong",
        "inline-code",
        "link",
        "image",
        "list",
        "quote",
        "definition-list",
        "table",
        "alert",
        "details",
        "tabs",
        "footnote-ref",
        "footnote",
        "api-directive",
        "demo-directive",
    } <= kinds
    assert all(node.source == "index.md" and node.span is not None for node in all_nodes)
    assert all(node.span_id.startswith("span-") for node in all_nodes)
    assert nodes == parse_markdown(REQUIRED_SOURCE, source_path=source_path, source_name="index.md")
    assert tuple(DocNode.from_dict(node.to_dict()) for node in nodes) == nodes
    heading = nodes[0]
    assert (heading.text, heading.attr("id"), heading.line, heading.column) == (
        "Héllo world",
        "welcome",
        1,
        1,
    )
    ordered = next(node for node in all_nodes if node.kind == "list")
    assert ordered.attr("start") == "3"


def test_phase_02_extensions_inside_fences_are_code_not_directives(tmp_path: Path) -> None:
    source = '```text\n!!! warning\n::: os.system\n=== "Tab"\n```\n'
    nodes = parse_markdown(source, source_path=tmp_path / "code.md")
    assert len(nodes) == 1
    assert nodes[0].kind == "code"
    assert "os.system" in nodes[0].text


@pytest.mark.parametrize(
    ("source", "kwargs", "code"),
    [
        ("abcdef", {"max_source_bytes": 5}, "HED-DOCS-0102"),
        ("one two three", {"max_nodes": 1}, "HED-DOCS-0101"),
        ("> > > nested", {"max_depth": 2}, "HED-DOCS-0103"),
        ("| A | B |\n|---|---|\n| 1 | 2 |\n", {"max_table_cells": 3}, "HED-DOCS-0104"),
        ("```\n1234\n```", {"max_code_block_bytes": 3}, "HED-DOCS-0105"),
        ("```\na\n```\n\n```\nb\n```", {"max_code_blocks": 1}, "HED-DOCS-0105"),
        ("::: hedron.Hedron\n\n::: demo sample", {"max_directives": 1}, "HED-DOCS-0106"),
    ],
)
def test_phase_02_parser_budgets_are_fail_closed(
    tmp_path: Path, source: str, kwargs: dict[str, int], code: str
) -> None:
    with pytest.raises(DocsError) as caught:
        parse_markdown(
            source,
            source_path=tmp_path / "bounded.md",
            **kwargs,  # pyright: ignore[reportArgumentType]
        )
    diagnostic = caught.value.diagnostic
    assert diagnostic.code == code
    assert diagnostic.title
    assert diagnostic.explanation
    assert diagnostic.remediation
    assert diagnostic.line is not None
    assert diagnostic.column is not None


@pytest.mark.parametrize(
    "source",
    [
        "<script>alert(1)</script>",
        "Text <img src=x onerror=alert(1)>",
        "!!! warning",
        "=== no-quoted-label",
        "::: os.system()",
        "::: demo ../escape",
        "[link](guide.md){.unsafe-class}",
    ],
)
def test_phase_02_unsafe_or_malformed_syntax_is_diagnostic(tmp_path: Path, source: str) -> None:
    with pytest.raises(DocsError) as caught:
        parse_markdown(source, source_path=tmp_path / "unsafe.md")
    assert caught.value.diagnostic.code in {
        "HED-DOCS-0100",
        "HED-DOCS-0107",
        "HED-DOCS-0108",
    }
    assert caught.value.diagnostic.to_dict()["remediation"]


def test_phase_02_config_schema_and_navigation_are_strict(tmp_path: Path) -> None:
    config_path = tmp_path / "hedron-docs.toml"
    config_path.write_text(
        """schema_version = 2
[site]
title = "Docs"
navigation = [
  { title = "Home", path = "index.md" },
  { title = "Guides", children = [{ title = "Start", path = "guides/start.md" }] },
]
[build]
max_depth = 12
max_table_cells = 20
max_code_blocks = 3
max_code_block_bytes = 1000
max_directives = 4
""",
        encoding="utf-8",
    )
    config = load_config(config_path)
    assert config.schema_version == 2
    assert config.max_depth == 12
    assert config.navigation == (
        NavigationItem("Home", "index.md"),
        NavigationItem("Guides", children=(NavigationItem("Start", "guides/start.md"),)),
    )

    config_path.write_text("schema_version = 1\n", encoding="utf-8")
    with pytest.raises(DocsError, match="unsupported configuration schema"):
        load_config(config_path)
    config_path.write_text('[site]\ntitle = "unversioned"\n', encoding="utf-8")
    with pytest.raises(DocsError, match="configuration integer value is invalid"):
        load_config(config_path)


def test_phase_02_mkdocs_navigation_import_is_bounded_and_normalized(tmp_path: Path) -> None:
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        """site_name: Example
docs_dir: docs
nav:
  - Home: index.md
  - Guides:
      - Start: guides/start.md
      - Plain: guides/plain.md
exclude_docs:
  - private/**
""",
        encoding="utf-8",
    )
    config = import_mkdocs(mkdocs)
    assert config.navigation[0] == NavigationItem("Home", "index.md")
    assert config.navigation[1].children[1] == NavigationItem("Plain", "guides/plain.md")
    assert config.exclude == ("private/**",)

    mkdocs.write_text("nav:\n  - Escape: ../secret.md\n", encoding="utf-8")
    with pytest.raises(DocsError, match="dot segment"):
        import_mkdocs(mkdocs)


def test_phase_02_manifest_is_a_clean_schema_break(tmp_path: Path) -> None:
    old: dict[str, object] = {
        "schema_version": "hedron-docs-manifest-1",
        "site": {"title": "Old"},
        "pages": [],
        "assets": [],
    }
    with pytest.raises(ValueError, match="hedron-docs-manifest-2"):
        SiteManifest.from_dict(old)

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(
        '# Home\n\nText[^1].\n\n[^1]: Note.\n\n??? note "Details"\n    More.\n',
        encoding="utf-8",
    )
    manifest = compile_site(DocsBuildConfig(docs_dir=docs, output=tmp_path / "site.json"))
    serialized = json.loads(manifest.dumps())
    assert serialized["schema_version"] == "hedron-docs-manifest-2"
    assert serialized["compiler_version"] == "0.2.0"
    assert serialized["pages"][0]["nodes"][0]["span"]["source"] == "index.md"
    response = TestClient(create_docs_app(manifest)).get("/")
    assert response.status_code == 200
    assert "Footnotes" in response.text
    assert "Details" in response.text
