"""Reviewed, lazy promotion of mature native Hedron capabilities."""

from __future__ import annotations

import importlib
import importlib.metadata
from dataclasses import dataclass
from typing import Any

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

from edron.capabilities import (
    IncompatibleCapabilityError,
    MissingCapabilityError,
)


@dataclass(frozen=True, slots=True)
class CapabilityPromotion:
    """A reviewed allowlist entry; module import is deferred until ``load``."""

    name: str
    distribution: str
    module: str
    minimum: str
    train: str
    native: str
    status: str = "promoted"

    def inspect(self) -> dict[str, Any]:
        """Check installed metadata without importing the promoted module."""
        try:
            version = importlib.metadata.version(self.distribution)
        except importlib.metadata.PackageNotFoundError:
            return {
                "name": self.name,
                "distribution": self.distribution,
                "status": "missing",
                "required": False,
                "native": self.native,
                "train": self.train,
            }
        try:
            compatible = Version(version) in SpecifierSet(self.train)
            meets_minimum = Version(version) >= Version(self.minimum)
        except (InvalidSpecifier, InvalidVersion, ValueError) as exc:
            return {
                "name": self.name,
                "distribution": self.distribution,
                "version": version,
                "status": "incompatible",
                "reason": str(exc),
                "required": False,
                "native": self.native,
                "train": self.train,
            }
        return {
            "name": self.name,
            "distribution": self.distribution,
            "version": version,
            "status": "available" if compatible and meets_minimum else "incompatible",
            "required": False,
            "native": self.native,
            "train": self.train,
        }

    def load(self) -> Any:
        """Import the native module after metadata compatibility succeeds."""
        facts = self.inspect()
        if facts["status"] == "missing":
            raise MissingCapabilityError(
                f"install {self.distribution!r} to enable {self.name!r}",
                distribution=self.distribution,
            )
        if facts["status"] != "available":
            raise IncompatibleCapabilityError(
                f"{self.distribution} is outside the compatible Hedron train {self.train}",
                distribution=self.distribution,
                version=facts.get("version"),
            )
        try:
            return importlib.import_module(self.module)
        except Exception as exc:  # pragma: no cover - defensive import boundary
            from edron.capabilities import BrokenCapabilityError

            raise BrokenCapabilityError(
                f"{self.distribution} is installed but {self.module!r} could not be imported",
                distribution=self.distribution,
            ) from exc

    @property
    def ejection(self) -> str:
        return f"Use the native {self.native} API directly; no Edron registry is required."

    def as_mapping(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "distribution": self.distribution,
            "module": self.module,
            "minimum": self.minimum,
            "train": self.train,
            "native": self.native,
            "status": self.status,
            "ejection": self.ejection,
        }


PROMOTED_CAPABILITIES: dict[str, CapabilityPromotion] = {
    "data": CapabilityPromotion(
        "data", "hedron-data", "hedron_data", "0.67.0", ">=0.67.0,<2.0", "hedron_data"
    ),
    "charts": CapabilityPromotion(
        "charts", "hedron-charts", "hedron_charts", "0.2.2", ">=0.2.2,<0.3", "hedron_charts"
    ),
    "maps": CapabilityPromotion(
        "maps", "hedron-maps", "hedron_maps", "0.1.2", ">=0.1.2,<0.2", "hedron_maps"
    ),
}


def promoted_capability(name: str) -> CapabilityPromotion:
    """Return one reviewed capability entry without importing its module."""
    try:
        return PROMOTED_CAPABILITIES[name]
    except KeyError as exc:
        raise KeyError(f"unknown promoted capability {name!r}") from exc


def promoted_capabilities() -> tuple[CapabilityPromotion, ...]:
    return tuple(PROMOTED_CAPABILITIES[name] for name in sorted(PROMOTED_CAPABILITIES))


__all__ = [
    "CapabilityPromotion",
    "PROMOTED_CAPABILITIES",
    "promoted_capability",
    "promoted_capabilities",
]
