"""In-memory paged DataEditorSource for tests and reference apps."""

from __future__ import annotations

import copy
import threading
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence

from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonValue
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


def _row_key(row: Mapping[str, JsonValue], key_field: str) -> str:
    if key_field not in row:
        raise error(
            "HED-DATA-0010",
            title="Row missing key field",
            explanation=f"Row is missing required key field {key_field!r}.",
            remediation="Ensure every row includes the configured key_field.",
        )
    return str(row[key_field])


def _sort_key(value: JsonValue) -> tuple[int, str, float | str]:
    """Deterministic cross-type ordering for heterogeneous JSON cells (#116)."""
    if value is None:
        return (0, "", "")
    if isinstance(value, bool):
        return (1, "bool", "1" if value else "0")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return (2, "number", float(value))
    if isinstance(value, str):
        return (3, "str", value)
    return (4, type(value).__name__, str(value))


class InMemoryDataSource:
    """Sync in-memory source with optimistic concurrency via per-row versions.

    Concurrent ``apply`` / ``fetch`` calls on one instance are serialized with an
    instance lock so a successful ``ok=True`` result always means the accepted
    changes are present (no lost updates under threaded hosts).
    """

    def __init__(
        self,
        rows: Sequence[Mapping[str, JsonValue]],
        *,
        key_field: str = "id",
        schema: Sequence[ColumnSchema] = (),
        writable_fields: frozenset[str] | None = None,
        allowlisted_sort_fields: frozenset[str] | None = None,
        allowlisted_filter_fields: frozenset[str] | None = None,
        allowlisted_projection_fields: frozenset[str] | None = None,
        search_fields: Sequence[str] = (),
        version: str = "1",
        audit_hook: Callable[[DataChanges[dict[str, JsonValue]]], None] | None = None,
    ) -> None:
        self._key_field = key_field
        built: dict[str, dict[str, JsonValue]] = {}
        for index, row in enumerate(rows):
            if key_field not in row:
                raise error(
                    "HED-DATA-0010",
                    title="Row missing key field",
                    explanation=(
                        f"Row at index {index} is missing required key field {key_field!r}."
                    ),
                    remediation="Ensure every row includes the configured key_field.",
                )
            try:
                key = _row_key(row, key_field)
            except (TypeError, ValueError) as exc:
                raise error(
                    "HED-DATA-0010",
                    title="Unusable row key",
                    explanation=f"Row at index {index} has an unusable key: {exc}.",
                    remediation="Use hashable, stringifiable key_field values.",
                ) from exc
            if key in built:
                raise error(
                    "HED-DATA-0011",
                    title="Duplicate row key",
                    explanation=(
                        f"Duplicate key {key!r} at index {index} (key_field={key_field!r})."
                    ),
                    remediation="Provide unique identities before constructing the source.",
                )
            built[key] = {str(k): v for k, v in row.items()}
        self._rows = built
        self._row_versions: dict[str, str] = {k: version for k in self._rows}
        self._schema = tuple(schema)
        # Deny-by-default: omitted writable_fields means no field is writable.
        self._writable = frozenset() if writable_fields is None else writable_fields
        self._sort_allow = (
            frozenset[str]() if allowlisted_sort_fields is None else allowlisted_sort_fields
        )
        self._filter_allow = (
            frozenset[str]() if allowlisted_filter_fields is None else allowlisted_filter_fields
        )
        self._projection_allow = (
            frozenset[str]()
            if allowlisted_projection_fields is None
            else allowlisted_projection_fields
        )
        self._secret_fields = frozenset(c.name for c in self._schema if c.secret)
        self._search_fields = tuple(search_fields)
        self._dataset_version = version
        self._audit_hook = audit_hook
        self._version_counter = int(version) if version.isdigit() else 1
        self._lock = threading.RLock()

    @property
    def dataset_version(self) -> str:
        with self._lock:
            return self._dataset_version

    def _next_version(self) -> str:
        self._version_counter += 1
        self._dataset_version = str(self._version_counter)
        return self._dataset_version

    def fetch(self, query: DataQuery) -> DataPage[dict[str, JsonValue]]:
        with self._lock:
            return self._fetch_unlocked(query)

    def _effective_allow(
        self, query_allow: frozenset[str] | None, source_allow: frozenset[str]
    ) -> frozenset[str]:
        # Empty source allowlist is deny-all; clients must not widen it (#573).
        if not source_allow:
            return source_allow
        if query_allow is None:
            return source_allow
        return query_allow & source_allow

    def _fetch_unlocked(self, query: DataQuery) -> DataPage[dict[str, JsonValue]]:
        # Secrets are never projection-allowlisted (#574).
        projection_allow = (
            self._effective_allow(
                query.allowlisted_projection_fields,
                self._projection_allow - self._secret_fields,
            )
            if query.projection is not None
            else None
        )
        q = DataQuery(
            offset=query.offset,
            limit=query.limit,
            cursor=query.cursor,
            sort=query.sort,
            filters=query.filters,
            projection=query.projection,
            search=query.search,
            locale=query.locale,
            allowlisted_sort_fields=self._effective_allow(
                query.allowlisted_sort_fields, self._sort_allow
            ),
            allowlisted_filter_fields=self._effective_allow(
                query.allowlisted_filter_fields, self._filter_allow
            ),
            allowlisted_projection_fields=projection_allow,
        ).validated()
        items = list(self._rows.values())
        for field_name, expected in q.filters.items():
            items = [r for r in items if r.get(field_name) == expected]
        if q.search:
            if not self._search_fields:
                raise error(
                    "HED-DATA-0012",
                    title="In-memory search requires an allowlist",
                    explanation="Deny-by-default: searchable fields must be declared.",
                    remediation="Set InMemoryDataSource.search_fields.",
                )
            needle = q.search.lower()
            items = [
                r
                for r in items
                if any(
                    needle in str(r.get(field_name, "")).lower()
                    for field_name in self._search_fields
                    if r.get(field_name) is not None
                )
            ]
        for field_name, direction in reversed(q.sort):
            items.sort(
                key=lambda r, f=field_name: _sort_key(r.get(f)),  # type: ignore[arg-type]
                reverse=direction == "desc",
            )
        total = len(items)
        page = items[q.offset : q.offset + q.limit]
        if q.projection:
            if self._secret_fields.intersection(q.projection):
                raise error(
                    "HED-DATA-0012",
                    title="Secret columns cannot be projected",
                    explanation=(
                        "ColumnSchema(secret=True) fields are not readable through "
                        "DataQuery.projection."
                    ),
                    remediation="Omit secret fields from projection or use an app-owned bridge.",
                )
            page = [{k: r.get(k) for k in q.projection} for r in page]
        next_offset = q.offset + q.limit if q.offset + q.limit < total else None
        return DataPage(
            rows=page,
            schema=self._schema,
            total=total,
            next_offset=next_offset,
            version=self._dataset_version,
        )

    def apply(
        self, changes: DataChanges[dict[str, JsonValue]]
    ) -> DataSaveResult[dict[str, JsonValue]]:
        with self._lock:
            return self._apply_unlocked(changes)

    def _apply_unlocked(
        self, changes: DataChanges[dict[str, JsonValue]]
    ) -> DataSaveResult[dict[str, JsonValue]]:
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

        # Validate against a working copy so a failed batch never partially mutates.
        rows = copy.deepcopy(self._rows)
        row_versions = dict(self._row_versions)
        version_counter = self._version_counter
        dataset_version = self._dataset_version

        def next_version() -> str:
            nonlocal version_counter, dataset_version
            version_counter += 1
            dataset_version = str(version_counter)
            return dataset_version

        errors: list[FieldError] = []
        conflicts: list[Conflict] = []
        accepted_updates: list[CellUpdate] = []
        accepted_inserts: list[dict[str, JsonValue]] = []
        accepted_deletes: list[str] = []

        # Group updates by row so multi-field edits share one pre-batch version (#113).
        grouped: dict[str, list[CellUpdate]] = defaultdict(list)
        for upd in changes.updates:
            grouped[upd.row_key].append(upd)

        for row_key, updates in grouped.items():
            submitted_versions = {u.row_version for u in updates if u.row_version is not None}
            if len(submitted_versions) > 1:
                conflicts.append(
                    Conflict(
                        row_key=row_key,
                        field=None,
                        server_value=row_versions.get(row_key),
                        client_value=",".join(sorted(str(v) for v in submitted_versions)),
                        message="Inconsistent row versions in batch",
                    )
                )
                continue
            submitted = next(iter(submitted_versions), None)
            row = rows.get(row_key)
            if row is None:
                for upd in updates:
                    errors.append(
                        FieldError(row_key=upd.row_key, field=upd.field, message="Unknown row")
                    )
                continue
            current_ver = row_versions.get(row_key)
            if submitted is not None and submitted != current_ver:
                for upd in updates:
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

            row_errors = False
            for upd in updates:
                if upd.field not in self._writable:
                    errors.append(
                        FieldError(
                            row_key=upd.row_key,
                            field=upd.field,
                            message="Field is not writable",
                        )
                    )
                    row_errors = True
                    continue
                schema_col = next((c for c in self._schema if c.name == upd.field), None)
                if schema_col is not None and (
                    schema_col.read_only or schema_col.hidden or schema_col.secret
                ):
                    errors.append(
                        FieldError(
                            row_key=upd.row_key,
                            field=upd.field,
                            message="Field is read-only, hidden, or secret",
                        )
                    )
                    row_errors = True
                    continue
            if row_errors:
                continue

            for upd in updates:
                row[upd.field] = upd.value
                accepted_updates.append(upd)
            row_versions[row_key] = next_version()

        for inserted in changes.inserts:
            row = dict(inserted)
            try:
                key = _row_key(row, self._key_field)
            except KeyError:
                errors.append(
                    FieldError(
                        row_key="",
                        field=self._key_field,
                        message="Inserted row missing key field",
                    )
                )
                continue
            if key in rows:
                errors.append(
                    FieldError(row_key=key, field=self._key_field, message="Duplicate key")
                )
                continue
            for field_name in list(row):
                if field_name != self._key_field and field_name not in self._writable:
                    del row[field_name]
            rows[key] = row
            row_versions[key] = next_version()
            accepted_inserts.append(row)

        for key in changes.deletes:
            if key not in rows:
                errors.append(FieldError(row_key=key, field=None, message="Unknown row"))
                continue
            del rows[key]
            row_versions.pop(key, None)
            accepted_deletes.append(key)

        ok = not errors and not conflicts
        if ok:
            self._rows = rows
            self._row_versions = row_versions
            self._version_counter = version_counter
            self._dataset_version = dataset_version
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

    async def fetch(self, query: DataQuery) -> DataPage[dict[str, JsonValue]]:
        return self._inner.fetch(query)

    async def apply(
        self, changes: DataChanges[dict[str, JsonValue]]
    ) -> DataSaveResult[dict[str, JsonValue]]:
        return self._inner.apply(changes)
