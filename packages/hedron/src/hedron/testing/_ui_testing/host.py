"""Spawned ASGI hosting for synthetic Hedron browser tests.

This module deliberately has no module-level Uvicorn or pytest dependency. The
server and factory are imported inside the spawned child so registries, event
loops, overrides, and database resources belong to that child process.
"""

from __future__ import annotations

import asyncio
import contextlib
import importlib
import ipaddress

# The repository's typings/json.pyi provides the precise object-returning JSON API.
import json  # pyright: ignore[reportMissingModuleSource]
import math
import multiprocessing
import os
import re
import socket
import sys
import threading
import time
from collections.abc import Callable, Mapping
from multiprocessing.process import BaseProcess
from pathlib import Path
from typing import Literal, Protocol, cast, final
from urllib.parse import urlsplit

from starlette.types import ASGIApp, Message, Receive, Scope, Send
from typing_extensions import override

from hedron_core.mount import normalize_mount_path

_MAX_CONFIG_BYTES = 64 * 1024
_HOST = "127.0.0.1"


class ManagedHostError(RuntimeError):
    """A managed ASGI app failed to start, serve, or stop cleanly."""


class ManagedHostCleanupError(ManagedHostError):
    """A managed ASGI child required forced termination or missed cleanup."""


def validate_factory_config(config: Mapping[str, object] | None) -> str:
    """Encode bounded JSON-compatible synthetic factory configuration."""
    value = dict(config or {})
    _validate_json_value(value, depth=0)
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        decoded = json.loads(encoded)
    except (TypeError, ValueError, RecursionError) as exc:
        raise TypeError("factory config must contain only bounded JSON-compatible values") from exc
    if not isinstance(decoded, dict):
        raise TypeError("factory config must be a JSON object")
    if len(encoded.encode("ascii")) > _MAX_CONFIG_BYTES:
        raise ValueError(f"factory config exceeds {_MAX_CONFIG_BYTES} bytes")
    return encoded


def validate_factory_ref(factory: object) -> tuple[str, str]:
    """Validate the importable ``package.module:factory`` reference."""
    if not isinstance(factory, str) or len(factory) > 512 or ":" not in factory:
        raise ValueError("factory must be an importable 'module:attribute' reference")
    module, attribute = factory.split(":", 1)
    parts = module.split(".") + attribute.split(".")
    if not module or not attribute or any(not part.isidentifier() for part in parts):
        raise ValueError("factory must be an importable 'module:attribute' reference")
    return module, attribute


def validate_root_path(root_path: object | None) -> str:
    """Return a normalized ASGI root path without query or traversal syntax."""
    if root_path in (None, "", "/"):
        return ""
    if not isinstance(root_path, str) or len(root_path) > 512:
        raise ValueError("root_path must be a short absolute URL path")
    parsed = urlsplit(root_path)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("root_path must not contain a scheme, host, query, or fragment")
    if not root_path.startswith("/") or "\\" in root_path:
        raise ValueError("root_path must be an absolute URL path")
    parts = root_path.split("/")
    if any(part in {".", ".."} for part in parts):
        raise ValueError("root_path must not contain dot segments")
    normalized = normalize_mount_path(root_path)
    if not normalized:
        raise ValueError("root_path contains an unsupported mount path")
    return normalized


def validate_loopback_url(url: object) -> tuple[str, str]:
    """Validate a caller-owned HTTP(S) URL with a literal loopback IP host."""
    if not isinstance(url, str) or len(url) > 4096:
        raise ValueError("base_url must be a literal-loopback HTTP(S) URL")
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("base_url must be a literal-loopback HTTP(S) URL")
    if parsed.username is not None or parsed.password is not None or parsed.fragment:
        raise ValueError("base_url must not include credentials or a fragment")
    try:
        address = ipaddress.ip_address(parsed.hostname)
    except ValueError as exc:
        raise ValueError("base_url host must be a literal loopback IP address") from exc
    if not address.is_loopback:
        raise ValueError("base_url host must be a literal loopback IP address")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("base_url must contain a valid port") from exc
    scheme = parsed.scheme.lower()
    authority = f"[{address.compressed}]" if address.version == 6 else address.compressed
    default_port = 80 if scheme == "http" else 443
    if port is not None and port != default_port:
        authority = f"{authority}:{port}"
    path = validate_root_path(parsed.path.rstrip("/"))
    if parsed.query:
        raise ValueError("base_url must not contain query values")
    return f"{scheme}://{authority}", path


def validate_origin(value: object) -> str:
    """Normalize an exact HTTP(S) origin allowlist entry."""
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError("allowed origins must be exact HTTP(S) origins")
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("allowed origins must be exact HTTP(S) origins")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("allowed origins must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("allowed origins must not contain a path, query, or fragment")
    try:
        address = ipaddress.ip_address(parsed.hostname)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("allowed origins must use a literal loopback IP address") from exc
    if not address.is_loopback:
        raise ValueError("allowed origins must use a literal loopback IP address")
    scheme = parsed.scheme.lower()
    host = address.compressed
    if address.version == 6:
        host = f"[{host}]"
    default_port = 80 if scheme == "http" else 443
    if port is not None and port != default_port:
        host = f"{host}:{port}"
    return f"{scheme}://{host}"


def _safe_exception_name(error: BaseException) -> str:
    name = type(error).__name__
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]{0,63}", name) else "Exception"


def _resolve_factory(reference: str) -> object:
    module_name, attribute_path = reference.split(":", 1)
    value: object = importlib.import_module(module_name)
    for part in attribute_path.split("."):
        value = cast(object, getattr(value, part))
    return value


class _PipeConnection(Protocol):
    def close(self) -> None: ...

    def poll(self, timeout: float = 0.0) -> bool: ...

    def recv(self) -> object: ...

    def send(self, value: object) -> None: ...


def _send(connection: _PipeConnection, lock: threading.Lock, message: dict[str, object]) -> None:
    try:
        with lock:
            connection.send(message)
    except (BrokenPipeError, EOFError, OSError):
        return


@final
class _ExceptionReportingASGI:
    """Report exception categories while preserving ASGI exception behavior."""

    def __init__(self, app: ASGIApp, connection: _PipeConnection, lock: threading.Lock) -> None:
        self._app = app
        self._connection = connection
        self._lock = lock
        self.shutdown_failed = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def reporting_send(message: Message) -> None:
            if (
                scope["type"] == "lifespan"
                and isinstance(message, dict)
                and message.get("type") == "lifespan.shutdown.failed"
            ):
                _send(
                    self._connection,
                    self._lock,
                    {"kind": "lifespan_shutdown_failed"},
                )
                self.shutdown_failed = True
            await send(message)

        try:
            await self._app(scope, receive, reporting_send)
        except Exception as exc:
            _send(
                self._connection,
                self._lock,
                {"kind": "server_exception", "exception_type": _safe_exception_name(exc)},
            )
            raise


@final
class _ScopeRootPathASGI:
    """Apply the same incoming ASGI mount scope a path-preserving proxy sends."""

    def __init__(self, app: ASGIApp, root_path: str) -> None:
        self._app = app
        self._root_path = root_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self._root_path and scope["type"] in {
            "http",
            "websocket",
        }:
            scope["root_path"] = self._root_path
            await self._app(scope, receive, send)
            return
        await self._app(scope, receive, send)


def _serve_child(
    connection: _PipeConnection,
    factory_ref: str,
    encoded_config: str,
    root_path: str,
    shutdown_timeout: float,
) -> None:
    """Multiprocessing spawn target. Keep all app/server objects child-local."""
    with Path(os.devnull).open("w", encoding="utf-8") as null_stream:
        sys.stdout = null_stream
        sys.stderr = null_stream
        lock = threading.Lock()
        listener: socket.socket | None = None
        try:
            factory_value = _resolve_factory(factory_ref)
            if not callable(factory_value):
                raise TypeError("factory attribute is not callable")
            factory = cast(Callable[[dict[str, object]], object], factory_value)
            config_value_raw: object = json.loads(encoded_config)
            if not isinstance(config_value_raw, dict):
                raise TypeError("factory config must decode to a JSON object")
            config_value = cast(dict[str, object], config_value_raw)
            app_value = factory(config_value)
            if not callable(app_value):
                raise TypeError("factory did not return an ASGI application")
            app = cast(ASGIApp, app_value)

            import uvicorn

            listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((_HOST, 0))
            listener.listen(2048)
            listener.setblocking(False)
            socket_name = cast(object, listener.getsockname())
            if not isinstance(socket_name, tuple):
                raise OSError("managed host listener returned an invalid socket address")
            socket_parts = cast(tuple[object, ...], socket_name)
            if len(socket_parts) < 2 or type(socket_parts[1]) is not int:
                raise OSError("managed host listener returned an invalid socket address")
            port = socket_parts[1]
            wrapped_app = _ExceptionReportingASGI(
                _ScopeRootPathASGI(app, root_path), connection, lock
            )
            server_config = uvicorn.Config(
                wrapped_app,
                host=_HOST,
                port=port,
                # The wrapper below installs the path-preserving proxy scope.
                # Uvicorn's option prepends root_path a second time to the raw path.
                root_path="",
                log_config=None,
                log_level="critical",
                access_log=False,
                lifespan="on",
                reload=False,
                workers=1,
                timeout_graceful_shutdown=math.ceil(shutdown_timeout),
            )

            class _ReadyServer(uvicorn.Server):
                @override
                async def startup(self, sockets: list[socket.socket] | None = None) -> None:
                    await super().startup(sockets=sockets)
                    if self.started:
                        _send(
                            connection,
                            lock,
                            {
                                "kind": "ready",
                                "host": _HOST,
                                "port": port,
                                "root_path": root_path,
                            },
                        )

            server = _ReadyServer(server_config)

            async def run_server() -> None:
                task = asyncio.create_task(server.serve(sockets=[listener]))
                try:
                    while not task.done():
                        if connection.poll():
                            try:
                                command: object = connection.recv()
                            except (EOFError, OSError):
                                server.should_exit = True
                            else:
                                if command == "stop":
                                    server.should_exit = True
                        await asyncio.sleep(0.01)
                    await task
                finally:
                    if not task.done():
                        server.should_exit = True
                        await task

            asyncio.run(run_server())
            _send(
                connection,
                lock,
                {"kind": "stopped", "lifespan_complete": not wrapped_app.shutdown_failed},
            )
        except Exception as exc:  # noqa: BLE001 — child boundary reports arbitrary app failures.
            _send(
                connection,
                lock,
                {"kind": "startup_error", "exception_type": _safe_exception_name(exc)},
            )
        finally:
            if listener is not None:
                with contextlib.suppress(OSError):
                    listener.close()
            with contextlib.suppress(OSError):
                connection.close()


class ManagedASGIHost:
    """Own one spawned ASGI process and its retained loopback listener."""

    def __init__(
        self,
        factory: str,
        *,
        config: Mapping[str, object] | None = None,
        root_path: str | None = None,
        startup_timeout: float = 15.0,
        shutdown_timeout: float = 5.0,
    ) -> None:
        _ = validate_factory_ref(factory)
        self._factory: str = factory
        self._config: str = validate_factory_config(config)
        self._root_path: str = validate_root_path(root_path)
        self._startup_timeout: float = _validate_timeout("startup_timeout", startup_timeout)
        self._shutdown_timeout: float = _validate_timeout("shutdown_timeout", shutdown_timeout)
        self._process: BaseProcess | None = None
        self._connection: _PipeConnection | None = None
        self._messages: list[dict[str, object]] = []
        self._origin: str | None = None
        self._started: bool = False
        self._closed: bool = False
        self._cleanup_error: str | None = None

    @property
    def origin(self) -> str:
        """The actual child-bound loopback origin, available after ``start``."""
        if self._origin is None:
            raise ManagedHostError("managed host has not completed startup")
        return self._origin

    @property
    def base_url(self) -> str:
        """The server origin combined with its configured root path."""
        return f"{self.origin}{self._root_path}"

    @property
    def cleanup_error(self) -> str | None:
        return self._cleanup_error

    def start(self) -> str:
        """Spawn the app, wait for lifespan-ready, and return its base URL."""
        if self._started:
            return self.base_url
        if self._closed:
            raise ManagedHostError("managed host cannot be restarted after close")
        context = multiprocessing.get_context("spawn")
        parent, child = context.Pipe(duplex=True)
        process = context.Process(
            target=_serve_child,
            args=(child, self._factory, self._config, self._root_path, self._shutdown_timeout),
            name="hedron-ui-asgi",
            daemon=False,
        )
        try:
            process.start()
        except BaseException:
            parent.close()
            child.close()
            raise
        child.close()
        self._process = process
        self._connection = cast(_PipeConnection, cast(object, parent))
        deadline = time.monotonic() + self._startup_timeout
        try:
            while time.monotonic() < deadline:
                self._collect_messages(timeout=min(0.05, max(0.0, deadline - time.monotonic())))
                for message in self._messages:
                    if message.get("kind") == "startup_error":
                        error_type = message.get("exception_type", "Exception")
                        raise ManagedHostError(f"managed app startup failed ({error_type})")
                    if message.get("kind") == "ready":
                        host = message.get("host")
                        port = message.get("port")
                        if host != _HOST or not isinstance(port, int) or not (0 < port < 65536):
                            raise ManagedHostError("managed app returned invalid readiness data")
                        self._origin = f"http://{host}:{port}"
                        self._started = True
                        return self.base_url
                if not process.is_alive():
                    raise ManagedHostError("managed app exited before readiness")
            raise ManagedHostError("managed app startup timed out")
        except (Exception, KeyboardInterrupt, SystemExit) as primary:
            try:
                self.close()
            except (Exception, KeyboardInterrupt, SystemExit) as cleanup:  # noqa: BLE001
                # Keep the startup failure primary while retaining bounded cleanup evidence.
                primary.add_note(f"managed host cleanup failed ({_safe_exception_name(cleanup)})")
            raise

    def drain_messages(self) -> tuple[dict[str, object], ...]:
        """Return and clear bounded structured child-side observations."""
        self._collect_messages(timeout=0.0)
        messages = tuple(self._messages)
        self._messages.clear()
        return messages

    def close(self) -> None:
        """Request graceful lifespan shutdown, then enforce bounded process cleanup."""
        if self._closed:
            if self._cleanup_error is not None:
                raise ManagedHostCleanupError(self._cleanup_error)
            return
        self._closed = True
        process = self._process
        connection = self._connection
        if process is None:
            return
        stopped = any(
            message.get("kind") == "stopped" and message.get("lifespan_complete") is True
            for message in self._messages
        )
        if process.is_alive() and connection is not None:
            with contextlib.suppress(BrokenPipeError, EOFError, OSError):
                connection.send("stop")
            deadline = time.monotonic() + self._shutdown_timeout + 1.0
            while process.is_alive() and time.monotonic() < deadline:
                self._collect_messages(timeout=min(0.05, max(0.0, deadline - time.monotonic())))
                if any(
                    message.get("kind") == "stopped" and message.get("lifespan_complete") is True
                    for message in self._messages
                ):
                    stopped = True
                process.join(timeout=0)
        if process.is_alive():
            process.terminate()
            process.join(timeout=1.0)
            if process.is_alive() and hasattr(process, "kill"):
                process.kill()
                process.join(timeout=1.0)
            self._cleanup_error = "managed app required forced process termination"
        if process.is_alive():
            self._cleanup_error = "managed app process did not exit after terminate/kill"
        if connection is not None:
            self._collect_messages(timeout=0.0)
            stopped = stopped or any(
                message.get("kind") == "stopped" and message.get("lifespan_complete") is True
                for message in self._messages
            )
            with contextlib.suppress(OSError):
                connection.close()
        if not self._cleanup_error and not process.is_alive() and not stopped and self._started:
            self._cleanup_error = "managed app exited without confirmed lifespan shutdown"
        elif not self._started and process.exitcode not in (0, None):
            # Startup failures are reported by start(); process cleanup itself is complete.
            self._cleanup_error = None
        with contextlib.suppress(ValueError, OSError):
            process.close()
        if self._cleanup_error is not None:
            raise ManagedHostCleanupError(self._cleanup_error)

    def _collect_messages(self, *, timeout: float) -> None:
        connection = self._connection
        if connection is None:
            return
        try:
            if connection.poll(timeout):
                message: object = connection.recv()
                if isinstance(message, dict):
                    typed_message = cast(dict[str, object], message)
                    if isinstance(typed_message.get("kind"), str):
                        self._messages.append(typed_message)
                    if len(self._messages) > 512:
                        del self._messages[: len(self._messages) - 512]
        except (EOFError, OSError):
            return


def _validate_timeout(name: Literal["startup_timeout", "shutdown_timeout"], value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a finite positive number")
    result = float(value)
    if not 0.05 <= result <= 300:
        raise ValueError(f"{name} must be between 0.05 and 300 seconds")
    return result


def _validate_json_value(value: object, *, depth: int) -> None:
    if depth > 32:
        raise ValueError("factory config exceeds the maximum JSON nesting depth")
    if value is None or isinstance(value, (str, bool, int, float)):
        return
    if isinstance(value, list):
        items = cast(list[object], value)
        if len(items) > 10000:
            raise ValueError("factory config contains too many array items")
        for item in items:
            _validate_json_value(item, depth=depth + 1)
        return
    if isinstance(value, dict):
        items = cast(dict[object, object], value)
        if len(items) > 10000:
            raise ValueError("factory config contains too many object keys")
        for key, item in items.items():
            if not isinstance(key, str):
                raise TypeError("factory config object keys must be strings")
            _validate_json_value(item, depth=depth + 1)
        return
    raise TypeError("factory config must contain only JSON-compatible values")
