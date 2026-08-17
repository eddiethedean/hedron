"""EXTENSION-048 closed catalog, declaration, HDJ projection."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from tests.unit._helpers_048 import injected_page, render_page

from hedron_core import HedronError
from hedron_core.builtins import Page, Text
from hedron_core.codes import HED_EXT_0002, HED_EXT_0003, HED_EXT_0004, HED_EXT_0009
from hedron_core.htmx_extensions import (
    ExtensionSet,
    HtmxExtension,
    catalog_facts,
    known_extensions,
    parse_htmx_extensions,
)
from hedron_jinja import register_htmx_catalog


def test_closed_public_ids_and_asset_names() -> None:
    names = {ext.name: ext for ext in known_extensions()}
    assert names["htmx-ext-sse"].public_id == "sse"
    assert names["htmx-ext-head-support"].public_id == "head-support"
    assert names["htmx-ext-preload"].public_id == "preload"
    assert HtmxExtension.SSE == "sse"
    facts = catalog_facts()
    assert facts["new_catalog_kind"] is False
    assert facts["feature_bundle_executor"] is False
    assert facts["fourth_fingerprint_authority"] is False
    assert facts["hx_ext_never_installs"] is True
    assert "morph" not in {item["public_id"] for item in facts["extensions"]}


def test_extension_set_unset_empty_declared() -> None:
    assert parse_htmx_extensions(None).is_unset
    assert parse_htmx_extensions(()).is_empty
    assert parse_htmx_extensions(ExtensionSet.empty()).is_empty
    declared = parse_htmx_extensions({"sse"})
    assert declared.public_ids == ("sse",)
    assert ExtensionSet.of(["head-support", "sse"]).public_ids[0] == "head-support"


def test_unknown_and_cdn_ids_fail_closed() -> None:
    with pytest.raises(HedronError) as unknown:
        parse_htmx_extensions(["response-targets"])
    assert unknown.value.diagnostic.code == HED_EXT_0002
    with pytest.raises(HedronError) as cdn:
        parse_htmx_extensions(["https://cdn.example/ext.js"])
    assert cdn.value.diagnostic.code == HED_EXT_0009
    with pytest.raises(HedronError) as morph:
        parse_htmx_extensions(["morph"])
    assert morph.value.diagnostic.code == HED_EXT_0003


def test_page_unset_empty_and_declared() -> None:
    html, result = injected_page(Text("ok"))
    assert "/hedron-static/ext/sse.js" in html
    assert "/hedron-static/ext/head-support.js" in html
    assert "preload.js" not in html
    assert result.htmx_plan.source == "compat-default"  # type: ignore[union-attr]
    assert any(d.code == "HED-EXT-0001" for d in result.diagnostics)
    assert 'hx-ext="head-support,sse"' in html

    html_empty, empty = injected_page(Text("ok"), htmx_extensions=())
    assert empty.htmx_plan.source == "opt-out"  # type: ignore[union-attr]
    assert "sse.js" not in html_empty
    assert "head-support.js" not in html_empty
    assert "preload.js" not in html_empty
    assert "hx-ext=" not in html_empty

    html_sse, declared = injected_page(Text("ok"), htmx_extensions={"sse"})
    assert declared.htmx_plan.source == "declared"  # type: ignore[union-attr]
    assert "sse.js" in html_sse
    assert "head-support.js" not in html_sse
    assert 'hx-ext="sse"' in html_sse


def test_opt_out_plus_requirement_fails() -> None:
    from hedron_core.security import SafeUrl, UrlPurpose
    from hedron_core.sse_ext import SseRegion

    page = Page(
        SseRegion(Text("live"), connect=SafeUrl.parse("/events", purpose=UrlPurpose.NAVIGATION)),
        title="x",
        htmx_extensions=(),
    )
    with pytest.raises(HedronError) as exc:
        render_page(page)
    assert exc.value.diagnostic.code == HED_EXT_0004


def test_hdj_projection_uses_public_ids_without_auto_install() -> None:
    registry = register_htmx_catalog()
    evidence = registry.require("sse")
    assert evidence.extension_id == "sse"
    assert evidence.kind == "htmx"
    src = Path("packages/hedron-jinja/src/hedron_jinja/instrumentation.py").read_text(
        encoding="utf-8"
    )
    assert "HED-JINJA-0030" in src
    tree = ast.parse(Path("packages/hedron-core/src/hedron_core/htmx_extensions.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "fastapi" not in node.module
            assert "flask" not in node.module
            assert "django" not in node.module
