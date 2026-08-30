"""DataEditor component with typed changes and Tabulator Web Component host."""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Literal, cast

from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Model, Props
from hedron_core.security import Secret
from hedron_core.typing_aliases import JsonValue
from hedron_data.columns import Column, resolve_columns
from hedron_data.normalize import normalize_rows
from hedron_data.sources import (
    AsyncDataEditorSource,
    CellUpdate,
    DataChanges,
    DataEditorSource,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)

SaveMode = Literal["batch", "row", "cell"]

ABI_VERSION = 1
TAG_NAME = "hedron-data-editor"
ELEMENT_ID = "hedron-data-editor"
DATA_EDITOR_EVENTS = (
    "hedron-data-cell-edit",
    "hedron-data-row-edit",
    "hedron-data-selection-change",
    "hedron-data-validation-error",
    "hedron-data-conflict",
    "hedron-data-optimistic",
)


def _public_row(row: Mapping[str, object], columns: Sequence[Column]) -> dict[str, JsonValue]:
    out: dict[str, JsonValue] = {}
    for c in columns:
        if c.hidden:
            continue
        val = row.get(c.name)
        if c.secret or isinstance(val, Secret):
            out[c.name] = "***"
        else:
            out[c.name] = cast(JsonValue, val)
    return out


def filter_writable_changes(
    changes: DataChanges[dict[str, JsonValue]],
    *,
    writable_fields: frozenset[str],
    read_only_fields: frozenset[str],
    hidden_fields: frozenset[str],
    allow_deletes: bool = True,
    key_field: str | None = None,
) -> tuple[DataChanges[dict[str, JsonValue]], tuple[FieldError, ...]]:
    """Server-authoritative writable-field policy for forged client edits."""
    errors: list[FieldError] = []
    updates: list[CellUpdate] = []
    for upd in changes.updates:
        if (
            upd.field in read_only_fields
            or upd.field in hidden_fields
            or upd.field not in writable_fields
        ):
            errors.append(
                FieldError(
                    row_key=upd.row_key,
                    field=upd.field,
                    message="Forged or unauthorized field write rejected",
                )
            )
            continue
        updates.append(upd)
    inserts: list[dict[str, JsonValue]] = []
    for row in changes.inserts:
        row_value: Any = row
        if not isinstance(row_value, Mapping):
            errors.append(
                FieldError(
                    row_key=None,
                    field=None,
                    message="Insert rows must be mappings",
                )
            )
            continue
        row_mapping = cast(Mapping[str, JsonValue], row_value)
        cleaned: dict[str, JsonValue] = {
            str(k): v
            for k, v in row_mapping.items()
            if (k == key_field or k in writable_fields)
            and k not in read_only_fields
            and k not in hidden_fields
        }
        if (
            key_field
            and key_field not in cleaned
            and key_field in row_mapping
            and key_field not in hidden_fields
        ):
            # Identity key may be read-only but still required on insert.
            cleaned[key_field] = row_mapping[key_field]
        inserts.append(cleaned)
    deletes: list[str] = []
    if changes.deletes:
        if not allow_deletes:
            for key in changes.deletes:
                errors.append(
                    FieldError(
                        row_key=key,
                        field=None,
                        message="Deletes are not authorized",
                    )
                )
        else:
            deletes = list(changes.deletes)
    filtered: DataChanges[dict[str, JsonValue]] = DataChanges(
        updates=tuple(updates),
        inserts=tuple(inserts),
        deletes=tuple(deletes),
        dataset_version=changes.dataset_version,
    )
    return filtered, tuple(errors)


class DataEditorProps(Props):
    editor_key: str = "editor"
    save_mode: SaveMode = "batch"
    page_size: int = 25
    caption: str | None = None


class DataEditor(Component[DataEditorProps]):
    """Editable grid host; browser module owns interaction, server owns policy."""

    props_type = DataEditorProps
    distribution = "hedron-data"
    logical_name = "DataEditor"

    def __init__(
        self,
        rows: object = None,
        *,
        key: str = "editor",
        row_model: type[Model] | None = None,
        columns: Sequence[Column] | None = None,
        key_field: str = "id",
        on_save: Callable[[DataChanges[dict[str, JsonValue]]], DataSaveResult[dict[str, JsonValue]]]
        | None = None,
        source: DataEditorSource[dict[str, JsonValue]]
        | AsyncDataEditorSource[dict[str, JsonValue]]
        | None = None,
        page: DataPage[dict[str, JsonValue]] | None = None,
        save_mode: SaveMode = "batch",
        page_size: int = 25,
        caption: str | None = None,
        save_endpoint: str | None = None,
        allow_deletes: bool = True,
        **kwargs: object,
    ) -> None:
        super().__init__(
            DataEditorProps(
                editor_key=key,
                save_mode=save_mode,
                page_size=page_size,
                caption=caption,
                **kwargs,
            )
        )
        # Server-only — never part of serializable props.
        self._on_save = on_save
        self._source = source
        self._key_field = key_field
        self._save_endpoint = save_endpoint
        self._row_model = row_model
        self._allow_deletes = allow_deletes

        if page is not None:
            raw: list[object] = list(cast(Sequence[object], page.rows))
            self._version = page.version
            self._total = page.total
        elif source is not None:
            fetch = getattr(source, "fetch", None)
            if not callable(fetch):
                raise error(
                    "HED-DATA-0005",
                    title="Invalid data source",
                    explanation="DataEditor source must expose fetch().",
                    remediation="Pass a DataEditorSource or an explicit page=.",
                )
            fetched = fetch(DataQuery(limit=page_size))
            if inspect.isawaitable(fetched):
                if inspect.iscoroutine(fetched):
                    fetched.close()
                raise error(
                    "HED-DATA-0006",
                    title="Async source requires explicit page",
                    explanation=(
                        "Async DataEditorSource.fetch cannot be awaited during "
                        "synchronous component construction."
                    ),
                    remediation=(
                        "Await source.fetch(...) and pass page=..., or use a sync source."
                    ),
                )
            if not isinstance(fetched, DataPage):
                raise error(
                    "HED-DATA-0005",
                    title="Invalid fetch result",
                    explanation="source.fetch must return DataPage.",
                    remediation="Return a DataPage from fetch().",
                )
            fetched_page = cast(DataPage[dict[str, JsonValue]], fetched)
            raw = list(cast(Sequence[object], fetched_page.rows))
            self._version = fetched_page.version
            self._total = fetched_page.total
        else:
            raw = list(cast(Sequence[object], normalize_rows(rows)))
            self._version = None
            self._total = len(raw)

        built_rows: list[dict[str, object]] = []
        for r in raw:
            if isinstance(r, Mapping):
                mapping = cast(Mapping[object, object], r)
                built_rows.append({str(k): v for k, v in mapping.items()})
            elif isinstance(r, Model):
                model_data = cast(Mapping[object, object], r.model_dump())
                built_rows.append({str(k): v for k, v in model_data.items()})
            else:
                raise error(
                    "HED-DATA-0005",
                    title="Invalid row",
                    explanation="DataEditor rows must be mappings or Hedron models.",
                    remediation="Pass mappings, models, a DataPage, or a valid source.",
                )
        self._rows = built_rows
        self._columns = resolve_columns(
            row_model=row_model,
            columns=columns,
            rows=cast(Sequence[Mapping[str, JsonValue]], self._rows),
        )

    @property
    def on_save(
        self,
    ) -> Callable[[DataChanges[dict[str, JsonValue]]], DataSaveResult[dict[str, JsonValue]]] | None:
        return self._on_save

    @property
    def columns(self) -> list[Column]:
        return list(self._columns)

    def writable_fields(self) -> frozenset[str]:
        from hedron_data.columns import write_policy

        return frozenset(c.name for c in self._columns if write_policy(c))

    def _policy_clean(
        self, changes: DataChanges[dict[str, JsonValue]]
    ) -> tuple[DataChanges[dict[str, JsonValue]], tuple[FieldError, ...]]:
        return filter_writable_changes(
            changes,
            writable_fields=self.writable_fields(),
            read_only_fields=frozenset(c.name for c in self._columns if c.read_only),
            hidden_fields=frozenset(c.name for c in self._columns if c.hidden),
            allow_deletes=self._allow_deletes,
            key_field=self._key_field,
        )

    def apply_changes(
        self, changes: DataChanges[dict[str, JsonValue]]
    ) -> DataSaveResult[dict[str, JsonValue]]:
        cleaned, policy_errors = self._policy_clean(changes)
        if policy_errors:
            return DataSaveResult(ok=False, errors=policy_errors, version=self._version)
        if self._on_save is not None:
            return self._on_save(cleaned)
        if self._source is not None and hasattr(self._source, "apply"):
            result = self._source.apply(cleaned)  # type: ignore[union-attr]
            if inspect.isawaitable(result):
                if inspect.iscoroutine(result):
                    result.close()
                raise error(
                    "HED-DATA-0006",
                    title="Async apply requires apply_changes_async",
                    explanation="source.apply returned an awaitable.",
                    remediation="Await DataEditor.apply_changes_async(...) for async sources.",
                )
            result_value: object = result
            if isinstance(cast(Any, result_value), DataSaveResult):
                return result_value
            raise error(
                "HED-DATA-0005",
                title="Invalid apply result",
                explanation="source.apply must return DataSaveResult.",
                remediation="Return a DataSaveResult from apply().",
            )
        return DataSaveResult(ok=True, accepted=cleaned, version=self._version)

    async def apply_changes_async(
        self, changes: DataChanges[dict[str, JsonValue]]
    ) -> DataSaveResult[dict[str, JsonValue]]:
        cleaned, policy_errors = self._policy_clean(changes)
        if policy_errors:
            return DataSaveResult(ok=False, errors=policy_errors, version=self._version)
        if self._on_save is not None:
            result = self._on_save(cleaned)
            if inspect.isawaitable(result):
                return await result  # type: ignore[no-any-return]
            return result
        if self._source is not None and hasattr(self._source, "apply"):
            result = self._source.apply(cleaned)  # type: ignore[union-attr]
            if inspect.isawaitable(result):
                result = await result
            result_value: object = result
            if isinstance(cast(Any, result_value), DataSaveResult):
                return result_value
            raise error(
                "HED-DATA-0005",
                title="Invalid apply result",
                explanation="source.apply must return DataSaveResult.",
                remediation="Return a DataSaveResult from apply().",
            )
        return DataSaveResult(ok=True, accepted=cleaned, version=self._version)

    def render(self) -> NodeLike:
        from hedron_data.columns import write_policy

        col_meta = [
            {
                "field": c.name,
                "title": c.label or c.name,
                "editor": (c.editor or "input") if write_policy(c) else False,
                "visible": not c.hidden,
                "headerSort": c.sortable,
                "width": c.width,
                "choices": list(c.choices) if c.choices else None,
            }
            for c in self._columns
            if not c.secret
        ]
        public_rows = [_public_row(r, self._columns) for r in self._rows]
        payload = {
            "keyField": self._key_field,
            "saveMode": self.props.save_mode,
            "columns": col_meta,
            "rows": public_rows,
            "version": self._version,
            "saveEndpoint": self._save_endpoint,
            "total": self._total,
            "allowDeletes": self._allow_deletes,
            "conflictActions": list(conflict_actions()),
        }
        noscript = DataTableFallback(self._columns, public_rows, self.props.caption)
        # ABI host: the custom element IS the markup (chart/example pattern).
        # SSR fallback table remains a child after upgrade (not permanently removed).
        return html.tag(TAG_NAME)(
            noscript.render(),
            **{
                "class_": "hedron-data-editor",
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "data-hedron-editor": self.props.editor_key,
                "data-hedron-module": "hedron-data:tabulator-editor",
                "data-hedron-payload": json.dumps(payload, default=str, separators=(",", ":")),
                "data-hedron-server-region": "fallback",
                "role": "grid",
                "aria-label": self.props.caption or "Data editor",
                "tabindex": "0",
            },
        )


class DataTableFallback:
    def __init__(
        self,
        columns: Sequence[Column],
        rows: Sequence[Mapping[str, JsonValue]],
        caption: str | None,
    ) -> None:
        self._columns = [c for c in columns if not c.hidden and not c.secret]
        self._rows = rows
        self._caption = caption

    def render(self) -> NodeLike:
        children: list[NodeLike] = []
        if self._caption:
            children.append(html.caption(self._caption))
        children.append(
            html.thead(html.tr(*[html.th(c.label or c.name, scope="col") for c in self._columns]))
        )
        body = [
            html.tr(*[html.td(str(row.get(c.name, ""))) for c in self._columns])
            for row in self._rows
        ]
        children.append(html.tbody(*body))
        return html.table(*children, class_="hedron-data-editor-fallback")


def conflict_actions() -> tuple[str, ...]:
    # retain-and-retry must rebase onto the server revision from the conflict
    # response (OPTIMISTIC-039 / #121) — never silently overwrite (no LWW).
    return ("reload", "retain-and-retry", "compare", "cancel")
