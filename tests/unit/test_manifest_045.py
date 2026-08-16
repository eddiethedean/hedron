"""MANIFEST-045: redacted interactions.json, atomic write, profiles, adversarial JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import (
    CatalogVersionError,
    InteractionManifest,
    catalog_fingerprint,
    compile_interaction_catalog,
)
from hedron_core.codes import HED_CATALOG_0001, HED_CATALOG_0007


def setup_function() -> None:
    reset_045()


def test_manifest_fingerprint_and_atomic_write(tmp_path: Path) -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    manifest = catalog.to_manifest(profile="production")
    path = tmp_path / "interactions.json"
    manifest.write_json(path)
    loaded = InteractionManifest.read_json(path)
    assert loaded.fingerprint == manifest.fingerprint
    loaded.validate_against(catalog)
    text = path.read_text(encoding="utf-8")
    assert "values" not in text
    assert "defaults" not in text
    first = path.read_bytes()
    manifest.write_json(path)
    assert path.read_bytes() == first


def test_production_profile_strips_source_paths() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    catalog = catalog.__class__(
        schema_version=catalog.schema_version,
        app_id=catalog.app_id,
        entries=catalog.entries,
        catalog_projections=catalog.catalog_projections,
        profile="development",
        provenance={"source_path": "app.py", "app_id": app.hedron_app_id},
    )
    development = catalog.to_manifest(profile="development").as_mapping()
    production = catalog.to_manifest(profile="production").as_mapping()
    assert (development.get("provenance") or {}).get("source_path") == "app.py"
    assert "source_path" not in (production.get("provenance") or {})


def test_duplicate_json_keys_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "interactions.json"
    path.write_text(
        '{"format_version":1,"format_version":2,"profile":"production","entries":[],"projections":[]}',
        encoding="utf-8",
    )
    with pytest.raises(CatalogVersionError) as caught:
        InteractionManifest.read_json(path)
    assert caught.value.diagnostic.code == HED_CATALOG_0007


def test_truncated_json_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "interactions.json"
    path.write_text('{"format_version":1,"profile":"production"', encoding="utf-8")
    with pytest.raises(CatalogVersionError) as caught:
        InteractionManifest.read_json(path)
    assert caught.value.diagnostic.code == HED_CATALOG_0007


def test_forbidden_keys_absent_from_production_payload() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    dumped = json.dumps(
        compile_interaction_catalog(app_id=app.hedron_app_id).to_manifest().as_mapping()
    )
    for key in ("values", "defaults", "examples", "callbacks", "credentials"):
        assert f'"{key}"' not in dumped


def test_stale_fingerprint_fails_closed(tmp_path: Path) -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    catalog = compile_interaction_catalog(app_id=app.hedron_app_id)
    path = tmp_path / "interactions.json"
    catalog.to_manifest().write_json(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["catalog_fingerprint"] = "0" * 32
    body = {key: value for key, value in payload.items() if key != "fingerprint"}
    payload["fingerprint"] = catalog_fingerprint(body)
    path.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    loaded = InteractionManifest.read_json(path)
    with pytest.raises(CatalogVersionError) as caught:
        loaded.validate_against(catalog)
    assert caught.value.diagnostic.code == HED_CATALOG_0001
