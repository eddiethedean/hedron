"""Reusable Edron feature-package declarations.

Phase 0.6 deliberately keeps package composition declarative.  A package is a
small, immutable description of an already native ``FeatureBundle`` plus the
assets it owns; registration is delegated to Hedron and is rolled back as one
transaction when any part fails.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Any, cast

from hedron_core.bundles import FeatureBundle, FeatureProvider
from hedron_core.registry import AssetMeta

MAX_FEATURE_PACKAGES = 64
MAX_PACKAGE_ASSETS = 128
MAX_PACKAGE_STRING = 256
_PACKAGE_NAME = re.compile(r"^[a-z][a-z0-9_.-]{0,127}$")


class PackageConflictError(ValueError):
    """A package or one of its native-owned contributions conflicts."""


@dataclass(frozen=True, slots=True)
class FeaturePackage:
    """A reusable, reviewable Edron package declaration.

    ``bundle`` must be a native ``FeatureBundle`` (or provider).  The package
    never accepts a registration callback: importing a package therefore
    cannot execute application code or create a hidden registry.
    """

    name: str
    version: str
    bundle: FeatureBundle | FeatureProvider | None = None
    assets: tuple[AssetMeta, ...] = ()
    description: str = ""
    documentation: str | None = None

    def __post_init__(self) -> None:
        name = str(self.name).strip()
        version = str(self.version).strip()
        if not _PACKAGE_NAME.fullmatch(name):
            raise PackageConflictError(
                "package name must be a lowercase dotted identifier (max 128 characters)"
            )
        if not version or len(version) > MAX_PACKAGE_STRING:
            raise PackageConflictError("package version must be a bounded non-empty string")
        if len(str(self.description)) > MAX_PACKAGE_STRING:
            raise PackageConflictError("package description is too long")
        if self.documentation is not None and len(str(self.documentation)) > MAX_PACKAGE_STRING:
            raise PackageConflictError("package documentation reference is too long")
        if len(self.assets) > MAX_PACKAGE_ASSETS:
            raise PackageConflictError(f"at most {MAX_PACKAGE_ASSETS} assets may be declared")
        seen: set[str] = set()
        for asset in self.assets:
            if not isinstance(cast(Any, asset), AssetMeta):
                raise TypeError("FeaturePackage assets must be native AssetMeta values")
            if asset.logical_id in seen:
                raise PackageConflictError(f"duplicate package asset {asset.logical_id!r}")
            seen.add(asset.logical_id)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "assets", tuple(self.assets))

    @property
    def logical_id(self) -> str:
        return f"edron-package:{self.name}"

    def to_bundle(self) -> FeatureBundle:
        """Return the package's native bundle with package provenance applied."""
        if self.bundle is None:
            return FeatureBundle(
                logical_id=self.logical_id,
                provider=self.name,
                provider_version=self.version,
            )
        value = self.bundle if isinstance(self.bundle, FeatureBundle) else self.bundle.to_bundle()
        if not isinstance(cast(Any, value), FeatureBundle):
            raise TypeError("FeaturePackage provider must return FeatureBundle")
        # Preserve the provider's stable logical id and surfaces while making
        # package identity/version explicit in the native projection.
        return replace(
            value,
            provider=value.provider or self.name,
            provider_version=value.provider_version or self.version,
        )


def feature_package(
    name: str,
    version: str,
    *,
    bundle: FeatureBundle | FeatureProvider | None = None,
    assets: Sequence[AssetMeta] = (),
    description: str = "",
    documentation: str | None = None,
) -> FeaturePackage:
    """Construct a :class:`FeaturePackage` with a beginner-friendly spelling."""
    return FeaturePackage(
        name=name,
        version=version,
        bundle=bundle,
        assets=tuple(assets),
        description=description,
        documentation=documentation,
    )


__all__ = [
    "FeaturePackage",
    "MAX_FEATURE_PACKAGES",
    "MAX_PACKAGE_ASSETS",
    "PackageConflictError",
    "feature_package",
]
