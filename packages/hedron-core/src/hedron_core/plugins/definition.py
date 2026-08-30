"""Composable plugin registration definitions.

Plugin entry points are intentionally tiny adapters.  Package-owned registration
work is represented as ordered contributions so each concern can be tested and
extended without changing the loader or creating a second registration API.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Protocol

from hedron_core.plugins.context import PluginContext
from hedron_core.plugins.meta import PluginMeta

__all__ = ["CallbackContribution", "PluginContribution", "PluginDefinition"]


class PluginContribution(Protocol):
    """A single package-owned registration responsibility."""

    @property
    def name(self) -> str: ...

    def apply(self, ctx: PluginContext) -> None: ...


@dataclass(frozen=True, slots=True)
class CallbackContribution:
    """Adapt a package registration function to the contribution protocol."""

    name: str
    callback: Callable[[PluginContext], None]

    def apply(self, ctx: PluginContext) -> None:
        self.callback(ctx)


@dataclass(frozen=True, slots=True)
class PluginDefinition:
    """Metadata plus deterministic, independently-owned registration work."""

    meta: PluginMeta
    contributions: tuple[PluginContribution, ...] = ()

    def __post_init__(self) -> None:
        names = tuple(contribution.name for contribution in self.contributions)
        if any(not name.strip() for name in names):
            raise ValueError("Plugin contributions require non-empty names")
        if len(names) != len(set(names)):
            raise ValueError("Plugin contribution names must be unique")

    @classmethod
    def from_callbacks(
        cls,
        meta: PluginMeta,
        callbacks: Iterable[tuple[str, Callable[[PluginContext], None]]],
    ) -> PluginDefinition:
        return cls(
            meta=meta,
            contributions=tuple(
                CallbackContribution(name=name, callback=callback) for name, callback in callbacks
            ),
        )

    def register(self, ctx: PluginContext) -> None:
        """Apply contributions in declaration order for loader determinism."""
        context_meta = getattr(ctx, "meta", None)
        if context_meta is not None and context_meta != self.meta:
            raise ValueError(f"PluginContext metadata does not match {self.meta.name!r} definition")
        for contribution in self.contributions:
            contribution.apply(ctx)
