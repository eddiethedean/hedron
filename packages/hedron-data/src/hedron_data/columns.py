"""Column derivation from Hedron models and Field metadata."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, get_args, get_origin

from hedron_core.field import hedron_meta
from hedron_core.models import Model
from hedron_core.security import Secret
from hedron_data.sources import ColumnSchema


@dataclass(frozen=True, slots=True)
class Column:
    name: str
    label: str | None = None
    editor: str | None = None
    read_only: bool = False
    hidden: bool = False
    secret: bool = False
    sortable: bool = False
    filterable: bool = False
    choices: tuple[Any, ...] | None = None
    width: str | int | None = None

    def to_schema(self) -> ColumnSchema:
        return ColumnSchema(
            name=self.name,
            label=self.label or self.name.replace("_", " ").title(),
            editor=self.editor or "text",
            read_only=self.read_only,
            hidden=self.hidden,
            secret=self.secret,
            sortable=self.sortable,
            filterable=self.filterable,
            choices=self.choices,
            width=self.width,
        )


def _editor_for_annotation(annotation: Any) -> str:
    origin = get_origin(annotation) or annotation
    if origin is Secret:
        args = get_args(annotation)
        return _editor_for_annotation(args[0]) if args else "text"
    name = getattr(origin, "__name__", str(origin))
    if name in {"int", "float", "Decimal"}:
        return "number"
    if name in {"bool"}:
        return "boolean"
    if name in {"date"}:
        return "date"
    if name in {"datetime"}:
        return "datetime"
    return "text"


def columns_from_model(model: type[Model]) -> list[Column]:
    cols: list[Column] = []
    for name, info in model.model_fields.items():
        meta = hedron_meta(info)
        annotation = info.annotation
        editor = meta.get("editor") or _editor_for_annotation(annotation)
        choices = meta.get("choices")
        cols.append(
            Column(
                name=name,
                label=meta.get("label") or name.replace("_", " ").title(),
                editor=editor,
                read_only=bool(meta.get("read_only", False)),
                hidden=bool(meta.get("hidden", False)),
                secret=bool(meta.get("secret", False)),
                sortable=bool(meta.get("sortable", False)),
                filterable=bool(meta.get("filterable", False)),
                choices=tuple(choices) if choices else None,
                width=meta.get("width"),
            )
        )
    return cols


def resolve_columns(
    *,
    row_model: type[Model] | None = None,
    columns: Sequence[Column] | None = None,
    rows: Sequence[Mapping[str, Any]] | None = None,
) -> list[Column]:
    if columns:
        return list(columns)
    if row_model is not None:
        return columns_from_model(row_model)
    if rows:
        keys: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for k in row:
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
        return [Column(name=k) for k in keys]
    return []
