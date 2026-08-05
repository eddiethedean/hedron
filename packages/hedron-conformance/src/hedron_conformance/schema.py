"""Fixture schema for the language-neutral conformance kit."""

from __future__ import annotations

import json
from enum import StrEnum
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

FIXTURE_VERSION = "1.0.0"
CONTRACT_VERSION = "hedron-portable-1"


class Capability(StrEnum):
    ESCAPING = "escaping"
    IDENTITY = "identity"
    DIAGNOSTICS = "diagnostics"
    ARTIFACT_VERSION = "artifact-version"
    RENDERING = "rendering"
    ACCESSIBILITY = "accessibility"
    ADVERSARIAL = "adversarial"


class FixtureInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str
    tree: dict[str, Any] | None = None
    text: str | None = None
    attr: str | None = None
    logical_id: str | None = None
    artifact: dict[str, Any] | None = None
    expect_error: bool = False


class ExpectedOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    html: str | None = None
    escaped_text: str | None = None
    escaped_attr: str | None = None
    identity: str | None = None
    diagnostic_code: str | None = None
    artifact_version: str | None = None
    a11y_ok: bool | None = None
    error_code: str | None = None


class ConformanceFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    fixture_version: str = FIXTURE_VERSION
    contract_version: str = CONTRACT_VERSION
    capability: Capability
    description: str = ""
    input: FixtureInput
    expected: ExpectedOutcome
    normalization: str = "html-v1"
    negative: bool = False


def fixtures_dir() -> Path:
    root = resources.files("hedron_conformance").joinpath("fixtures")
    return Path(str(root))


def load_bundled_fixtures() -> list[ConformanceFixture]:
    directory = fixtures_dir()
    fixtures: list[ConformanceFixture] = []
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            fixtures.extend(ConformanceFixture.model_validate(item) for item in data)
        else:
            fixtures.append(ConformanceFixture.model_validate(data))
    return fixtures


def fixture_schema_dict() -> dict[str, Any]:
    """JSON Schema for ConformanceFixture (draft-friendly export)."""
    return ConformanceFixture.model_json_schema()
