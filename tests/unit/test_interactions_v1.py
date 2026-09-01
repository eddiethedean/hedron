"""Canonical interaction catalog and static-inspection contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hedron import Hedron, Text
from hedron.interactions import (
    app_interactions,
    emit_interactions_manifest,
    inspect_interactions_static,
    seal_app_catalog,
    validate_production_interactions,
)
from hedron_core.diagnostics import HedronError


def _app() -> Hedron:
    return Hedron(
        title="Interactions v1",
        security="development",
        explorer="off",
        session_secret="interactions-v1-test-secret",
    )


def test_static_inspection_recognizes_v1_view_and_action(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "from hedron import Hedron\n"
        "app = Hedron()\n"
        "@app.view('/status')\n"
        "async def status(): pass\n"
        "@app.action('/save')\n"
        "def save(): pass\n"
        "@app.page('/')\n"
        "def home(): pass\n",
        encoding="utf-8",
    )

    payload = inspect_interactions_static(tmp_path)
    entries = {item["logical_id"]: item for item in payload["entries"]}
    assert entries["status"]["kind"] == "view"
    assert entries["save"]["kind"] == "command"
    assert "home" not in entries


def test_static_inspection_ignores_hidden_invalid_and_unrelated_sources(tmp_path: Path) -> None:
    hidden = tmp_path / ".generated"
    hidden.mkdir()
    (hidden / "hidden.py").write_text("@app.view('/hidden')\ndef hidden(): pass\n")
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "ordinary.py").write_text("def helper(): pass\n", encoding="utf-8")

    payload = inspect_interactions_static(tmp_path)
    assert payload["entries"] == []
    assert payload["provenance"] == {"mode": "static-source", "unknown": True}


def test_app_catalog_cache_seal_and_manifest_round_trip(tmp_path: Path) -> None:
    app = _app()

    @app.view("/status")
    def status() -> object:
        return Text("ready")

    compiled = app_interactions(app)
    assert compiled.require(status.logical_id).kind == "view"
    sealed = seal_app_catalog(app, profile="development")
    assert app_interactions(app, sealed=True) is sealed

    manifest_path = emit_interactions_manifest(
        tmp_path,
        app=app,
        profile="development",
    )
    loaded = validate_production_interactions(tmp_path, sealed)
    assert loaded is not None
    assert manifest_path == tmp_path / "interactions.json"

    static_payload = inspect_interactions_static(tmp_path, manifest=manifest_path)
    assert static_payload["provenance"]["mode"] == "static-manifest"
    assert static_payload["provenance"]["unknown"] is False


def test_production_validation_requires_manifest_only_for_nonempty_catalog(tmp_path: Path) -> None:
    empty_app = _app()
    empty = app_interactions(empty_app)
    assert validate_production_interactions(tmp_path, empty) is None

    app = _app()

    @app.action("/save")
    def save() -> object:
        return Text("saved")

    catalog = app_interactions(app)
    with pytest.raises(HedronError, match="manifest missing"):
        validate_production_interactions(tmp_path, catalog)


def test_static_manifest_rejects_tampered_digest(tmp_path: Path) -> None:
    app = _app()

    @app.action("/save")
    def save() -> object:
        return Text("saved")

    manifest = emit_interactions_manifest(
        tmp_path,
        app=app,
        profile="development",
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["entries"] = []
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises((HedronError, ValueError)):
        inspect_interactions_static(tmp_path, manifest=manifest)
