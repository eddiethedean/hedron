"""The visual theme gallery stays renderable in both explicit color modes."""

from __future__ import annotations

import importlib.util
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest
from fastapi.testclient import TestClient


def _load_gallery() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "examples" / "theme-gallery" / "app.py"
    spec = importlib.util.spec_from_file_location("hedron_theme_gallery_test_app", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def gallery_client() -> Iterator[TestClient]:
    module = _load_gallery()
    with TestClient(module.app) as client:
        yield client


@pytest.mark.parametrize("route", ["/", "/settings", "/orders", "/support", "/components"])
@pytest.mark.parametrize("mode", ["light", "dark"])
@pytest.mark.parametrize("theme", ["default", "aurora"])
def test_gallery_route_renders_in_explicit_mode(
    gallery_client: TestClient, route: str, mode: str, theme: str
) -> None:
    response = gallery_client.get(route, params={"mode": mode, "theme": theme})
    assert response.status_code == 200
    assert f'data-theme="{mode}"' in response.text
    assert f'data-hedron-theme="{theme}"' in response.text
    assert 'href="/hedron-static/hedron-default.css"' in response.text
