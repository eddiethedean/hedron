"""ASSET-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core import (
    ApplicationAssetSpec,
    compile_application_asset_plan,
)
from hedron_core.codes import (
    HED_ASSET_0532,
    HED_ASSET_0533,
    HED_ASSET_0536,
)
from hedron_core.registry.asset import AssetMeta, register_asset


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


def test_register_asset_kwargs_accept_depends_on() -> None:
    from hedron_core.registry import reset_registry_for_tests

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
    finally:
        reset_registry_for_tests()
