"""ASSET-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path
from types import MappingProxyType

from hedron_core import (
    ApplicationAssetSpec,
    compile_application_asset_plan,
    ordered_registry_assets,
)
from hedron_core.codes import (
    HED_ASSET_0532,
    HED_ASSET_0533,
    HED_ASSET_0536,
)
from hedron_core.htmx_extensions import ExtensionPlan
from hedron_core.page_assets import inject_page_assets
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.registry.asset import AssetMeta, register_asset
from hedron_core.rendering import AssetRef, RenderMode


def test_asset_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["ASSET-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_asset_meta_accepts_depends_on_and_placement() -> None:
    meta = AssetMeta(
        logical_id="app.css",
        kind="css",
        path="/static/app.css",
        digest="sha256-abc",
        content_type="text/css",
        depends_on=("base.css",),
        placement="after_htmx_core",
    )
    assert meta.depends_on == ("base.css",)
    assert meta.placement == "after_htmx_core"


def test_compile_happy_path_topo_order() -> None:
    plan = compile_application_asset_plan(
        [
            ApplicationAssetSpec(
                logical_id="app",
                kind="js",
                href="/static/app.js",
                depends_on=("vendor",),
                placement="body_end",
                integrity="sha256-dGVzdA==",
            ),
            ApplicationAssetSpec(
                logical_id="vendor",
                kind="js",
                href="/static/vendor.js",
                placement="after_htmx_core",
            ),
            ApplicationAssetSpec(
                logical_id="theme",
                kind="css",
                href="/static/theme.css",
                placement="head",
            ),
        ]
    )
    assert plan.ok
    assert plan.diagnostics == ()
    assert [item.logical_id for item in plan.assets] == ["theme", "vendor", "app"]


def test_compile_missing_dependency() -> None:
    plan = compile_application_asset_plan(
        [
            ApplicationAssetSpec(
                logical_id="app",
                kind="js",
                href="/static/app.js",
                depends_on=("missing",),
            )
        ]
    )
    assert not plan.ok
    assert any(d.code == HED_ASSET_0532 for d in plan.diagnostics)


def test_compile_cycle() -> None:
    plan = compile_application_asset_plan(
        [
            ApplicationAssetSpec(
                logical_id="a",
                kind="js",
                href="/static/a.js",
                depends_on=("b",),
            ),
            ApplicationAssetSpec(
                logical_id="b",
                kind="js",
                href="/static/b.js",
                depends_on=("a",),
            ),
        ]
    )
    assert not plan.ok
    assert any(d.code == HED_ASSET_0533 for d in plan.diagnostics)


def test_compile_rejects_http_cdn() -> None:
    plan = compile_application_asset_plan(
        [
            ApplicationAssetSpec(
                logical_id="cdn",
                kind="js",
                href="https://cdn.example.com/lib.js",
            )
        ]
    )
    assert not plan.ok
    assert any(d.code == HED_ASSET_0536 for d in plan.diagnostics)


def test_compile_rejects_file_scheme() -> None:
    plan = compile_application_asset_plan(
        [
            ApplicationAssetSpec(
                logical_id="local-file",
                kind="js",
                href="file:///tmp/lib.js",
            )
        ]
    )
    assert not plan.ok
    assert any(d.code == HED_ASSET_0536 for d in plan.diagnostics)


def test_register_asset_stores_depends_on_and_placement() -> None:
    reset_registry_for_tests()
    try:
        register_asset(
            logical_id="unit-asset-053",
            kind="css",
            path="/static/unit.css",
            digest="sha256-unit",
            content_type="text/css",
            depends_on=("other",),
            placement="body_end",
        )
        stored = {meta.logical_id: meta for meta in get_registry().assets()}
        assert stored["unit-asset-053"].depends_on == ("other",)
        assert stored["unit-asset-053"].placement == "body_end"
    finally:
        reset_registry_for_tests()


def test_inject_honors_body_end_vs_head_placement() -> None:
    reset_registry_for_tests()
    try:
        register_asset(
            logical_id="head-theme",
            kind="css",
            path="/static/theme.css",
            digest="sha256-theme",
            content_type="text/css",
            placement="head",
        )
        register_asset(
            logical_id="boot",
            kind="js",
            path="/static/boot.js",
            digest="sha256-boot",
            content_type="text/javascript",
            placement="body_end",
        )
        html = inject_page_assets(
            "<html><head></head><body></body></html>",
            RenderMode.PAGE,
            include_default_styles=False,
            include_ui_modules=False,
            plan=ExtensionPlan(ids=(), source="declared", inject=False),
        )
        head, _, body = html.partition("</head>")
        assert "/static/theme.css" in head
        assert "/static/boot.js" not in head
        assert "/static/boot.js" in body
    finally:
        reset_registry_for_tests()


def test_inject_honors_depends_on_order() -> None:
    reset_registry_for_tests()
    try:
        register_asset(
            logical_id="app",
            kind="js",
            path="/static/app.js",
            digest="sha256-app",
            content_type="text/javascript",
            depends_on=("vendor",),
            placement="body_end",
        )
        register_asset(
            logical_id="vendor",
            kind="js",
            path="/static/vendor.js",
            digest="sha256-vendor",
            content_type="text/javascript",
            placement="body_end",
        )
        assert [s.logical_id for s in ordered_registry_assets()] == ["vendor", "app"]
        html = inject_page_assets(
            "<html><head></head><body></body></html>",
            RenderMode.PAGE,
            include_default_styles=False,
            include_ui_modules=False,
            plan=ExtensionPlan(ids=(), source="declared", inject=False),
        )
        assert html.index("/static/vendor.js") < html.index("/static/app.js")
    finally:
        reset_registry_for_tests()


def test_inject_emits_integrity_attribute() -> None:
    asset = AssetRef(
        kind="js",
        href="/static/sri.js",
        attributes=MappingProxyType(
            {"integrity": "sha256-dGVzdA==", "crossorigin": "anonymous"}
        ),
    )
    html = inject_page_assets(
        "<html><head></head><body></body></html>",
        RenderMode.PAGE,
        assets=(asset,),
        include_default_styles=False,
        include_ui_modules=False,
        plan=ExtensionPlan(ids=(), source="declared", inject=False),
    )
    assert 'integrity="sha256-dGVzdA=="' in html
    assert 'crossorigin="anonymous"' in html


def test_inject_no_double_script_with_head_support() -> None:
    asset = AssetRef(kind="js", href="/static/app.js", attributes=MappingProxyType({}))
    html = inject_page_assets(
        "<html><head></head><body></body></html>",
        RenderMode.PAGE,
        assets=(asset,),
        include_default_styles=False,
        include_ui_modules=False,
        plan=ExtensionPlan(ids=("head-support",), source="declared", inject=True),
    )
    assert html.count("/static/app.js") == 1
    assert 'src="/static/app.js"' in html


def test_inject_omits_invalid_sri() -> None:
    asset = AssetRef(
        kind="js",
        href="/static/bad.js",
        attributes=MappingProxyType({"integrity": "not-a-digest"}),
    )
    html = inject_page_assets(
        "<html><head></head><body></body></html>",
        RenderMode.PAGE,
        assets=(asset,),
        include_default_styles=False,
        include_ui_modules=False,
        plan=ExtensionPlan(ids=(), source="declared", inject=False),
    )
    assert "/static/bad.js" not in html
    assert "not-a-digest" not in html


def test_inject_relative_href_with_head_support() -> None:
    asset = AssetRef(kind="js", href="app.js", attributes=MappingProxyType({}))
    html = inject_page_assets(
        "<html><head></head><body></body></html>",
        RenderMode.PAGE,
        assets=(asset,),
        include_default_styles=False,
        include_ui_modules=False,
        plan=ExtensionPlan(ids=("head-support",), source="declared", inject=True),
    )
    assert 'src="app.js"' in html
