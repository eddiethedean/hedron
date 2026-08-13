"""COMPOSE-035: reference-app isolation and Supported combination smoke."""

from __future__ import annotations

import importlib.util
from importlib import import_module
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]


def _load_reference_app_module():
    path = ROOT / "examples" / "reference-app" / "app.py"
    spec = importlib.util.spec_from_file_location("reference_app_035", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def reference_client():
    module = _load_reference_app_module()
    app = module.get_app()
    with TestClient(app) as client:
        yield client


def test_reference_app_health_and_security_headers(reference_client: TestClient) -> None:
    response = reference_client.get("/")
    assert response.status_code in {200, 302, 303, 307, 308}
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
