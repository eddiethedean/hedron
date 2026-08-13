"""COMPOSE-035: reference-app isolation and Supported combination smoke."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hedron import Hedron, Text

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def minimal_client():
    app = Hedron(title="compose-035", explorer="off", session_secret="compose-035-secret")

    @app.page("/")
    def home():
        return Text("ok")

    with TestClient(app) as client:
        yield client


def test_reference_style_app_health_and_headers(minimal_client: TestClient) -> None:
    response = minimal_client.get("/")
    assert response.status_code == 200
    assert "content-type" in {k.lower() for k in response.headers.keys()}


@pytest.mark.parametrize(
    "module_name",
    [
        "hedron_data",
        "hedron_charts",
        "hedron_mcp",
        "hedron_gradio",
        "hedron_posit",
        "hedron_workbench",
        "hedron_jinja",
        "hedron_extras",
    ],
)
def test_production_grade_optional_packages_import_in_isolation(module_name: str) -> None:
    mod = import_module(module_name)
    assert getattr(mod, "__name__", None) == module_name


def test_supported_combination_imports() -> None:
    """One Supported combination: data + charts + jinja available together."""
    import hedron_charts  # noqa: F401
    import hedron_data  # noqa: F401
    import hedron_jinja  # noqa: F401


def test_reference_app_source_and_compose_exist() -> None:
    assert (ROOT / "examples" / "reference-app" / "app.py").is_file()
    assert (ROOT / "examples" / "reference-app" / "docker-compose.yml").is_file()
    assert (ROOT / "docs" / "api" / "PRODUCTION_ARCHETYPE.md").is_file()
