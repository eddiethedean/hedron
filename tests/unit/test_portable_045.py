"""PORTABLE-045: fixture JSON and native canonical-byte parity."""

from __future__ import annotations

import json
from pathlib import Path

from tests.unit._helpers_045 import make_app, reset_045

from hedron import Text
from hedron_core.catalog import compile_interaction_catalog
from hedron_core.manifests import canonical_json

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "conformance" / "fixtures" / "interactions_045.json"


def setup_function() -> None:
    reset_045()


def test_fixture_json_is_canonical_and_forbidden_key_free() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert payload["format_version"] == 1
    encoded = canonical_json(payload)
    assert "values" not in encoded
    assert "callbacks" not in encoded
    assert payload["entries"][0]["logical_id"] == "status"


def test_python_manifest_matches_fixture_shape() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    manifest = compile_interaction_catalog(app_id=app.hedron_app_id).to_manifest()
    payload = manifest.as_mapping()
    assert set(payload) >= {"format_version", "fingerprint", "entries", "projections", "profile"}
    second = compile_interaction_catalog(app_id=app.hedron_app_id).to_manifest().as_mapping()
    assert canonical_json(payload) == canonical_json(second)
