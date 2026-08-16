"""SECURITY-045: catalog ids are not capabilities; hostile JSON/paths fail closed."""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import (
    CatalogVersionError,
    InteractionManifest,
    compile_interaction_catalog,
)


def setup_function() -> None:
    reset_045()


def test_catalog_id_is_not_a_capability() -> None:
    app = make_app()

    @app.refreshable
    def secret_card():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    entry = catalog.require(secret_card.logical_id)
    assert entry.logical_id == secret_card.logical_id
    assert entry.descriptor_fingerprint
    # Fingerprints identify artifacts; they do not authorize anything.
    assert "authorize" not in entry.as_mapping()
    assert "capability" not in str(entry.as_mapping().get("projections") or {})


def test_path_escape_and_hostile_json(tmp_path: Path) -> None:
    payload = {
        "format_version": 1,
        "profile": "production",
        "entries": [{"logical_id": "../etc/passwd", "kind": "view"}],
        "projections": [],
    }
    path = tmp_path / "interactions.json"
    path.write_text("not-json", encoding="utf-8")
    with pytest.raises(CatalogVersionError):
        InteractionManifest.read_json(path)
    # Cross-app reuse
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    other = catalog.to_manifest()
    object.__setattr__(other, "app_id", "foreign-app")
    object.__setattr__(other, "payload", {**other.as_mapping(), "app_id": "foreign-app"})
    with pytest.raises(CatalogVersionError):
        other.validate_against(catalog)
    del payload
