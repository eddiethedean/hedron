"""Independently removable sample-kit variants (SAMPLE-054).

Each variant is a self-contained folder discovered at import time. Deleting a
variant folder removes the variant from ``list_variants`` and from plugin
registration without breaking the rest of the kit. A missing third-party
dependency inside a variant still raises, so absence stays honest.
"""

from __future__ import annotations

import importlib
from collections.abc import Iterator
from typing import Protocol, cast

from hedron_core.plugins import PluginContext

VARIANT_MODULES: tuple[str, ...] = (
    "web_component",
    "workflow",
    "hdj",
    "optional",
)

__all__ = [
    "VARIANT_MODULES",
    "SampleVariant",
    "iter_variants",
    "list_variants",
    "load_variant",
    "register_variants",
]


class SampleVariant(Protocol):
    """Registration surface every variant module implements."""

    VARIANT_ID: str

    def register(self, ctx: PluginContext) -> None: ...


def load_variant(name: str) -> SampleVariant | None:
    """Import a variant module, or return None when its folder was removed."""
    qualified = f"{__name__}.{name}"
    try:
        module = importlib.import_module(qualified)
    except ModuleNotFoundError as exc:
        missing = exc.name or ""
        if missing == qualified or missing.startswith(f"{qualified}."):
            return None
        raise
    return cast(SampleVariant, module)


def iter_variants() -> Iterator[SampleVariant]:
    for name in VARIANT_MODULES:
        module = load_variant(name)
        if module is not None:
            yield module


def list_variants() -> tuple[str, ...]:
    """Return the ids of the variants present in this installation."""
    return tuple(variant.VARIANT_ID for variant in iter_variants())


def register_variants(ctx: PluginContext) -> tuple[str, ...]:
    """Register every present variant and return the registered ids."""
    registered: list[str] = []
    for variant in iter_variants():
        variant.register(ctx)
        registered.append(variant.VARIANT_ID)
    return tuple(registered)
