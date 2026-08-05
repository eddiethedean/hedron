"""Saved grid views: columns, filters, sort, and selection state."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from hedron_core.typing_aliases import JsonValue

__all__ = ["SavedView"]

ViewScope = Literal["user", "tenant", "app"]


@dataclass(frozen=True, slots=True)
class SavedView:
    name: str
    version: str = "1"
    scope: ViewScope = "user"
    columns: tuple[str, ...] = ()
    filters: Mapping[str, JsonValue] = field(default_factory=dict)
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
        sort_raw = data.get("sort") or ()
        sort: list[tuple[str, str]] = []
        for item in sort_raw:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                sort.append((str(item[0]), str(item[1])))
        return cls(
            name=str(data.get("name") or ""),
            version=str(data.get("version") or "1"),
            scope=str(data.get("scope") or "user"),  # type: ignore[arg-type]
            columns=tuple(str(c) for c in (data.get("columns") or ())),
            filters=dict(data.get("filters") or {}),
            sort=tuple(sort),
            selection=tuple(str(s) for s in (data.get("selection") or ())),
            owner_id=(str(data["owner_id"]) if data.get("owner_id") is not None else None),
        ).validated()
