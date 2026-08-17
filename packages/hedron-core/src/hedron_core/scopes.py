"""Portable scope declarations. They never grant or authenticate."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["RequiresScopes"]


@dataclass(frozen=True, slots=True)
class RequiresScopes:
    """Inspectable OpenAPI/adapter requirement. Applications still own authz."""

    scopes: tuple[str, ...]

    def __init__(self, *scopes: str) -> None:
        object.__setattr__(self, "scopes", tuple(str(item) for item in scopes if str(item)))

    def grants_access(self) -> bool:
        return False
