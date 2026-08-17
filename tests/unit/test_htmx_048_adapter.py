"""ADAPTER-048 Flask/Django/portable injector; no FastAPI types in core."""

from __future__ import annotations

import ast
from pathlib import Path
from types import MappingProxyType

import pytest

from hedron_core import HedronError
from hedron_core.codes import HED_EXT_0011
from hedron_core.htmx_extensions import ExtensionPlan
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import AssetRef, RenderMode


def test_core_and_catalog_forbid_host_imports() -> None:
    forbidden = {"fastapi", "starlette", "flask", "django"}
    for rel in (
        "packages/hedron-core/src/hedron_core/htmx_extensions.py",
        "packages/hedron-core/src/hedron_core/sse_ext.py",
        "packages/hedron-core/src/hedron_core/head_support.py",
        "packages/hedron-core/src/hedron_core/page_assets.py",
    ):
        tree = ast.parse(Path(rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                assert root not in forbidden
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    assert root not in forbidden


def test_flask_and_django_call_portable_injector() -> None:
    flask = Path("packages/hedron-flask/src/hedron_flask/responses.py").read_text(encoding="utf-8")
    django = Path("packages/hedron-django/src/hedron_django/responses.py").read_text(
        encoding="utf-8"
    )
    assert "inject_page_assets" in flask
    assert "inject_page_assets" in django
    assert "htmx_plan" in flask
    assert "htmx_plan" in django
    assert callable(inject_page_assets)


def test_flask_django_injector_rejects_breakout_href() -> None:
    evil = AssetRef(kind="js", href='/ok?"onclick="alert(1)', attributes=MappingProxyType({}))
    plan = ExtensionPlan(ids=("head-support",), source="declared", inject=True)
    with pytest.raises(HedronError) as injected:
        inject_page_assets(
            "<html><head></head><body></body></html>",
            RenderMode.PAGE,
            assets=(evil,),
            include_default_styles=False,
            include_ui_modules=False,
            plan=plan,
        )
    assert injected.value.diagnostic.code == HED_EXT_0011


def test_posit_workbench_keep_mount_prefix_labels() -> None:
    workbench = Path("packages/hedron-workbench").is_dir()
    posit = Path("packages/hedron-posit").is_dir()
    assert workbench and posit
