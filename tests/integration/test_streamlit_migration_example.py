"""Smoke and outcome tests for the public Streamlit migration example."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi.testclient import TestClient

_APP_PATH = Path(__file__).resolve().parents[2] / "examples" / "streamlit-migration" / "app.py"
_SPEC = importlib.util.spec_from_file_location("streamlit_migration_example", _APP_PATH)
assert _SPEC and _SPEC.loader
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["streamlit_migration_example"] = _MOD
_SPEC.loader.exec_module(_MOD)


def test_default_dashboard_totals() -> None:
    with TestClient(_MOD.app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "$22,600" in response.text
    assert ">213<" in response.text


def test_query_filters_are_typed_and_reproducible() -> None:
    with TestClient(_MOD.app) as client:
        response = client.get("/?region=North&minimum=4000")

    assert response.status_code == 200
    assert "$8,700" in response.text
    assert "$4,100" in response.text
    assert "$4,600" in response.text
    assert "$3,600" not in response.text


def test_invalid_filter_is_rejected() -> None:
    with TestClient(_MOD.app) as client:
        response = client.get("/?minimum=9000")

    assert response.status_code == 422
