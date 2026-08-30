"""Saved grid views: columns, filters, sort, and selection state."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from hedron_core.typing_aliases import JsonValue

__all__ = ["SavedView"]

ViewScope = Literal["user", "tenant", "app"]


@dataclass(frozen=True, slots=True)
class SavedView:
    name: str
    version: str = "1"
    scope: ViewScope = "user"
    columns: tuple[str, ...] = ()
    filters: Mapping[str, JsonValue] = field(default_factory=lambda: dict[str, JsonValue]())
    sort: tuple[tuple[str, str], ...] = ()
    selection: tuple[str, ...] = ()
    owner_id: str | None = None

    def validated(self) -> SavedView:
        if not self.name.strip():
            raise ValueError("SavedView.name is required")
        if self.scope not in {"user", "tenant", "app"}:
            raise ValueError(f"Invalid SavedView.scope {self.scope!r}")
        for _field, direction in self.sort:
            if direction not in {"asc", "desc"}:
                raise ValueError(f"Invalid sort direction {direction!r}")
        return SavedView(
            name=self.name.strip(),
            version=self.version,
            scope=self.scope,
            columns=tuple(self.columns),
            filters=dict(self.filters),
            sort=tuple(self.sort),
            selection=tuple(self.selection),
            owner_id=self.owner_id,
        )

    def serialize(self) -> dict[str, Any]:
        view = self.validated()
        return {
            "name": view.name,
            "version": view.version,
            "scope": view.scope,
            "columns": list(view.columns),
            "filters": dict(view.filters),
            "sort": [list(item) for item in view.sort],
            "selection": list(view.selection),
            "owner_id": view.owner_id,
        }

    @classmethod
    def deserialize(cls, data: Mapping[str, Any]) -> SavedView:
        sort_raw: object = data.get("sort") or ()
        columns_raw: object = data.get("columns") or ()
        selection_raw: object = data.get("selection") or ()
        filters_raw: object = data.get("filters", {})
        if not isinstance(columns_raw, (list, tuple)) or any(
            not isinstance(item, str)
            for item in cast(list[object] | tuple[object, ...], columns_raw)
        ):
            raise ValueError("SavedView.columns must be an array of strings")
        if not isinstance(selection_raw, (list, tuple)) or any(
            not isinstance(item, str)
            for item in cast(list[object] | tuple[object, ...], selection_raw)
        ):
            raise ValueError("SavedView.selection must be an array of strings")
        if not isinstance(filters_raw, Mapping):
            raise ValueError("SavedView.filters must be an object")
        if not isinstance(sort_raw, (list, tuple)):
            raise ValueError("SavedView.sort must be an array of pairs")
        sort: list[tuple[str, str]] = []
        typed_sort = cast(list[object] | tuple[object, ...], sort_raw)
        for item in typed_sort:
            if not isinstance(item, (list, tuple)):
                raise ValueError("SavedView.sort entries must be two-item arrays")
            pair = cast(list[object] | tuple[object, ...], item)
            if len(pair) != 2:
                raise ValueError("SavedView.sort entries must be two-item arrays")
            sort.append((str(pair[0]), str(pair[1])))
        columns = cast(list[str] | tuple[str, ...], columns_raw)
        selection = cast(list[str] | tuple[str, ...], selection_raw)
        filters = cast(Mapping[str, JsonValue], filters_raw)
        return cls(
            name=str(data.get("name") or ""),
            version=str(data.get("version") or "1"),
            scope=str(data.get("scope") or "user"),  # type: ignore[arg-type]
            columns=tuple(columns),
            filters=dict(filters),
            sort=tuple(sort),
            selection=tuple(selection),
            owner_id=(str(data["owner_id"]) if data.get("owner_id") is not None else None),
        ).validated()
