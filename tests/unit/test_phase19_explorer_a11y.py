"""Phase 0.19 EXPLORER-019."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron
from hedron_core import reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_explorer_a11y_workspace_surface() -> None:
    app = Hedron(
        title="ex",
        security="standard",
        explorer="development",
        session_secret="test-secret",
    )
    client = TestClient(app)
    resp = client.get("/hedron-explorer/a11y")
    assert resp.status_code == 200
    text = resp.text
    assert "Accessibility review workspace" in text
    assert "Standards profile" in text
    assert "Component contracts" in text
    assert "Structure outline" in text
    assert "Reviewed" in text
    assert "Review modes" in text
    assert "ATAG authoring assistance" in text
    assert "empty scans never summarize as accessible" in text.lower() or "Empty scans" in text
    assert ">yes<" in text  # curated reviewed contracts seeded
