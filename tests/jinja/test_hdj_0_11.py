"""HDJ 0.11 dynamic manifests, foreign namespaces, CSP reconciliation."""

from __future__ import annotations

import pytest

from hedron_core import HedronError
from hedron_jinja import (
    DynamicDependency,
    DynamicDependencyManifest,
    ForeignNamespace,
    build_production_inventory,
    reconcile_csp,
)
from hedron_jinja.source import parse_hdj_source


def test_dynamic_dependency_requires_fingerprint() -> None:
    dep = DynamicDependency.from_bytes("app:widget", "widget.hdj", b"<div></div>")
    manifest = DynamicDependencyManifest(dependencies=(dep,))
    assert manifest.require_bound("app:widget").digest == dep.digest
    with pytest.raises(HedronError):
        manifest.require_bound("app:missing")


def test_foreign_namespace_shadow() -> None:
    manifest = DynamicDependencyManifest(
        foreign_namespaces=(ForeignNamespace(name="shared", root="/a/shared"),)
    )
    with pytest.raises(HedronError):
        manifest.prevent_shadow("shared", package_root="/b/shared")
    manifest.prevent_shadow("shared", package_root="/a/shared")


def test_reconcile_csp_fails_closed() -> None:
    mismatches = reconcile_csp(
        "default-src 'self'; script-src 'self'",
        required_capabilities=["htmx.eval"],
        source_name="page.hdj",
    )
    assert mismatches
    assert "htmx.eval" in mismatches[0]


def test_production_inventory() -> None:
    dep = DynamicDependency.from_bytes("app:a", "a.hdj", b"x")
    manifest = DynamicDependencyManifest(dependencies=(dep,))
    inv = build_production_inventory(
        template_reports=[{"name": "a.hdj", "kind": "page"}],
        manifest=manifest,
        capabilities=["web.html"],
    )
    assert inv.dynamic_manifest_fingerprint == manifest.fingerprint()
    assert inv.as_dict()["capabilities"] == ["web.html"]


def test_prologue_accepts_dynamic_and_foreign_features() -> None:
    source = """\
---hdj
version = 1
kind = "page"
profile = "custom"
features = ["jinja.dynamic-dependencies", "jinja.foreign"]
---
<html><body>ok</body></html>
"""
    parsed = parse_hdj_source("demo.hdj", source)
    assert "jinja.dynamic-dependencies" in parsed.declaration.declared_features
    assert "jinja.foreign" in parsed.declaration.declared_features
    assert "ok" in parsed.body
