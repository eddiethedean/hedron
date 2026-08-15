"""Narrow data-source protocol for Auto inspection (no hedron-data import)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

__all__ = ["DataSource", "is_lazy_source"]


@runtime_checkable
class DataSource(Protocol):
    """Bounded row source used by ``inspect_data`` / Auto.

    Adapters in ``hedron-data`` (and application code) implement this instead of
    relying on pandas/polars/QuerySet type names inside core.
    """

    def inspect_rows(self, *, max_rows: int) -> Sequence[Mapping[str, object]]:
        """Return a bounded window of row mappings."""
        ...


def is_lazy_source(value: object) -> bool:
    """Return True when implicit collection is forbidden.

    Prefer an explicit ``hedron_lazy`` marker. Type-name matching remains a
    fail-closed fallback for Django QuerySets and similarly lazy iterables.
    """
    marker = getattr(value, "hedron_lazy", None)
    if marker is True:
        return True
    type_name = type(value).__name__
    return "lazy" in type_name.lower() or type_name.endswith("QuerySet")
