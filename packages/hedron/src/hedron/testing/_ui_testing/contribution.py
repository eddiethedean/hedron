"""Versioned metadata for explicitly loaded UI-testing package contributions."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast, final

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

_PACKAGE_ID_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
_NAME_RE = re.compile(r"[a-z][a-z0-9_.-]{0,63}\Z")
_FIXTURE_RE = re.compile(r"[a-z][a-z0-9_]{0,63}\Z")


@final
@dataclass(frozen=True, slots=True)
class UITestingContribution:
    """Bounded package identity and capabilities for a test-only contribution.

    Contributions are loaded only when a test explicitly names their import
    reference with ``@pytest.mark.hedron_ui_contribution(...)``. They declare
    fixture resources and metadata; they do not receive browser, host, or
    artifact ownership.
    """

    package_id: str
    package_version: str
    hedron_version_range: str
    capabilities: tuple[str, ...]
    fixture_resources: tuple[str, ...] = ()
    schema_version: int = 1

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("unsupported UI-testing contribution schema")
        if not _matches(_PACKAGE_ID_RE, self.package_id):
            raise ValueError("invalid UI-testing contribution package id")
        if len(self.package_version) > 64:
            raise ValueError("invalid UI-testing contribution package version")
        try:
            _ = Version(self.package_version)
        except (InvalidVersion, TypeError) as exc:
            raise ValueError("invalid UI-testing contribution package version") from exc
        if len(self.hedron_version_range) > 128:
            raise ValueError("invalid UI-testing contribution Hedron version range")
        try:
            _ = SpecifierSet(self.hedron_version_range)
        except (InvalidSpecifier, TypeError) as exc:
            raise ValueError("invalid UI-testing contribution Hedron version range") from exc
        self._validate_names(self.capabilities, _NAME_RE, "capabilities")
        self._validate_names(self.fixture_resources, _FIXTURE_RE, "fixture resources")

    def validate_for(self, hedron_version: str) -> None:
        """Require this contribution's declared range to include the installed Hedron."""
        try:
            version = Version(hedron_version)
            supported = SpecifierSet(self.hedron_version_range)
        except (InvalidSpecifier, InvalidVersion) as exc:
            raise ValueError("invalid UI-testing contribution version compatibility") from exc
        if not supported.contains(version, prereleases=True):
            raise ValueError("UI-testing contribution does not support this Hedron version")

    def to_metadata(self) -> dict[str, object]:
        """Return a JSON-safe, bounded summary for a failure manifest."""
        return {
            "schema_version": self.schema_version,
            "package_id": self.package_id,
            "package_version": self.package_version,
            "hedron_version_range": self.hedron_version_range,
            "capabilities": list(self.capabilities),
            "fixture_resources": list(self.fixture_resources),
        }

    @staticmethod
    def _validate_names(values: object, pattern: re.Pattern[str], label: str) -> None:
        if not isinstance(values, tuple):
            raise ValueError(f"invalid UI-testing contribution {label}")
        value_items = cast(tuple[object, ...], values)
        if len(value_items) > 32:
            raise ValueError(f"invalid UI-testing contribution {label}")
        if any(not _matches(pattern, value) for value in value_items):
            raise ValueError(f"invalid UI-testing contribution {label}")
        if len(set(value_items)) != len(value_items):
            raise ValueError(f"duplicate UI-testing contribution {label}")


def _matches(pattern: re.Pattern[str], value: object) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def validate_ui_testing_contribution(
    value: object,
    *,
    hedron_version: str,
) -> UITestingContribution:
    """Validate object or JSON-shaped contribution metadata against this Hedron version."""
    contribution: UITestingContribution
    if isinstance(value, UITestingContribution):
        contribution = value
    elif isinstance(value, Mapping):
        metadata = cast(Mapping[str, object], value)
        expected = {
            "schema_version",
            "package_id",
            "package_version",
            "hedron_version_range",
            "capabilities",
            "fixture_resources",
        }
        if set(metadata) != expected:
            raise ValueError("contribution metadata has missing or unknown fields")
        schema_version = metadata["schema_version"]
        package_id = metadata["package_id"]
        package_version = metadata["package_version"]
        hedron_version_range = metadata["hedron_version_range"]
        if type(schema_version) is not int:
            raise ValueError("invalid UI-testing contribution schema")
        if not isinstance(package_id, str):
            raise ValueError("invalid UI-testing contribution identity")
        if not isinstance(package_version, str):
            raise ValueError("invalid UI-testing contribution identity")
        if not isinstance(hedron_version_range, str):
            raise ValueError("invalid UI-testing contribution identity")
        contribution = UITestingContribution(
            package_id=package_id,
            package_version=package_version,
            hedron_version_range=hedron_version_range,
            capabilities=_metadata_names(metadata["capabilities"], "capabilities"),
            fixture_resources=_metadata_names(metadata["fixture_resources"], "fixture resources"),
            schema_version=schema_version,
        )
    else:
        raise ValueError("contribution must expose bounded versioned metadata")
    contribution.validate_for(hedron_version)
    return contribution


def _metadata_names(value: object, label: str) -> tuple[str, ...]:
    if isinstance(value, list):
        values = cast(list[object], value)
    elif isinstance(value, tuple):
        values = cast(tuple[object, ...], value)
    else:
        raise ValueError(f"invalid UI-testing contribution {label}")
    names: list[str] = []
    for item in values:
        if not isinstance(item, str):
            raise ValueError(f"invalid UI-testing contribution {label}")
        names.append(item)
    return tuple(names)


__all__ = ["UITestingContribution", "validate_ui_testing_contribution"]
