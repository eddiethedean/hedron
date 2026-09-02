from __future__ import annotations

import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hedron import render
from hedron_core.rendering import RenderMode
from hedron_docs import (
    DocsBuildConfig,
    SiteManifest,
    compile_site,
    create_docs_app,
    parse_markdown,
)
from hedron_docs.render import COMPATIBILITY_NODE_REGISTRY, render_document

W3_SOURCE = """# Native *content* {#native #legacy}

Paragraph with **strong**, *emphasis*, `inline`, and [a link](https://example.test).

> A semantic quote.

- one
- two

```python
print("safe")
```

| Name | Value |
| --- | --- |
| alpha | **one** |

!!! warning "Heads up"
    Alert **body**.

=== "Python"
    ```python
    print("tab")
    ```

Read the note[^note].

[^note]: Footnote body.
"""


def test_w3_native_render_semantic_snapshot(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text(W3_SOURCE, encoding="utf-8")
    manifest = compile_site(DocsBuildConfig(docs_dir=docs, output=tmp_path / "site.json"))
    output = render(render_document(manifest.pages[0].nodes), mode=RenderMode.FRAGMENT).html

    # Keep this compact snapshot focused on the public semantic contract rather than renderer
    # implementation whitespace or unrelated Hedron attributes.
    snapshot = {
        "anchors": re.findall(r'<a id="([^"]+)" class="hedron-doc-anchor"', output),
        "semantic_tags": {
            tag: output.count(f"<{tag}")
            for tag in ("h1", "p", "blockquote", "strong", "em", "code", "table", "ul", "ol", "li")
        },
        "native_markers": [
            'data-hedron-code-block="true"',
            'data-hedron-clipboard-copy="true"',
            'data-hedron-responsive="scroll"',
            'data-hedron-fragment-target="true"',
            "hedron-doc-footnotes",
        ],
        "escaped": "print(&quot;safe&quot;)" in output,
        "inline_script": "<script" in output,
    }
    assert snapshot == {
        "anchors": ["native", "legacy"],
        "semantic_tags": {
            "h1": 1,
            "p": 9,
            "blockquote": 1,
            "strong": 4,
            "em": 2,
            "code": 3,
            "table": 1,
            "ul": 1,
            "ol": 1,
            "li": 3,
        },
        "native_markers": [
            'data-hedron-code-block="true"',
            'data-hedron-clipboard-copy="true"',
            'data-hedron-responsive="scroll"',
            'data-hedron-fragment-target="true"',
            "hedron-doc-footnotes",
        ],
        "escaped": True,
        "inline_script": False,
    }
    assert frozenset() == COMPATIBILITY_NODE_REGISTRY


def test_w3_css_is_immutable_and_no_inline_script_dependency(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "index.md").write_text("# Home\n", encoding="utf-8")
    manifest = compile_site(DocsBuildConfig(docs_dir=docs, output=tmp_path / "site.json"))
    client = TestClient(create_docs_app(manifest))

    page = client.get("/")
    assert page.status_code == 200
    assert 'href="/_hedron-docs/docs.css"' in page.text
    assert not re.search(r"<script(?![^>]+\bsrc=)", page.text)
    css = client.get("/_hedron-docs/docs.css")
    assert css.status_code == 200
    assert css.headers["cache-control"] == "public, max-age=31536000, immutable"
    assert css.headers["x-content-type-options"] == "nosniff"
    assert ".hedron-doc-anchor:target" in css.text
    assert ".hedron-table-scroll" in css.text
    assert ".hedron-code-viewer" in css.text


def test_w3_rejects_pre_w3_contracts(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="expected 3"):
        DocsBuildConfig(schema_version=2)
    with pytest.raises(ValueError, match="manifest-3"):
        SiteManifest.from_dict(
            {
                "schema_version": "hedron-docs-manifest-2",
                "site": {"title": "Old"},
                "pages": [],
                "assets": [],
            }
        )


def test_w3_heading_aliases_are_unique_and_safe(tmp_path: Path) -> None:
    nodes = parse_markdown(
        "# Heading {#canonical #legacy}\n\n## Other {#second}\n",
        source_path=tmp_path / "index.md",
    )
    assert nodes[0].attr("id") == "canonical"
    assert nodes[0].attr("aliases") == "legacy"
    assert nodes[1].attr("id") == "second"
