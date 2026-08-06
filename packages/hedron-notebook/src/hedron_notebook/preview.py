"""Notebook preview: local ASGI server with iframe / external-link modes."""

from __future__ import annotations

import ipaddress
import secrets
import socket
import threading
import warnings
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import quote, urlencode

__all__ = [
    "NotebookPreview",
    "PreviewServer",
    "start_preview",
]

_LOOPBACK_NAMES = frozenset({"localhost", "127.0.0.1", "::1", "0:0:0:0:0:0:0:1"})


class PreviewServer(Protocol):
    """Minimal server contract; inject a fake for unit tests."""

    @property
    def port(self) -> int: ...

    def start(self) -> None: ...

    def shutdown(self) -> None: ...


def _is_loopback_host(host: str) -> bool:
    normalized = host.strip().lower().strip("[]")
    if normalized in _LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def _pick_free_port(host: str) -> int:
    family = socket.AF_INET6 if ":" in host and not host.startswith("127.") else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def _normalize_root_path(root_path: str) -> str:
    if not root_path:
        return ""
    path = root_path if root_path.startswith("/") else f"/{root_path}"
    return path.rstrip("/")


@dataclass
class _UvicornThreadServer:
    """Background uvicorn server used when no fake server is injected."""

    app: Any
    host: str
    port: int
    root_path: str = ""
    _server: Any = field(default=None, init=False, repr=False)
    _thread: threading.Thread | None = field(default=None, init=False, repr=False)
    _started: threading.Event = field(default_factory=threading.Event, init=False, repr=False)

    def start(self) -> None:
        try:
            import uvicorn
        except ImportError as exc:  # pragma: no cover - exercised when uvicorn absent
            raise RuntimeError(
                "uvicorn is required to start a notebook preview server. "
                "Install hedron-notebook[server] or inject a PreviewServer."
            ) from exc

        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            root_path=self.root_path or "",
            log_level="warning",
            access_log=False,
        )
        server = uvicorn.Server(config)
        self._server = server

        def _run() -> None:
            self._started.set()
            server.run()

        thread = threading.Thread(
            target=_run,
            name="hedron-notebook-preview",
            daemon=True,
        )
        self._thread = thread
        thread.start()
        if not self._started.wait(timeout=5.0):
            raise RuntimeError("Notebook preview server failed to start")

    def shutdown(self) -> None:
        server = self._server
        if server is not None:
            server.should_exit = True
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=5.0)
        self._server = None
        self._thread = None


@dataclass
class NotebookPreview:
    """Handle for a running notebook preview session."""

    host: str
    port: int
    token: str
    root_path: str = ""
    iframe: bool = True
    width: str = "100%"
    height: str = "600"
    hosted_warning: bool = False
    _server: PreviewServer | None = field(default=None, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    @property
    def url(self) -> str:
        return self.external_url()

    def external_url(self) -> str:
        root = _normalize_root_path(self.root_path)
        host = self.host
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        query = urlencode({"hedron_preview_token": self.token})
        return f"http://{host}:{self.port}{root}/?{query}"

    def iframe_html(self, *, width: str | None = None, height: str | None = None) -> str:
        w = width if width is not None else self.width
        h = height if height is not None else self.height
        src = quote(self.external_url(), safe=":/?&=#%[]")
        return (
            f'<iframe src="{src}" width="{w}" height="{h}" '
            'title="Hedron notebook preview" '
            'sandbox="allow-scripts allow-same-origin allow-forms allow-popups"></iframe>'
        )

    def shutdown(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._server is not None:
            self._server.shutdown()


def start_preview(
    app: Any,
    *,
    host: str = "127.0.0.1",
    port: int = 0,
    root_path: str = "",
    iframe: bool = True,
    width: str = "100%",
    height: str = "600",
    server: PreviewServer | None = None,
    token: str | None = None,
) -> NotebookPreview:
    """Start a development preview for ``app``.

    Parameters
    ----------
    app:
        ASGI application (typically a Hedron/FastAPI app).
    host, port, root_path:
        Bind address, TCP port (``0`` = ephemeral), and optional proxy prefix.
    iframe:
        Preferred display mode hint (iframe vs external link).
    server:
        Optional injectable :class:`PreviewServer` for unit tests. When omitted,
        uvicorn is started in a background thread (requires ``uvicorn``).
    token:
        Optional fixed session token (tests); otherwise a random unguessable token.
    """
    hosted_warning = not _is_loopback_host(host)
    if hosted_warning:
        warnings.warn(
            (
                f"hedron-notebook preview is binding to non-loopback host {host!r}. "
                "This is intended for localhost development only; hosted or publicly "
                "reachable notebooks risk token leakage and open ports."
            ),
            UserWarning,
            stacklevel=2,
        )

    bind_port = port if port else (server.port if server is not None else _pick_free_port(host))
    session_token = token if token is not None else secrets.token_urlsafe(32)

    if server is None:
        server = _UvicornThreadServer(
            app=app,
            host=host,
            port=bind_port,
            root_path=_normalize_root_path(root_path),
        )
    else:
        bind_port = server.port

    preview = NotebookPreview(
        host=host,
        port=bind_port,
        token=session_token,
        root_path=root_path,
        iframe=iframe,
        width=width,
        height=height,
        hosted_warning=hosted_warning,
        _server=server,
    )
    server.start()
    return preview
