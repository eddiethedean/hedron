from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeVar

from fastapi import Depends

T = TypeVar("T")
ResourceScope = Literal["request", "application"]


@dataclass
class Dependency(Generic[T]):
    provider: Callable[..., T] | None = None
    use_cache: bool = True
    name: str | None = None
    scope: Literal["function", "request"] | None = None

    def __set_name__(self, owner: type[Any], name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, instance: Any, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]
        return self

    def native(self) -> Any:
        return Depends(self.provider, use_cache=self.use_cache, scope=self.scope)


def dependency(
    provider: Callable[..., T] | None = None,
    *,
    use_cache: bool = True,
    scope: Literal["function", "request"] | None = None,
) -> Dependency[T]:
    return Dependency(provider, use_cache=use_cache, scope=scope)


@dataclass(frozen=True, slots=True)
class Resource:
    """App-owned named resource specification.

    The factory is resolved lazily by Hedron's native ``ConnectionRegistry`` and
    disposed by the host lifespan. Secret values must be represented by opaque
    references in ``secret_refs``; Edron never stores live credentials.
    """

    name: str
    factory: Callable[[], Any]
    scope: ResourceScope = "application"
    kind: Literal["sqlalchemy", "snowflake", "custom"] = "custom"
    secret_refs: Mapping[str, str] = field(default_factory=dict)
    config: Mapping[str, object] = field(default_factory=dict)
    healthcheck: Callable[[Any], bool] | None = None
    healthcheck_name: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("resource name must be a non-empty string")
        if not callable(self.factory):
            raise TypeError("resource factory must be callable")
        if self.scope not in {"request", "application"}:
            raise ValueError("resource scope must be 'request' or 'application'")
        if self.kind not in {"sqlalchemy", "snowflake", "custom"}:
            raise ValueError("resource kind must be 'sqlalchemy', 'snowflake', or 'custom'")

    def register(self, registry: Any) -> Any:
        """Register this resource in a native ``ConnectionRegistry``."""
        return registry.register(
            self.name,
            self.factory,
            kind=self.kind,
            secret_refs=self.secret_refs,
            config=self.config,
            healthcheck=self.healthcheck,
            healthcheck_name=self.healthcheck_name,
        )


def resource(
    name: str,
    factory: Callable[[], Any] | None = None,
    *,
    kind: Literal["sqlalchemy", "snowflake", "custom"] = "custom",
    scope: ResourceScope = "application",
    secret_refs: Mapping[str, str] | None = None,
    config: Mapping[str, object] | None = None,
    healthcheck: Callable[[Any], bool] | None = None,
    healthcheck_name: str | None = None,
) -> Resource | Callable[[Callable[[], Any]], Resource]:
    """Declare a reusable resource specification for ``App.resource``."""

    def build(provider: Callable[[], Any]) -> Resource:
        return Resource(
            name=name,
            factory=provider,
            scope=scope,
            kind=kind,
            secret_refs=dict(secret_refs or {}),
            config=dict(config or {}),
            healthcheck=healthcheck,
            healthcheck_name=healthcheck_name,
        )

    if factory is None:
        return build
    return build(factory)
