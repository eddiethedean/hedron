"""Explicit Edron data-workspace vocabulary over :mod:`hedron_data`.

The facade in this module owns no rows, transactions, authorization state, or
audit store.  It validates and lowers small author-facing values to the native
Hedron data contracts that continue to own paging, editing, rendering, and
concurrency behavior.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeVar, cast

from edron.errors import BindingError
from hedron_core.typing_aliases import JsonValue
from hedron_data import (
    HARD_MAX_PAGE_SIZE,
    CellUpdate,
    Column,
    DataChanges,
    DataQuery,
    DataSaveResult,
    DataTable,
    FieldError,
    InMemoryDataSource,
    SQLAlchemyDataSource,
    normalize_rows,
)
from hedron_data import (
    DataEditor as NativeDataEditor,
)
from hedron_data import (
    DataPage as NativeDataPage,
)
from hedron_data import (
    DataWorkspace as NativeDataWorkspace,
)
from hedron_data import (
    DataWorkspacePolicy as NativeDataWorkspacePolicy,
)

Row = dict[str, JsonValue]
T = TypeVar("T")
ModelT = TypeVar("ModelT")
EditAuthorizer = Callable[..., bool]
EditValidator = Callable[..., Sequence[FieldError | str] | None]
AuditSink = Callable[["AuditEvent"], None]

DEFAULT_PAGE_SIZE = 25
DEFAULT_MAX_PAGE_SIZE = 100
MAX_EDIT_OPERATIONS = 500
MAX_SELECTION_SIZE = 500


def _bounded_text(value: object | None, *, limit: int = 160) -> str | None:
    if value is None:
        return None
    return str(value)[:limit]


@dataclass(frozen=True, slots=True)
class PageRequest:
    """A bounded, allowlisted request for one workspace page."""

    offset: int = 0
    limit: int = DEFAULT_PAGE_SIZE
    sort: tuple[tuple[str, Literal["asc", "desc"]], ...] = ()
    filters: Mapping[str, JsonValue] = field(default_factory=dict)
    search: str | None = None
    projection: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class CellEdit:
    """One typed cell mutation with an optional optimistic row revision."""

    row_key: str
    field: str
    value: JsonValue
    row_version: str | None = None

    def __post_init__(self) -> None:
        if not self.row_key:
            raise ValueError("CellEdit.row_key must be non-empty")
        if not self.field:
            raise ValueError("CellEdit.field must be non-empty")


@dataclass(frozen=True, slots=True)
class EditIntent:
    """Explicit application mutation intent; never persisted by Edron itself."""

    updates: tuple[CellEdit, ...] = ()
    inserts: tuple[Mapping[str, JsonValue], ...] = ()
    deletes: tuple[str, ...] = ()
    dataset_version: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        operations = len(self.updates) + len(self.inserts) + len(self.deletes)
        if operations < 1:
            raise ValueError("EditIntent must contain at least one operation")
        if operations > MAX_EDIT_OPERATIONS:
            raise ValueError(f"EditIntent is limited to {MAX_EDIT_OPERATIONS} operations")
        if any(not key for key in self.deletes):
            raise ValueError("EditIntent delete keys must be non-empty")
        object.__setattr__(self, "reason", _bounded_text(self.reason))

    @classmethod
    def from_native(cls, changes: DataChanges[Row]) -> EditIntent:
        return cls(
            updates=tuple(
                CellEdit(item.row_key, item.field, item.value, item.row_version)
                for item in changes.updates
            ),
            inserts=tuple(dict(row) for row in changes.inserts),
            deletes=tuple(changes.deletes),
            dataset_version=changes.dataset_version,
        )

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> EditIntent:
        """Validate the finite JSON shape emitted by the native editor host."""
        raw_updates = payload.get("updates") or ()
        raw_inserts = payload.get("inserts") or ()
        raw_deletes = payload.get("deletes") or ()
        for name, value in (
            ("updates", raw_updates),
            ("inserts", raw_inserts),
            ("deletes", raw_deletes),
        ):
            if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
                raise ValueError(f"{name} must be an array")
        updates: list[CellEdit] = []
        for item in raw_updates:
            if not isinstance(item, Mapping):
                raise ValueError("each update must be an object")
            updates.append(
                CellEdit(
                    row_key=str(item.get("row_key", "")),
                    field=str(item.get("field", "")),
                    value=cast(JsonValue, item.get("value")),
                    row_version=(
                        str(item["row_version"]) if item.get("row_version") is not None else None
                    ),
                )
            )
        inserts: list[Mapping[str, JsonValue]] = []
        for item in raw_inserts:
            if not isinstance(item, Mapping):
                raise ValueError("each insert must be an object")
            inserts.append({str(key): cast(JsonValue, value) for key, value in item.items()})
        return cls(
            updates=tuple(updates),
            inserts=tuple(inserts),
            deletes=tuple(str(key) for key in raw_deletes),
            dataset_version=(
                str(payload["dataset_version"])
                if payload.get("dataset_version") is not None
                else None
            ),
            reason=_bounded_text(payload.get("reason")),
        )

    def native(self) -> DataChanges[Row]:
        return DataChanges(
            updates=tuple(
                CellUpdate(item.row_key, item.field, item.value, item.row_version)
                for item in self.updates
            ),
            inserts=tuple(dict(row) for row in self.inserts),
            deletes=self.deletes,
            dataset_version=self.dataset_version,
        )


@dataclass(frozen=True, slots=True)
class EditPolicy:
    """Application-owned authorization, validation, and audit hooks.

    Mutation is deny-by-default: ``authorize`` is required at execution time,
    writable fields must be named, and insert/delete operations must be enabled
    separately.  The audit hook receives metadata only, never cell values.
    """

    writable_fields: frozenset[str] = frozenset()
    authorize: EditAuthorizer | None = None
    validate: EditValidator | None = None
    audit: AuditSink | None = None
    allow_inserts: bool = False
    allow_deletes: bool = False


@dataclass(frozen=True, slots=True)
class AuditEvent:
    workspace: str
    outcome: Literal["accepted", "rejected", "conflict"]
    update_count: int
    insert_count: int
    delete_count: int
    principal: str | None = None
    reason: str | None = None
    version: str | None = None
    error_count: int = 0
    conflict_count: int = 0


@dataclass(frozen=True, slots=True)
class DataSelection:
    """A bounded set of stable row identities."""

    row_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.row_keys) > MAX_SELECTION_SIZE:
            raise ValueError(f"selection is limited to {MAX_SELECTION_SIZE} rows")
        if len(set(self.row_keys)) != len(self.row_keys):
            raise ValueError("selection row keys must be unique")
        if any(not key for key in self.row_keys):
            raise ValueError("selection row keys must be non-empty")


@dataclass(frozen=True, slots=True)
class DataExport:
    """A bounded export produced from an already-authorized page."""

    content: bytes
    filename: str
    media_type: str
    row_count: int


@dataclass(frozen=True, slots=True)
class WorkspacePage:
    """One native page plus safe facts useful to Edron application code."""

    native: NativeDataPage[Row]
    request: PageRequest
    selected: DataSelection = DataSelection()

    @property
    def rows(self) -> tuple[Row, ...]:
        return tuple(dict(cast(Mapping[str, JsonValue], row)) for row in self.native.rows)

    @property
    def total(self) -> int | None:
        return self.native.total

    @property
    def next_offset(self) -> int | None:
        return self.native.next_offset


class DataSource(Generic[T]):
    """Small adapter facade around one explicit native data source."""

    def __init__(self, native: Any, *, adapter: str = "custom") -> None:
        if not callable(getattr(native, "fetch", None)) or not callable(
            getattr(native, "apply", None)
        ):
            raise TypeError("DataSource requires explicit fetch() and apply() methods")
        self._native = native
        self.adapter = adapter

    @property
    def native(self) -> Any:
        return self._native

    @classmethod
    def in_memory(
        cls,
        rows: object,
        *,
        key_field: str = "id",
        columns: Sequence[Column] = (),
        writable_fields: Sequence[str] = (),
        sort_fields: Sequence[str] = (),
        filter_fields: Sequence[str] = (),
        projection_fields: Sequence[str] = (),
        search_fields: Sequence[str] = (),
        version: str = "1",
    ) -> DataSource[Row]:
        normalized = normalize_rows(rows)
        schema = tuple(column.to_schema() for column in columns)
        native = InMemoryDataSource(
            normalized,
            key_field=key_field,
            schema=schema,
            writable_fields=frozenset(writable_fields),
            allowlisted_sort_fields=frozenset(sort_fields),
            allowlisted_filter_fields=frozenset(filter_fields),
            allowlisted_projection_fields=frozenset(projection_fields),
            search_fields=search_fields,
            version=version,
        )
        return DataSource(native, adapter="memory")

    @classmethod
    def dataframe(cls, frame: object, **kwargs: Any) -> DataSource[Row]:
        """Adapt a bounded pandas, Polars, or PyArrow value via native Narwhals."""
        module = type(frame).__module__.split(".")[0]
        if module not in {"pandas", "polars", "pyarrow", "narwhals"}:
            raise TypeError("dataframe() expects pandas, Polars, PyArrow, or Narwhals data")
        source = DataSource.in_memory(frame, **kwargs)
        source.adapter = module
        return source

    @classmethod
    def sqlalchemy(
        cls,
        *,
        session_factory: Callable[[], Any],
        statement: object,
        row_key: str = "id",
        to_row: Callable[[object], T] | None = None,
        apply_changes: Callable[[Any, DataChanges[T]], DataSaveResult[T]] | None = None,
        columns: Sequence[Column] = (),
        search_fields: Sequence[str] = (),
    ) -> DataSource[T]:
        native = SQLAlchemyDataSource(
            session_factory=session_factory,
            statement=statement,
            row_key=row_key,
            to_row=to_row,
            apply_changes=apply_changes,
            schema=tuple(column.to_schema() for column in columns),
            search_fields=search_fields,
        )
        return cls(native, adapter="sqlalchemy")

    def fetch(self, query: DataQuery) -> NativeDataPage[T]:
        result = self._native.fetch(query)
        if inspect.isawaitable(result):
            if inspect.iscoroutine(result):
                result.close()
            raise TypeError("async sources must be awaited before constructing an Edron workspace")
        if not isinstance(result, NativeDataPage):
            raise TypeError("source.fetch() must return hedron_data.DataPage")
        return result

    def apply(self, changes: DataChanges[T]) -> DataSaveResult[T]:
        result = self._native.apply(changes)
        if inspect.isawaitable(result):
            if inspect.iscoroutine(result):
                result.close()
            raise TypeError("async sources require an explicit application action")
        if not isinstance(result, DataSaveResult):
            raise TypeError("source.apply() must return hedron_data.DataSaveResult")
        return result


def _invoke_hook(hook: Callable[..., Any], **values: Any) -> Any:
    try:
        signature = inspect.signature(hook)
    except (TypeError, ValueError):
        return hook(**values)
    if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in signature.parameters.values()):
        return hook(**values)
    accepted = {
        name: values[name]
        for name, parameter in signature.parameters.items()
        if name in values
        and parameter.kind
        in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
    }
    try:
        signature.bind(**accepted)
    except TypeError:
        return False
    return hook(**accepted)


class DataWorkspace:
    """Request-bounded read/filter/edit workspace over one native source."""

    def __init__(
        self,
        name: str,
        *,
        source: DataSource[Row] | Any,
        columns: Sequence[Column],
        key_field: str = "id",
        page_size: int = DEFAULT_PAGE_SIZE,
        max_page_size: int = DEFAULT_MAX_PAGE_SIZE,
        sort_fields: Sequence[str] | None = None,
        filter_fields: Sequence[str] | None = None,
        projection_fields: Sequence[str] | None = None,
        edit: EditPolicy | None = None,
    ) -> None:
        if not name or not name.replace("-", "_").isidentifier():
            raise ValueError("workspace name must be a non-empty identifier")
        if not columns:
            raise ValueError("workspace columns must be explicit")
        if page_size < 1 or max_page_size < 1 or page_size > max_page_size:
            raise ValueError("page_size must be between 1 and max_page_size")
        if max_page_size > HARD_MAX_PAGE_SIZE:
            raise ValueError(f"max_page_size cannot exceed {HARD_MAX_PAGE_SIZE}")
        column_names = [column.name for column in columns]
        if len(column_names) != len(set(column_names)):
            raise ValueError("workspace column names must be unique")
        if key_field not in column_names:
            raise ValueError("workspace key_field must be present in columns")
        self.name = name
        self.source = source if isinstance(source, DataSource) else DataSource(source)
        self.columns = tuple(columns)
        self.key_field = key_field
        self.page_size = page_size
        self.max_page_size = max_page_size
        self.edit_policy = edit
        self.save_endpoint: str | None = None
        self.sort_fields = frozenset(
            sort_fields if sort_fields is not None else (c.name for c in columns if c.sortable)
        )
        self.filter_fields = frozenset(
            filter_fields
            if filter_fields is not None
            else (c.name for c in columns if c.filterable)
        )
        visible = frozenset(c.name for c in columns if not c.hidden and not c.secret)
        self.projection_fields = frozenset(
            projection_fields if projection_fields is not None else visible
        )
        for label, fields in (
            ("sort", self.sort_fields),
            ("filter", self.filter_fields),
            ("projection", self.projection_fields),
        ):
            unknown = fields - set(column_names)
            if unknown:
                raise ValueError(f"unknown {label} fields: {sorted(unknown)!r}")
        secret = {c.name for c in columns if c.secret}
        if self.projection_fields & secret:
            raise ValueError("secret fields cannot be projection fields")
        if key_field not in self.projection_fields:
            raise ValueError("workspace key_field must be a projection field")
        if edit is not None:
            unknown_writable = edit.writable_fields - set(column_names)
            if unknown_writable:
                raise ValueError(f"unknown writable fields: {sorted(unknown_writable)!r}")
            forbidden = {
                c.name
                for c in columns
                if c.read_only or c.hidden or c.secret or c.writable is not True
            }
            if edit.writable_fields & forbidden:
                raise ValueError("writable fields must be explicitly writable visible columns")

    def request_from(self, values: Mapping[str, Any]) -> PageRequest:
        """Parse ordinary query parameters using only workspace allowlists."""
        raw_sort = values.get("sort")
        sort: tuple[tuple[str, Literal["asc", "desc"]], ...] = ()
        if raw_sort:
            field_name, _sep, raw_direction = str(raw_sort).partition(":")
            direction = raw_direction or "asc"
            if direction not in {"asc", "desc"}:
                raise BindingError("invalid workspace sort", code="EDRON_DATA_QUERY")
            sort = ((field_name, cast(Literal["asc", "desc"], direction)),)
        filters = {
            name: cast(JsonValue, values[name])
            for name in self.filter_fields
            if values.get(name) not in (None, "")
        }
        try:
            offset = int(values.get("offset", 0) or 0)
            limit = int(values.get("limit", self.page_size) or self.page_size)
        except (TypeError, ValueError) as exc:
            raise BindingError("invalid workspace paging", code="EDRON_DATA_QUERY") from exc
        return PageRequest(
            offset=offset,
            limit=limit,
            sort=sort,
            filters=filters,
            search=_bounded_text(values.get("q"), limit=240),
        )

    def _native_query(self, request: PageRequest) -> DataQuery:
        query = DataQuery(
            offset=request.offset,
            limit=request.limit,
            sort=cast(tuple[tuple[str, str], ...], request.sort),
            filters=dict(request.filters),
            search=request.search,
            projection=request.projection or tuple(sorted(self.projection_fields)),
            allowlisted_sort_fields=self.sort_fields,
            allowlisted_filter_fields=self.filter_fields,
            allowlisted_projection_fields=self.projection_fields,
        )
        try:
            return query.validated(max_page_size=self.max_page_size)
        except ValueError as exc:
            raise BindingError(str(exc), code="EDRON_DATA_QUERY") from exc

    def page(
        self,
        request: PageRequest | None = None,
        *,
        selection: DataSelection | None = None,
    ) -> WorkspacePage:
        request = request or PageRequest(limit=self.page_size)
        native = self.source.fetch(self._native_query(request))
        rows: list[Row] = []
        for row in native.rows:
            if isinstance(row, Mapping):
                rows.append(dict(cast(Mapping[str, JsonValue], row)))
            else:
                dump = getattr(row, "model_dump", None)
                if not callable(dump):
                    raise TypeError("workspace rows must be mappings or Pydantic models")
                rows.append(dict(cast(Mapping[str, JsonValue], dump())))
        normalized = NativeDataPage(
            rows=rows,
            schema=native.schema,
            total=native.total,
            next_offset=native.next_offset,
            next_cursor=native.next_cursor,
            version=native.version,
        )
        chosen = selection or DataSelection()
        available = {str(row.get(self.key_field, "")) for row in rows}
        if not set(chosen.row_keys) <= available:
            raise BindingError(
                "selection contains rows outside the authorized page", code="EDRON_DATA_SELECTION"
            )
        return WorkspacePage(normalized, request, chosen)

    def table(self, page: WorkspacePage, *, caption: str | None = None) -> DataTable:
        return DataTable(
            page=page.native,
            query=self._native_query(page.request),
            columns=self.columns,
            caption=caption or self.name.replace("_", " ").title(),
            page_size=self.page_size,
        )

    def editor(
        self,
        page: WorkspacePage,
        *,
        caption: str | None = None,
        save_endpoint: str | None = None,
        save_mode: Literal["batch", "row", "cell"] = "batch",
    ) -> NativeDataEditor:
        if self.edit_policy is None:
            raise BindingError("workspace is read-only", code="EDRON_DATA_READ_ONLY")
        return NativeDataEditor(
            page=page.native,
            source=self.source.native,
            columns=self.columns,
            key=self.name,
            key_field=self.key_field,
            on_save=lambda changes: self.apply(EditIntent.from_native(changes)),
            page_size=self.page_size,
            caption=caption or self.name.replace("_", " ").title(),
            save_endpoint=save_endpoint or self.save_endpoint,
            save_mode=save_mode,
            allow_deletes=self.edit_policy.allow_deletes,
        )

    def _policy_errors(self, intent: EditIntent) -> list[FieldError]:
        policy = self.edit_policy
        if policy is None:
            return [FieldError(None, None, "Workspace is read-only")]
        errors: list[FieldError] = []
        for item in intent.updates:
            if item.field not in policy.writable_fields:
                errors.append(FieldError(item.row_key, item.field, "Field is not writable"))
        if intent.inserts and not policy.allow_inserts:
            errors.append(FieldError(None, None, "Inserts are not authorized"))
        if intent.deletes and not policy.allow_deletes:
            errors.extend(
                FieldError(key, None, "Deletes are not authorized") for key in intent.deletes
            )
        for row in intent.inserts:
            forged = set(row) - policy.writable_fields - {self.key_field}
            errors.extend(FieldError(None, name, "Field is not writable") for name in forged)
        return errors

    def apply(self, intent: EditIntent, *, principal: object | None = None) -> DataSaveResult[Row]:
        """Authorize, validate, persist through the native source, then audit."""
        policy = self.edit_policy
        errors = self._policy_errors(intent)
        if policy is None or policy.authorize is None:
            errors.append(FieldError(None, None, "Explicit edit authorization is required"))
        elif not bool(
            _invoke_hook(policy.authorize, intent=intent, principal=principal, workspace=self)
        ):
            errors.append(FieldError(None, None, "Edit is not authorized"))
        if not errors and policy is not None and policy.validate is not None:
            findings = _invoke_hook(
                policy.validate, intent=intent, principal=principal, workspace=self
            )
            for finding in findings or ():
                errors.append(
                    finding
                    if isinstance(finding, FieldError)
                    else FieldError(None, None, _bounded_text(finding, limit=240) or "Invalid edit")
                )
        if errors:
            result: DataSaveResult[Row] = DataSaveResult(ok=False, errors=tuple(errors))
        else:
            result = self.source.apply(intent.native())
        if policy is not None and policy.audit is not None:
            outcome: Literal["accepted", "rejected", "conflict"] = (
                "conflict" if result.conflicts else "accepted" if result.ok else "rejected"
            )
            policy.audit(
                AuditEvent(
                    workspace=self.name,
                    outcome=outcome,
                    update_count=len(intent.updates),
                    insert_count=len(intent.inserts),
                    delete_count=len(intent.deletes),
                    principal=_bounded_text(principal),
                    reason=intent.reason,
                    version=result.version,
                    error_count=len(result.errors),
                    conflict_count=len(result.conflicts),
                )
            )
        return result

    def export_csv(
        self,
        page: WorkspacePage,
        *,
        selection: DataSelection | None = None,
        filename: str | None = None,
    ) -> DataExport:
        chosen = selection or page.selected
        rows = list(page.rows)
        if chosen.row_keys:
            wanted = set(chosen.row_keys)
            rows = [row for row in rows if str(row.get(self.key_field, "")) in wanted]
            if len(rows) != len(wanted):
                raise BindingError(
                    "export selection contains rows outside the authorized page",
                    code="EDRON_DATA_SELECTION",
                )
        table = DataTable(rows, columns=self.columns)
        content = table.to_csv().encode("utf-8")
        return DataExport(
            content=content,
            filename=filename or f"{self.name}.csv",
            media_type="text/csv; charset=utf-8",
            row_count=len(rows),
        )

    def diagnostics(self) -> Mapping[str, Any]:
        return {
            "schema": "edron.data-workspace/1",
            "name": self.name,
            "adapter": self.source.adapter,
            "key_field": self.key_field,
            "page_size": self.page_size,
            "max_page_size": self.max_page_size,
            "sortable": sorted(self.sort_fields),
            "filterable": sorted(self.filter_fields),
            "projectable": sorted(self.projection_fields),
            "editable": self.edit_policy is not None,
            "writable": sorted(self.edit_policy.writable_fields) if self.edit_policy else [],
            "authorization": "explicit"
            if self.edit_policy and self.edit_policy.authorize
            else "deny",
            "validation": "explicit"
            if self.edit_policy and self.edit_policy.validate
            else "native",
            "audit": "explicit"
            if self.edit_policy and self.edit_policy.audit
            else "application-owned",
            "save_endpoint": self.save_endpoint,
        }

    @staticmethod
    def principal_from_request(request: Any) -> object | None:
        """Read the host-established principal without creating identity state."""
        scope = getattr(request, "scope", None)
        if isinstance(scope, Mapping):
            principal = scope.get("user")
            if principal not in (None, False, ""):
                return principal
            session = scope.get("session")
            if isinstance(session, Mapping):
                for key in ("user", "username", "principal", "sub", "user_id", "_user_id"):
                    value = session.get(key)
                    if value not in (None, False, ""):
                        return value
        return None

    def native_feature(
        self,
        *,
        model: type[ModelT],
        can_read: Callable[..., bool],
        can_create: Callable[..., bool] | None = None,
        can_edit: Callable[..., bool] | None = None,
    ) -> NativeDataWorkspace[Any]:
        """Compile common CRUD composition through native ``DataWorkspace``."""
        policy = NativeDataWorkspacePolicy(
            can_read=can_read,
            can_create=can_create,
            can_edit=can_edit,
            delete="disabled",
        )
        return NativeDataWorkspace(
            self.name,
            model=cast(Any, model),
            source=self.source.native,
            policy=policy,
            key_field=self.key_field,
            columns=self.columns,
        )


__all__ = [
    "AuditEvent",
    "CellEdit",
    "Column",
    "DataExport",
    "DataSelection",
    "DataSource",
    "DataWorkspace",
    "EditIntent",
    "EditPolicy",
    "PageRequest",
    "WorkspacePage",
]
