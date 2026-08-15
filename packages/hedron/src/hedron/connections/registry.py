"""Named resource/connection registry over host DI and lifespan."""

from __future__ import annotations

import logging
import threading
from collections.abc import AsyncGenerator, Callable, Mapping
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass, field
from typing import Literal, Protocol, TypeVar, cast

from fastapi import FastAPI, Request

ConnectionKind = Literal["sqlalchemy", "snowflake", "custom"]
T = TypeVar("T")
_logger = logging.getLogger("hedron.connections")

__all__ = [
    "ClosableConnection",
    "ConnectionKind",
    "ConnectionRegistry",
    "ConnectionSpec",
    "bind_connection_fixture",
    "connection_dependency",
    "get_connection",
    "install_connections",
]


class ClosableConnection(Protocol):
    """Optional dispose surface probed by sync/async close helpers.

    Host connection objects need not implement this Protocol explicitly; the
    registry looks for ``close`` / ``dispose`` / ``shutdown`` / ``aclose`` by
    attribute. Declared for documentation and structural typing.
    """

    def close(self) -> object: ...


@dataclass(frozen=True, slots=True)
class ConnectionSpec:
    """Named connection metadata (secrets remain opaque refs/strings).

    ``config`` holds host-defined opaque values (DSN refs, provider labels).
    Live secret material must not be stored here — use ``secret_refs`` labels.
    """

    name: str
    kind: ConnectionKind = "custom"
    # Host-defined opaque config (DSN refs, provider labels, etc.).
    config: Mapping[str, object] = field(default_factory=dict)
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


def _dispose_instance(instance: object) -> None:
    for attr in ("close", "dispose", "shutdown"):
        method = getattr(instance, attr, None)
        if callable(method):
            result = method()
            if hasattr(result, "__await__"):
                # Sync dispose cannot await — fail closed so callers use close_all_async.
                with suppress(Exception):
                    close = getattr(result, "close", None)
                    if callable(close):
                        close()
                raise RuntimeError(
                    "Connection dispose returned an awaitable from the sync path; "
                    "use close_all_async() / lifespan async shutdown instead."
                )
            return


async def _dispose_instance_async(instance: object) -> None:
    errors: list[BaseException] = []
    for attr in ("close", "dispose", "shutdown", "aclose"):
        method = getattr(instance, attr, None)
        if callable(method):
            try:
                result = method()
                if hasattr(result, "__await__"):
                    await result  # type: ignore[misc]  # duck-typed awaitable from host close()
            except Exception as exc:  # noqa: BLE001 — aggregate then fail closed
                errors.append(exc)
            else:
                return
    if errors:
        raise RuntimeError(
            f"Connection dispose failed with {len(errors)} error(s): {errors[0]!r}"
        ) from errors[0]


class ConnectionRegistry:
    """App-owned named connection cache with health/reset semantics."""

    def __init__(self) -> None:
        self._specs: dict[str, ConnectionSpec] = {}
        self._factories: dict[str, Callable[[], object]] = {}
        self._healthchecks: dict[str, Callable[[object], bool]] = {}
        self._instances: dict[str, object] = {}
        self._secret_refs: dict[str, Mapping[str, str]] = {}
        self._lock = threading.RLock()

    def register(
        self,
        name: str,
        factory: Callable[[], T],
        *,
        kind: ConnectionKind = "custom",
        secret_refs: Mapping[str, str] | None = None,
        config: Mapping[str, object] | None = None,
        healthcheck: Callable[[T], bool] | None = None,
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
        merged: dict[str, object] = dict(config or {})
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
            # Heterogeneous registry stores checks as object→bool after registration.
            self._healthchecks[name] = cast(Callable[[object], bool], healthcheck)
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

    def get(self, name: str) -> object:
        """Return a cached instance, creating it via the registered factory once."""
        with self._lock:
            if name not in self._factories:
                raise KeyError(f"unknown connection {name!r}")
            if name not in self._instances:
                self._instances[name] = self._factories[name]()
            return self._instances[name]

    def health(self, name: str) -> bool:
        """Run the registered healthcheck (or ``True`` when none is configured).

        Factory or healthcheck failures return ``False`` and are logged so ops
        can distinguish unhealthy connections from a quiet miss.
        """
        if name not in self._factories:
            raise KeyError(f"unknown connection {name!r}")
        try:
            instance = self.get(name)
        except Exception:
            _logger.exception("Connection %r factory failed during health check", name)
            return False
        check = self._healthchecks.get(name)
        if check is None:
            return True
        try:
            return bool(check(instance))
        except Exception:
            _logger.exception("Connection %r healthcheck raised", name)
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

    async def close_all_async(self) -> None:
        """Awaitable dispose for async connection closes during lifespan shutdown."""
        for name in list(self._instances):
            await _dispose_instance_async(self._instances.pop(name))


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
            await registry.close_all_async()

    app.router.lifespan_context = _connections_lifespan
    return registry


def get_connection(request: Request, name: str) -> object:
    """Resolve a named connection from the request's app registry."""
    registry = getattr(request.app.state, "hedron_connections", None)
    if not isinstance(registry, ConnectionRegistry):
        raise RuntimeError(
            "ConnectionRegistry not installed; call install_connections(app, registry) first"
        )
    return registry.get(name)


def connection_dependency(name: str) -> Callable[[Request], object]:
    """FastAPI ``Depends`` factory for a named connection."""

    def _dependency(request: Request) -> object:
        return get_connection(request, name)

    _dependency.__name__ = f"connection_{name}"
    _dependency.__hedron_connection__ = name  # type: ignore[attr-defined]  # FastAPI dep marker
    return _dependency


def bind_connection_fixture(
    registry: ConnectionRegistry,
    fixture: object,
    *,
    factory: Callable[[], object] | None = None,
    healthcheck: Callable[[object], bool] | None = None,
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
    config: dict[str, object] = {"provider": provider, **dict(options)}
    secret_refs: dict[str, str] = {}
    if isinstance(dsn, str) and dsn.strip():
        # DSN is treated as an opaque secret ref for config/redaction, not expanded here.
        secret_refs["dsn"] = dsn
        config["dsn"] = dsn

    if factory is None:

        def _stub() -> dict[str, object]:
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
