"""Data-source protocols and typed change contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Generic, Protocol, TypeVar, runtime_checkable

from hedron_core.typing_aliases import JsonValue

T = TypeVar("T")

DEFAULT_MAX_PAGE_SIZE = 100
HARD_MAX_PAGE_SIZE = 500


@dataclass(frozen=True, slots=True)
class DataQuery:
    """Bounded page/cursor query with allowlisted sort and filter expressions."""

    offset: int = 0
    limit: int = 25
    cursor: str | None = None
    sort: tuple[tuple[str, str], ...] = ()
    filters: Mapping[str, JsonValue] = field(default_factory=dict)
    projection: tuple[str, ...] | None = None
    search: str | None = None
    locale: str | None = None
    allowlisted_sort_fields: frozenset[str] | None = None
    allowlisted_filter_fields: frozenset[str] | None = None

    def validated(self, *, max_page_size: int = DEFAULT_MAX_PAGE_SIZE) -> DataQuery:
        if self.offset < 0:
            raise ValueError("DataQuery.offset must be >= 0")
        limit = self.limit
        if limit < 1:
            raise ValueError("DataQuery.limit must be >= 1")
        capped = min(limit, max_page_size, HARD_MAX_PAGE_SIZE)
        sort = self.sort
        if self.allowlisted_sort_fields is not None:
            for name, direction in sort:
                if name not in self.allowlisted_sort_fields:
                    raise ValueError(f"Sort field {name!r} is not allowlisted")
                if direction not in ("asc", "desc"):
                    raise ValueError(f"Invalid sort direction {direction!r}")
        filters = dict(self.filters)
        if self.allowlisted_filter_fields is not None:
            for name in filters:
                if name not in self.allowlisted_filter_fields:
                    raise ValueError(f"Filter field {name!r} is not allowlisted")
        return DataQuery(
            offset=self.offset,
            limit=capped,
            cursor=self.cursor,
            sort=sort,
            filters=filters,
            projection=self.projection,
            search=self.search,
            locale=self.locale,
            allowlisted_sort_fields=self.allowlisted_sort_fields,
            allowlisted_filter_fields=self.allowlisted_filter_fields,
        )


@dataclass(frozen=True, slots=True)
class ColumnSchema:
    name: str
    label: str
    editor: str = "text"
    read_only: bool = False
    hidden: bool = False
    secret: bool = False
    sortable: bool = False
    filterable: bool = False
    choices: tuple[JsonValue, ...] | None = None
    width: str | int | None = None


@dataclass(frozen=True, slots=True)
class DataPage(Generic[T]):
    rows: Sequence[T]
    schema: tuple[ColumnSchema, ...] = ()
    total: int | None = None
    next_offset: int | None = None
    next_cursor: str | None = None
    version: str | None = None


@dataclass(frozen=True, slots=True)
class CellUpdate:
    row_key: str
    field: str
    value: JsonValue
    row_version: str | None = None


@dataclass(frozen=True, slots=True)
class DataChanges(Generic[T]):
    updates: tuple[CellUpdate, ...] = ()
    inserts: tuple[T, ...] = ()
    deletes: tuple[str, ...] = ()
    dataset_version: str | None = None


@dataclass(frozen=True, slots=True)
class FieldError:
    row_key: str | None
    field: str | None
    message: str


@dataclass(frozen=True, slots=True)
class Conflict:
    row_key: str
    field: str | None
    server_value: JsonValue
    client_value: JsonValue
    message: str = "Stale update"


@dataclass(frozen=True, slots=True)
class DataSaveResult(Generic[T]):
    ok: bool
    accepted: DataChanges[T] | None = None
    normalized: Sequence[T] = ()
    errors: tuple[FieldError, ...] = ()
    conflicts: tuple[Conflict, ...] = ()
    version: str | None = None


@runtime_checkable
class DataEditorSource(Protocol[T]):
    """Fetch and apply protocol for editable tabular sources."""

    def fetch(self, query: DataQuery) -> DataPage[T]: ...

    def apply(self, changes: DataChanges[T]) -> DataSaveResult[T]: ...


@runtime_checkable
class AsyncDataEditorSource(Protocol[T]):
    async def fetch(self, query: DataQuery) -> DataPage[T]: ...

    async def apply(self, changes: DataChanges[T]) -> DataSaveResult[T]: ...


DEFAULT_MAX_VIZ_ROWS = 10_000
DEFAULT_MAX_VIZ_PAYLOAD_BYTES = 1_000_000


@runtime_checkable
class VisualizationSource(Protocol[T]):
    """Load bounded tabular pages for chart and map adapters."""

    def load(self, query: DataQuery) -> DataPage[T]: ...


@runtime_checkable
class AsyncVisualizationSource(Protocol[T]):
    async def load(self, query: DataQuery) -> DataPage[T]: ...
