"""Adapter tests for hedron-flask."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from flask.testing import FlaskClient

from hedron_core import Heading, Page, Text
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderMode
from hedron_flask import HedronFlask, component_response, interaction_response
from hedron_flask.htmx import render_mode_for_request

ROOT = Path(__file__).resolve().parents[3]
FLASK_SRC = ROOT / "packages" / "hedron-flask" / "src" / "hedron_flask"
FORBIDDEN = frozenset({"fastapi", "starlette", "hedron"})


@pytest.fixture
def client() -> FlaskClient:
    app = HedronFlask(__name__).flask

    @app.get("/page")
    def page():
        return component_response(
            Page(Heading("Hello", level=1), title="Test"),
            mode=RenderMode.PAGE,
        )

    @app.get("/fragment")
    def fragment():
        return component_response(Text("Fragment body"), mode=RenderMode.FRAGMENT)

    @app.get("/interaction")
    def interaction():
        return interaction_response(
            InteractionResult(
                content=Text("Updated"),
                trigger="refreshed",
                explanation="test",
            )
        )

    return app.test_client()


def test_page_render(client: FlaskClient) -> None:
    response = client.get("/page")
    assert response.status_code == 200
    assert "<h1" in response.get_data(as_text=True)
    assert "<html" in response.get_data(as_text=True)


def test_fragment_render(client: FlaskClient) -> None:
    response = client.get("/fragment", headers={"HX-Request": "true"})
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Fragment body" in body
    assert "<html" not in body


def test_interaction_headers(client: FlaskClient) -> None:
    response = client.get("/interaction")
    assert response.status_code == 200
    assert response.headers.get("HX-Trigger") == "refreshed"
    assert "Updated" in response.get_data(as_text=True)


def test_render_mode_for_request() -> None:
    assert render_mode_for_request({}) is RenderMode.PAGE
    assert render_mode_for_request({"HX-Request": "true"}) is RenderMode.FRAGMENT
    assert (
        render_mode_for_request({"HX-Request": "true", "HX-History-Restore-Request": "true"})
        is RenderMode.PAGE
    )


def test_no_fastapi_imports_in_source() -> None:
    found: list[str] = []
    for path in FLASK_SRC.rglob("*.py"):
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
