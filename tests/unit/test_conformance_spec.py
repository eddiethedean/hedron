"""SPEC-014: language-neutral fixture schema."""

from __future__ import annotations

from hedron_conformance.schema import (
    CONTRACT_VERSION,
    FIXTURE_VERSION,
    Capability,
    ConformanceFixture,
    fixture_schema_dict,
)


def test_fixture_schema_exports_required_keys() -> None:
    schema = fixture_schema_dict()
    assert "properties" in schema
    props = schema["properties"]
    for key in ("id", "fixture_version", "contract_version", "capability", "input", "expected"):
        assert key in props


def test_contract_and_fixture_versions() -> None:
    assert FIXTURE_VERSION == "1.0.0"
    assert CONTRACT_VERSION == "hedron-portable-1"
    assert Capability.ESCAPING.value == "escaping"


def test_fixture_round_trip() -> None:
    raw = {
        "id": "t",
        "capability": "escaping",
        "input": {"kind": "escape_text", "text": "a"},
        "expected": {"escaped_text": "a"},
    }
    fixture = ConformanceFixture.model_validate(raw)
    assert fixture.fixture_version == FIXTURE_VERSION
    assert fixture.model_dump()["id"] == "t"
