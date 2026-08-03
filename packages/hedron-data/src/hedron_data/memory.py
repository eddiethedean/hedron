"""In-memory paged DataEditorSource for tests and reference apps."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from hedron_data.sources import (
    CellUpdate,
    ColumnSchema,
    Conflict,
    DataChanges,
    DataPage,
    DataQuery,
    DataSaveResult,
    FieldError,
)


def _row_key(row: Mapping[str, Any], key_field: str) -> str:
    return str(row[key_field])


class InMemoryDataSource:
    """Sync in-memory source with optimistic concurrency via per-row versions."""

    def __init__(
        self,
        rows: Sequence[Mapping[str, Any]],
        *,
        key_field: str = "id",
        schema: Sequence[ColumnSchema] = (),
        writable_fields: frozenset[str] | None = None,
        version: str = "1",
        audit_hook: Callable[[DataChanges[dict[str, Any]]], None] | None = None,
    ) -> None:
        self._key_field = key_field
        self._rows: dict[str, dict[str, Any]] = {_row_key(r, key_field): dict(r) for r in rows}
        self._row_versions: dict[str, str] = {k: version for k in self._rows}
        self._schema = tuple(schema)
        self._writable = writable_fields
        self._dataset_version = version
        self._audit_hook = audit_hook
        self._version_counter = int(version) if version.isdigit() else 1

    @property
    def dataset_version(self) -> str:
        return self._dataset_version

    def _next_version(self) -> str:
        self._version_counter += 1
        self._dataset_version = str(self._version_counter)
        return self._dataset_version

    def fetch(self, query: DataQuery) -> DataPage[dict[str, Any]]:
        q = query.validated()
        items = list(self._rows.values())
        for field_name, expected in q.filters.items():
            items = [r for r in items if r.get(field_name) == expected]
        if q.search:
            needle = q.search.lower()
            items = [
                r
                for r in items
                if any(needle in str(v).lower() for v in r.values() if v is not None)
            ]
        for field_name, direction in reversed(q.sort):
            items.sort(
                key=lambda r, f=field_name: (r.get(f) is None, r.get(f)),
                reverse=direction == "desc",
            )
        total = len(items)
        page = items[q.offset : q.offset + q.limit]
        if q.projection:
            page = [{k: r.get(k) for k in q.projection} for r in page]
        next_offset = q.offset + q.limit if q.offset + q.limit < total else None
        return DataPage(
            rows=page,
            schema=self._schema,
            total=total,
            next_offset=next_offset,
            version=self._dataset_version,
        )

    def apply(self, changes: DataChanges[dict[str, Any]]) -> DataSaveResult[dict[str, Any]]:
        if changes.dataset_version is not None and changes.dataset_version != self._dataset_version:
            return DataSaveResult(
                ok=False,
                conflicts=(
                    Conflict(
                        row_key="*",
                        field=None,
                        server_value=self._dataset_version,
                        client_value=changes.dataset_version,
                        message="Dataset version conflict",
                    ),
                ),
                version=self._dataset_version,
            )

        errors: list[FieldError] = []
        conflicts: list[Conflict] = []
        accepted_updates: list[CellUpdate] = []
        accepted_inserts: list[dict[str, Any]] = []
        accepted_deletes: list[str] = []

        for upd in changes.updates:
            if self._writable is not None and upd.field not in self._writable:
                errors.append(
                    FieldError(
                        row_key=upd.row_key,
                        field=upd.field,
                        message="Field is not writable",
                    )
                )
                continue
            schema_col = next((c for c in self._schema if c.name == upd.field), None)
            if schema_col is not None and (schema_col.read_only or schema_col.hidden):
                errors.append(
                    FieldError(
                        row_key=upd.row_key,
                        field=upd.field,
                        message="Field is read-only or hidden",
                    )
                )
                continue
            row = self._rows.get(upd.row_key)
            if row is None:
                errors.append(
                    FieldError(row_key=upd.row_key, field=upd.field, message="Unknown row")
                )
                continue
            current_ver = self._row_versions.get(upd.row_key)
            if upd.row_version is not None and upd.row_version != current_ver:
                conflicts.append(
                    Conflict(
                        row_key=upd.row_key,
                        field=upd.field,
                        server_value=row.get(upd.field),
                        client_value=upd.value,
                        message="Stale row version",
                    )
                )
                continue
            row[upd.field] = upd.value
            self._row_versions[upd.row_key] = self._next_version()
            accepted_updates.append(upd)

        for inserted in changes.inserts:
            row = dict(inserted)
            key = _row_key(row, self._key_field)
            if key in self._rows:
                errors.append(
                    FieldError(row_key=key, field=self._key_field, message="Duplicate key")
                )
                continue
            if self._writable is not None:
                for field_name in list(row):
                    if field_name != self._key_field and field_name not in self._writable:
                        del row[field_name]
            self._rows[key] = row
            self._row_versions[key] = self._next_version()
            accepted_inserts.append(row)

        for key in changes.deletes:
            if key not in self._rows:
                errors.append(FieldError(row_key=key, field=None, message="Unknown row"))
                continue
            del self._rows[key]
            self._row_versions.pop(key, None)
            accepted_deletes.append(key)

        ok = not errors and not conflicts
        accepted = DataChanges(
            updates=tuple(accepted_updates),
            inserts=tuple(accepted_inserts),
            deletes=tuple(accepted_deletes),
            dataset_version=self._dataset_version,
        )
        if ok and self._audit_hook is not None:
            self._audit_hook(accepted)
        return DataSaveResult(
            ok=ok,
            accepted=accepted if ok else None,
            normalized=list(copy.deepcopy(list(self._rows.values()))),
            errors=tuple(errors),
            conflicts=tuple(conflicts),
            version=self._dataset_version,
        )


class AsyncInMemoryDataSource:
    """Async wrapper around InMemoryDataSource."""

    def __init__(self, inner: InMemoryDataSource) -> None:
        self._inner = inner

    async def fetch(self, query: DataQuery) -> DataPage[dict[str, Any]]:
        return self._inner.fetch(query)

    async def apply(self, changes: DataChanges[dict[str, Any]]) -> DataSaveResult[dict[str, Any]]:
        return self._inner.apply(changes)
