"""Data-source protocols and typed change contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar, cast, runtime_checkable

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
    filters: Mapping[str, JsonValue] = field(default_factory=lambda: dict[str, JsonValue]())
    projection: tuple[str, ...] | None = None
    search: str | None = None
    locale: str | None = None
    allowlisted_sort_fields: frozenset[str] | None = None
    allowlisted_filter_fields: frozenset[str] | None = None
    allowlisted_projection_fields: frozenset[str] | None = None

    def validated(self, *, max_page_size: int = DEFAULT_MAX_PAGE_SIZE) -> DataQuery:
        offset: Any = self.offset
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            raise ValueError("DataQuery.offset must be an integer >= 0")
        if (
            not isinstance(cast(Any, max_page_size), int)
            or isinstance(max_page_size, bool)
            or max_page_size < 1
        ):
            raise ValueError("max_page_size must be an integer >= 1")
        limit = self.limit
        if not isinstance(cast(Any, limit), int) or isinstance(limit, bool) or limit < 1:
            raise ValueError("DataQuery.limit must be an integer >= 1")
        capped = min(limit, max_page_size, HARD_MAX_PAGE_SIZE)
        if capped < 1:
            raise ValueError("DataQuery.limit must be >= 1 after capping")
        sort = self.sort
        for name, direction in sort:
            if direction not in ("asc", "desc"):
                raise ValueError(f"Invalid sort direction {direction!r}")
            allow = self.allowlisted_sort_fields
            if allow is not None and name not in allow:
                raise ValueError(f"Sort field {name!r} is not allowlisted")
        filters = dict(self.filters)
        if self.allowlisted_filter_fields is not None:
            for name in filters:
                if name not in self.allowlisted_filter_fields:
                    raise ValueError(f"Filter field {name!r} is not allowlisted")
        projection = self.projection
        if projection is not None and self.allowlisted_projection_fields is not None:
            for name in projection:
                if name not in self.allowlisted_projection_fields:
                    raise ValueError(f"Projection field {name!r} is not allowlisted")
        return DataQuery(
            offset=self.offset,
            limit=capped,
            cursor=self.cursor,
            sort=sort,
            filters=filters,
            projection=projection,
            search=self.search,
            locale=self.locale,
            allowlisted_sort_fields=self.allowlisted_sort_fields,
            allowlisted_filter_fields=self.allowlisted_filter_fields,
            allowlisted_projection_fields=self.allowlisted_projection_fields,
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
    display: str | None = None
    writable: bool | None = None
    format: str | None = None


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
