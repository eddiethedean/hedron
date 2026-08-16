"""Portable catalog/manifest fixture checks (Node/Java JSON-only consumers)."""

from __future__ import annotations

import json
from pathlib import Path

from hedron_core.manifests import canonical_json

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "interactions_045.json"


def test_conformance_catalog_fixture() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert payload["format_version"] == 1
    assert payload["profile"] == "conformance"
    assert payload["entries"][0]["kind"] in {"view", "command"}
    dumped = canonical_json(payload)
    assert "values" not in dumped
    assert "defaults" not in dumped
    roundtrip = json.loads(dumped)
    assert roundtrip["entries"][0]["logical_id"] == "status"
