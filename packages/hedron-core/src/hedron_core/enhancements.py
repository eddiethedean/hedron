"""Typed contracts introduced by the Phase 1.1 enhancement bundle.

These types deliberately contain presentation and transport state only. Domain
authorization, persistence, and secret storage remain owned by the application.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, Protocol, TypeVar, cast

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PrincipalContext:
    """Display-safe identity data supplied by an external provider."""

    id: str
    display_name: str | None = None
    authenticated: bool = True
    principal_type: str = "user"

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("principal id must not be empty")
        if any(token in self.id.lower() for token in ("token", "secret", "password")):
            raise ValueError("principal id must not contain credential-like values")


@dataclass(frozen=True, slots=True)
class ResourceRef:
    """Consumer-defined resource identity used for presentation decisions."""

    type: str
    id: str | None = None

    def __post_init__(self) -> None:
        if not self.type.strip():
            raise ValueError("resource type must not be empty")


class AuthorizationUIProvider(Protocol):
    """Optional provider for presentation-only authorization checks."""

    def can(
        self,
        request: Any,
        action: str,
        resource: ResourceRef | None = None,
    ) -> bool | Any: ...


async def presentation_allowed(
    provider: AuthorizationUIProvider | None,
    request: Any,
    action: str,
    resource: ResourceRef | None = None,
) -> bool:
    """Resolve a UI authorization decision safely.

    Missing providers and provider failures fail closed. The result must never
    be used as endpoint authorization.
    """

    if provider is None:
        return False
    try:
        result = provider.can(request, action, resource)
        if inspect.isawaitable(result):
            result = await result
        return bool(result)
    except Exception:  # noqa: BLE001 - provider failures must fail closed
        return False


@dataclass(frozen=True, slots=True)
class SortSpec:
    field: str
    direction: str = "asc"

    def __post_init__(self) -> None:
        if not self.field.strip() or self.direction not in {"asc", "desc"}:
            raise ValueError("sort requires a field and asc/desc direction")


@dataclass(frozen=True, slots=True)
class FilterSpec:
    field: str
    value: Any
    operator: str = "eq"

    def __post_init__(self) -> None:
        if not self.field.strip() or not self.operator.strip():
            raise ValueError("filter requires a field and operator")


@dataclass(frozen=True, slots=True)
class PageState(Generic[T]):
    """Provider-neutral offset/page or cursor response."""

    items: Sequence[T] = field(default_factory=tuple)
    total: int | None = None
    page: int | None = None
    size: int | None = None
    pages: int | None = None
    next_cursor: str | None = None
    previous_cursor: str | None = None

    def __post_init__(self) -> None:
        if self.total is not None and self.total < 0:
            raise ValueError("page total cannot be negative")
        if self.page is not None and self.page < 1:
            raise ValueError("page numbers start at one")
        if self.size is not None and self.size < 1:
            raise ValueError("page size must be positive")

    @property
    def has_next(self) -> bool:
        return self.next_cursor is not None or (
            self.pages is not None and self.page is not None and self.page < self.pages
        )

    @property
    def has_previous(self) -> bool:
        return self.previous_cursor is not None or (self.page is not None and self.page > 1)


class PaginatedDataSource(Protocol[T]):
    async def fetch(
        self,
        *,
        page: int | None = None,
        size: int | None = None,
        cursor: str | None = None,
        sort: Sequence[SortSpec] = (),
        filters: Sequence[FilterSpec] = (),
    ) -> PageState[T]: ...


async def fetch_page(
    source: PaginatedDataSource[T],
    *,
    page: int | None = None,
    size: int | None = None,
    cursor: str | None = None,
    sort: Sequence[SortSpec] = (),
    filters: Sequence[FilterSpec] = (),
) -> PageState[T]:
    """Fetch and normalize one page from any Phase 1.1 data source."""

    result = await source.fetch(page=page, size=size, cursor=cursor, sort=sort, filters=filters)
    return cast(PageState[T], normalize_page(result))


def normalize_page(value: Any) -> PageState[Any]:
    """Normalize common page/cursor response objects without importing adapters."""

    if isinstance(value, PageState):
        return cast(PageState[Any], value)
    if isinstance(value, Mapping):
        data = cast(Mapping[str, Any], value)
        items = data.get("items", data.get("data", ()))
        return PageState(
            items=tuple(items or ()),
            total=data.get("total"),
            page=data.get("page", data.get("current_page")),
            size=data.get("size", data.get("per_page")),
            pages=data.get("pages", data.get("last_page")),
            next_cursor=data.get("next_cursor", data.get("next")),
            previous_cursor=data.get("previous_cursor", data.get("previous")),
        )
    attrs: dict[str, Any] = {
        name: getattr(value, name, None)
        for name in ("items", "total", "page", "size", "pages", "next_cursor", "previous_cursor")
    }
    return PageState(
        items=tuple(attrs["items"] or ()),
        **{key: value for key, value in attrs.items() if key != "items"},
    )


class SecretOperation(str, Enum):
    KEEP = "keep"
    REPLACE = "replace"
    CLEAR = "clear"


@dataclass(frozen=True, slots=True)
class SecretUpdate:
    """Write-only secret mutation request; plaintext is never retained in repr."""

    operation: SecretOperation
    value: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.operation is SecretOperation.REPLACE and not self.value:
            raise ValueError("replace requires a non-empty new secret")
        if self.operation is not SecretOperation.REPLACE and self.value is not None:
            raise ValueError("keep and clear cannot carry a replacement value")


def resolve_secret_update(form: Mapping[str, Any], name: str) -> SecretUpdate:
    """Resolve a write-only secret field from a submitted form mapping."""

    def values(key: str) -> tuple[str, ...]:
        raw = form.get(key)
        if raw is None:
            return ()
        if isinstance(raw, (list, tuple)):
            return tuple(str(item) for item in cast(list[Any] | tuple[Any, ...], raw))
        return (str(raw),)

    if any(value in {"1", SecretOperation.CLEAR.value} for value in values(f"{name}__clear")):
        return SecretUpdate(SecretOperation.CLEAR)
    replacement = next((value for value in values(f"{name}__replacement") if value), None)
    if replacement is not None:
        return SecretUpdate(SecretOperation.REPLACE, replacement)
    operation = next(iter(values(f"{name}__operation")), SecretOperation.KEEP.value)
    return SecretUpdate(SecretOperation(operation))


@dataclass(frozen=True, slots=True)
class FormIssue:
    path: tuple[str, ...] = ()
    code: str = "invalid"
    message: str = "Invalid value"

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("form issue message must not be empty")


@dataclass(frozen=True, slots=True)
class ValidationResult:
    issues: tuple[FormIssue, ...] = ()

    @classmethod
    def from_issues(cls, issues: Sequence[FormIssue]) -> ValidationResult:
        return cls(tuple(issues))

    @property
    def valid(self) -> bool:
        return not self.issues

    def for_path(self, path: Sequence[str]) -> tuple[FormIssue, ...]:
        wanted = tuple(path)
        return tuple(issue for issue in self.issues if issue.path == wanted)


@dataclass(frozen=True, slots=True)
class FieldHelp:
    summary: str | None = None
    details: str | None = None
    example: str | None = None
    docs: str | None = None
    group: str | None = None


@dataclass(slots=True)
class DirtyScope:
    """Bounded in-memory dirty state for opt-in navigation protection."""

    name: str
    dirty: bool = False
    committed_revision: int = 0
    revision: int = 0

    def mark_changed(self) -> None:
        self.revision += 1
        self.dirty = self.revision != self.committed_revision

    def commit(self) -> None:
        self.committed_revision = self.revision
        self.dirty = False

    def reset(self) -> None:
        self.commit()

    def assert_clean(self) -> None:
        """Raise when navigation would discard unsaved work."""

        if self.dirty:
            raise RuntimeError(f"dirty scope '{self.name}' must be committed before navigation")
