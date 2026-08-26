from __future__ import annotations

import importlib
import importlib.metadata
from typing import Any

from edron.errors import EdronError


class CapabilityError(EdronError):
    code = "EDRON_CAPABILITY_ERROR"


class MissingCapabilityError(CapabilityError):
    code = "EDRON_CAPABILITY_MISSING"


class IncompatibleCapabilityError(CapabilityError):
    code = "EDRON_CAPABILITY_INCOMPATIBLE"


class BrokenCapabilityError(CapabilityError):
    code = "EDRON_CAPABILITY_BROKEN"


def require_capability(
    distribution: str, module: str | None = None, *, minimum: str | None = None
) -> Any:
    try:
        version = importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError as exc:
        raise MissingCapabilityError(
            f"install {distribution!r} to enable this capability", distribution=distribution
        ) from exc
    if minimum is not None:
        from packaging.version import Version

        if Version(version) < Version(minimum):
            raise IncompatibleCapabilityError(
                f"{distribution} {version} is older than {minimum}",
                distribution=distribution,
                version=version,
            )
    if module is None:
        return version
    try:
        return importlib.import_module(module)
    except Exception as exc:
        raise BrokenCapabilityError(
            f"{distribution} is installed but {module!r} could not be imported",
            distribution=distribution,
        ) from exc
