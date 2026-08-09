"""Column derivation from Hedron models and Field metadata."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import cast, get_args, get_origin

from hedron_core.field import hedron_meta
from hedron_core.models import Model
from hedron_core.security import Secret
from hedron_core.typing_aliases import JsonValue
from hedron_data.sources import ColumnSchema

__all__ = [
    "COLUMN_DISPLAYS",
    "Column",
    "columns_from_model",
    "display_for_editor",
    "resolve_columns",
    "write_policy",
]

COLUMN_DISPLAYS = frozenset(
    {
        "numeric",
        "text",
        "checkbox",
        "select",
        "date",
        "datetime",
        "link",
        "image",
        "progress",
        "compact-chart",
    }
)


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
    choices: tuple[JsonValue, ...] | None = None
    width: str | int | None = None
    display: str | None = None
    writable: bool | None = None
    format: str | None = None

    def to_schema(self) -> ColumnSchema:
        display = self.display or display_for_editor(self.editor or "text")
        if display not in COLUMN_DISPLAYS:
            raise ValueError(f"Unknown column display {display!r}")
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
            display=display,
            writable=self.writable,
            format=self.format,
        )


def display_for_editor(editor: str) -> str:
    mapping = {
        "number": "numeric",
        "boolean": "checkbox",
        "checkbox": "checkbox",
        "select": "select",
        "date": "date",
        "datetime": "datetime",
        "link": "link",
        "image": "image",
        "progress": "progress",
        "compact-chart": "compact-chart",
        "text": "text",
    }
    return mapping.get(editor, "text")


def write_policy(column: Column | ColumnSchema) -> bool:
    """Display never implies writable; unset ``writable`` denies writes.

    Secrets, hidden, and read-only columns always deny. Explicit ``writable=True``
    is required (deny-by-default), matching InMemoryDataSource field allowlists.
    """
    if column.read_only or column.hidden or column.secret:
        return False
    return column.writable is True


def _editor_for_annotation(annotation: object) -> str:
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
        origin = get_origin(annotation) or annotation
        is_secret_ann = origin is Secret
        label_raw = meta.get("label")
        label = label_raw if isinstance(label_raw, str) else name.replace("_", " ").title()
        editor_val = editor if isinstance(editor, str) else "text"
        width_raw = meta.get("width")
        width: str | int | None
        if isinstance(width_raw, (str, int)) and not isinstance(width_raw, bool):
            width = width_raw
        else:
            width = None
        display_raw = meta.get("display")
        display = display_raw if isinstance(display_raw, str) else display_for_editor(editor_val)
        writable_raw = meta.get("writable")
        writable = writable_raw if isinstance(writable_raw, bool) else None
        format_raw = meta.get("format")
        fmt = format_raw if isinstance(format_raw, str) else None
        cols.append(
            Column(
                name=name,
                label=label,
                editor=editor_val,
                read_only=bool(meta.get("read_only", False)) or is_secret_ann,
                hidden=bool(meta.get("hidden", False)),
                secret=bool(meta.get("secret", False)) or is_secret_ann,
                sortable=bool(meta.get("sortable", False)),
                filterable=bool(meta.get("filterable", False)),
                choices=tuple(cast(tuple[JsonValue, ...] | list[JsonValue], choices))
                if choices
                else None,
                width=width,
                display=display,
                writable=writable,
                format=fmt,
            )
        )
    return cols


def resolve_columns(
    *,
    row_model: type[Model] | None = None,
    columns: Sequence[Column] | None = None,
    rows: Sequence[Mapping[str, JsonValue]] | None = None,
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
