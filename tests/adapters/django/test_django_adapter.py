"""Adapter tests for hedron-django."""

from __future__ import annotations

import ast
from pathlib import Path

from django.test import Client

from hedron_core.htmx.policy import InteractionPolicy
from hedron_core.rendering import RenderMode
from hedron_django import HedronDjango
from hedron_django.htmx import render_mode_for_request

ROOT = Path(__file__).resolve().parents[3]
DJANGO_SRC = ROOT / "packages" / "hedron-django" / "src" / "hedron_django"
FORBIDDEN = frozenset({"fastapi", "starlette", "hedron"})


def test_page_render(django_client: Client) -> None:
    response = django_client.get("/page/")
    assert response.status_code == 200
    content = response.content.decode()
    assert "<h1" in content
    assert "<html" in content
    assert "htmx.min.js" in content
    assert "/hedron-static/ext/head-support.js" in content
    assert content.index("htmx.min.js") < content.index("/hedron-static/ext/head-support.js")


def test_hedron_static_mount(django_client: Client) -> None:
    response = django_client.get("/hedron-static/htmx.min.js")
    assert response.status_code == 200
    payload = b"".join(response.streaming_content)
    assert len(payload) > 1000


def test_page_static_href_honors_script_prefix(django_client: Client) -> None:
    from django.urls import clear_script_prefix, set_script_prefix

    set_script_prefix("/app/")
    try:
        response = django_client.get("/page/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "/app/hedron-static/htmx.min.js" in content
        assert 'src="/hedron-static/htmx.min.js"' not in content
    finally:
        clear_script_prefix()


def test_fragment_render(django_client: Client) -> None:
    response = django_client.get("/fragment/", HTTP_HX_REQUEST="true")
    assert response.status_code == 200
    content = response.content.decode()
    assert "Fragment body" in content
    assert "<html" not in content


def test_interaction_headers(django_client: Client) -> None:
    response = django_client.get("/interaction/")
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "refreshed"
    assert "Updated" in response.content.decode()


def test_component_vary_header(django_client: Client) -> None:
    response = django_client.get("/fragment/", HTTP_HX_REQUEST="true")
    vary = response.headers.get("Vary", "")
    assert "HX-Request" in vary


def test_csrf_header_name_portable_default() -> None:
    from hedron_django.csrf import (
        DEFAULT_CSRF_HEADER,
        DJANGO_CSRF_HEADER,
        PORTABLE_CSRF_HEADER,
        csrf_header_name,
    )

    assert DEFAULT_CSRF_HEADER == PORTABLE_CSRF_HEADER
    assert DJANGO_CSRF_HEADER == "X-CSRFToken"
    # Without CSRF_HEADER_NAME override, helpers advertise the portable header.
    assert csrf_header_name() in {PORTABLE_CSRF_HEADER, DJANGO_CSRF_HEADER}


def test_oob_authorization(django_client: Client) -> None:
    from hedron_core import Text
    from hedron_core.interaction import (
        FragmentRegion,
        InteractionPolicy,
        InteractionResult,
        OobUpdate,
    )
    from hedron_django.responses import interaction_response

    ok = InteractionResult(
        content=Text("main"),
        oob=(OobUpdate(content=Text("side"), element_id="side"),),
        policy=InteractionPolicy(declared_regions=(FragmentRegion(id="side", selector="#side"),)),
    )
    response = interaction_response(ok)
    assert response.status_code == 200
    assert b"hx-swap-oob" in response.content

    bad = InteractionResult(
        content=Text("main"),
        oob=(OobUpdate(content=Text("evil"), element_id="evil"),),
        policy=InteractionPolicy(declared_regions=(FragmentRegion(id="side", selector="#side"),)),
    )
    denied = interaction_response(bad)
    assert denied.status_code == 403


def test_render_mode_history_restore() -> None:
    assert (
        render_mode_for_request({"HX-Request": "true", "HX-History-Restore-Request": "true"})
        is RenderMode.PAGE
    )


def test_history_restore_without_hx_request_stays_page() -> None:
    """#578: forged HX-History-Restore-Request alone must not select FRAGMENT."""
    policy = InteractionPolicy(history_restore="primary")
    assert (
        render_mode_for_request({"HX-History-Restore-Request": "true"}, policy=policy)
        is RenderMode.PAGE
    )
    assert (
        render_mode_for_request(
            {"HX-Request": "true", "HX-History-Restore-Request": "true"},
            policy=policy,
        )
        is RenderMode.FRAGMENT
    )


def test_render_mode_boosted() -> None:
    assert render_mode_for_request({"HX-Request": "true", "HX-Boosted": "true"}) is RenderMode.PAGE


def test_render_mode_for_request() -> None:
    assert render_mode_for_request({}) is RenderMode.PAGE
    assert render_mode_for_request({"HX-Request": "true"}) is RenderMode.FRAGMENT


def test_queryset_datasource_supported() -> None:
    caps = HedronDjango().capabilities
    qs = next(c for c in caps.capabilities if c.name == "queryset_datasource")
    assert qs.supported is True
    forms = next(c for c in caps.capabilities if c.name == "django_forms")
    assert forms.supported is True


def test_no_fastapi_imports_in_source() -> None:
    found: list[str] = []
    for path in DJANGO_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".", 1)[0]
                    if root in FORBIDDEN:
                        found.append(f"{path.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".", 1)[0]
                if root in FORBIDDEN:
                    found.append(f"{path.name}: from {node.module}")
    assert found == []
