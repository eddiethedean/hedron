"""Named resource/connection registry over host DI and lifespan.

Owned per-app via ``app.state.hedron_connections`` — not a process-global locator.
Secret values stay as opaque refs/strings; Hedron does not store a secret manager.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable, Mapping
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from typing import Any, Literal

from fastapi import FastAPI, Request

ConnectionKind = Literal["sqlalchemy", "snowflake", "custom"]

__all__ = [
    "ConnectionKind",
    "ConnectionRegistry",
    "ConnectionSpec",
    "bind_connection_fixture",
    "connection_dependency",
    "get_connection",
    "install_connections",
    "snowflake_connection_factory",
    "sqlalchemy_connection_factory",
]


@dataclass(frozen=True, slots=True)
class ConnectionSpec:
    """Named connection metadata (secrets remain opaque refs/strings)."""

    name: str
    kind: ConnectionKind = "custom"
    config: Mapping[str, Any] = field(default_factory=dict)
    healthcheck: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a non-empty string")
        if self.kind not in {"sqlalchemy", "snowflake", "custom"}:
            raise ValueError(
                f"kind must be 'sqlalchemy', 'snowflake', or 'custom'; got {self.kind!r}"
            )
        if not isinstance(self.config, Mapping):
            raise ValueError("config must be a mapping")
        if self.healthcheck is not None and (
            not isinstance(self.healthcheck, str) or not self.healthcheck.strip()
        ):
            raise ValueError("healthcheck must be a non-empty string when set")


def _dispose_instance(instance: Any) -> None:
    for attr in ("close", "dispose", "shutdown"):
        method = getattr(instance, attr, None)
        if callable(method):
            with suppress(Exception):
                method()
            return


class ConnectionRegistry:
    """App-owned named connection cache with health/reset semantics."""

    def __init__(self) -> None:
        self._specs: dict[str, ConnectionSpec] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._healthchecks: dict[str, Callable[[Any], bool]] = {}
        self._instances: dict[str, Any] = {}
        self._secret_refs: dict[str, Mapping[str, str]] = {}

    def register(
        self,
        name: str,
        factory: Callable[[], Any],
        *,
        kind: ConnectionKind = "custom",
        secret_refs: Mapping[str, str] | None = None,
        config: Mapping[str, Any] | None = None,
        healthcheck: Callable[[Any], bool] | None = None,
        healthcheck_name: str | None = None,
    ) -> ConnectionSpec:
        """Register a lazy factory under ``name`` (replaces prior registration)."""
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if not callable(factory):
            raise TypeError("factory must be callable")
        check_name = healthcheck_name
        if check_name is None and healthcheck is not None:
            check_name = getattr(healthcheck, "__name__", None)
            if not isinstance(check_name, str) or check_name in {"<lambda>", "<locals>"}:
                check_name = "healthcheck"
        merged: dict[str, Any] = dict(config or {})
        if secret_refs:
            # Opaque refs only — values are labels/paths, not live secrets.
            merged.setdefault("secret_refs", dict(secret_refs))
        spec = ConnectionSpec(
            name=name,
            kind=kind,
            config=merged,
            healthcheck=check_name,
        )
        # Drop any cached instance from a prior registration of the same name.
        if name in self._instances:
            _dispose_instance(self._instances.pop(name))
        self._specs[name] = spec
        self._factories[name] = factory
        self._secret_refs[name] = dict(secret_refs or {})
        if healthcheck is not None:
            self._healthchecks[name] = healthcheck
        else:
            self._healthchecks.pop(name, None)
        return spec

    def spec(self, name: str) -> ConnectionSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"unknown connection {name!r}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._specs)

    def get(self, name: str) -> Any:
        """Return a cached instance, creating it via the registered factory once."""
        if name not in self._factories:
            raise KeyError(f"unknown connection {name!r}")
        if name not in self._instances:
            self._instances[name] = self._factories[name]()
        return self._instances[name]

    def health(self, name: str) -> bool:
        """Run the registered healthcheck (or ``True`` when none is configured)."""
        if name not in self._factories:
            raise KeyError(f"unknown connection {name!r}")
        try:
            instance = self.get(name)
        except Exception:
            return False
        check = self._healthchecks.get(name)
        if check is None:
            return True
        try:
            return bool(check(instance))
        except Exception:
            return False

    def reset(self, name: str) -> None:
        """Dispose the cached instance so the next ``get`` recreates it."""
        if name not in self._factories:
            raise KeyError(f"unknown connection {name!r}")
        if name in self._instances:
            _dispose_instance(self._instances.pop(name))

    def close_all(self) -> None:
        """Dispose every cached instance (typically from app lifespan shutdown)."""
        for name in list(self._instances):
            _dispose_instance(self._instances.pop(name))


def install_connections(app: FastAPI, registry: ConnectionRegistry) -> ConnectionRegistry:
    """Attach ``registry`` to ``app.state.hedron_connections`` and close on shutdown."""
    app.state.hedron_connections = registry
    previous = app.router.lifespan_context

    @asynccontextmanager
    async def _connections_lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
        try:
            async with previous(app_):
                yield
        finally:
            registry.close_all()

    app.router.lifespan_context = _connections_lifespan
    return registry


def get_connection(request: Request, name: str) -> Any:
    """Resolve a named connection from the request's app registry."""
    registry = getattr(request.app.state, "hedron_connections", None)
    if not isinstance(registry, ConnectionRegistry):
        raise RuntimeError(
            "ConnectionRegistry not installed; call install_connections(app, registry) first"
        )
    return registry.get(name)


def connection_dependency(name: str) -> Callable[[Request], Any]:
    """FastAPI ``Depends`` factory for a named connection."""

    def _dependency(request: Request) -> Any:
        return get_connection(request, name)

    _dependency.__name__ = f"connection_{name}"
    _dependency.__hedron_connection__ = name  # type: ignore[attr-defined]
    return _dependency


def bind_connection_fixture(
    registry: ConnectionRegistry,
    fixture: Any,
    *,
    factory: Callable[[], Any] | None = None,
    healthcheck: Callable[[Any], bool] | None = None,
) -> ConnectionSpec:
    """Map a :class:`~hedron_core.testing.fixtures.NamedConnectionFixture` onto ``registry``.

    The fixture ``name`` becomes the registry key. When ``factory`` is omitted, a stub
    factory returns a mapping of provider/dsn/options for scenario tests.
    """
    name = getattr(fixture, "name", None)
    provider = getattr(fixture, "provider", None)
    if not isinstance(name, str) or not name.strip():
        raise TypeError("fixture must expose a non-empty string name")
    if not isinstance(provider, str) or not provider.strip():
        raise TypeError("fixture must expose a non-empty string provider")

    kind: ConnectionKind = "custom"
    lowered = provider.lower()
    if "sqlalchemy" in lowered or lowered in {"sa", "sql", "postgres", "postgresql", "sqlite"}:
        kind = "sqlalchemy"
    elif "snowflake" in lowered:
        kind = "snowflake"

    dsn = getattr(fixture, "dsn", None)
    options = getattr(fixture, "options", {}) or {}
    config: dict[str, Any] = {"provider": provider, **dict(options)}
    secret_refs: dict[str, str] = {}
    if isinstance(dsn, str) and dsn.strip():
        # DSN is treated as an opaque secret ref for config/redaction, not expanded here.
        secret_refs["dsn"] = dsn
        config["dsn"] = dsn

    if factory is None:

        def _stub() -> dict[str, Any]:
            return {
                "name": name,
                "provider": provider,
                "dsn": dsn,
                "options": dict(options),
            }

        factory = _stub

    return registry.register(
        name,
        factory,
        kind=kind,
        secret_refs=secret_refs or None,
        config=config,
        healthcheck=healthcheck,
    )


def sqlalchemy_connection_factory(
    url_or_engine: Any,
    *,
    statement: Any | None = None,
    session_factory: Callable[[], Any] | None = None,
    **source_kwargs: Any,
) -> Callable[[], Any]:
    """Lazy factory for a SQLAlchemy Engine or :class:`SQLAlchemyDataSource`.

    Without ``statement``, returns ``url_or_engine`` when it already looks like an
    engine, otherwise builds one via ``sqlalchemy.create_engine``. With ``statement``,
    lazy-imports ``hedron_data`` and returns a :class:`SQLAlchemyDataSource`.
    """

    def _factory() -> Any:
        if statement is not None:
            from hedron_data.sqlalchemy_source import SQLAlchemyDataSource

            if session_factory is not None:
                sf = session_factory
            else:
                engine = url_or_engine
                if isinstance(url_or_engine, str) or not hasattr(url_or_engine, "connect"):
                    from sqlalchemy import create_engine

                    engine = create_engine(url_or_engine)

                def sf() -> Any:
                    return engine.connect()

            return SQLAlchemyDataSource(
                session_factory=sf,
                statement=statement,
                **source_kwargs,
            )

        if not isinstance(url_or_engine, str) and hasattr(url_or_engine, "connect"):
            return url_or_engine
        from sqlalchemy import create_engine

        return create_engine(url_or_engine)

    return _factory


def snowflake_connection_factory(
    *,
    connection_factory: Callable[[], Any] | None = None,
    statement: str | None = None,
    connect_kwargs: Mapping[str, Any] | None = None,
    **source_kwargs: Any,
) -> Callable[[], Any]:
    """Lazy factory for a Snowflake connection or :class:`SnowflakeDataSource`.

    With ``statement``, wraps :class:`~hedron_data.snowflake_source.SnowflakeDataSource`.
    Without it, returns a live connection from ``connection_factory`` or
    ``snowflake.connector.connect(**connect_kwargs)``.
    """
    connect_kwargs = dict(connect_kwargs or {})

    def _connect() -> Any:
        if connection_factory is not None:
            return connection_factory()
        import snowflake.connector  # type: ignore[import-not-found]

        return snowflake.connector.connect(**connect_kwargs)

    def _factory() -> Any:
        if statement is not None:
            from hedron_data.snowflake_source import SnowflakeDataSource

            return SnowflakeDataSource(
                connection_factory=_connect if connection_factory is None else connection_factory,
                statement=statement,
                **source_kwargs,
            )
        return _connect()

    return _factory
