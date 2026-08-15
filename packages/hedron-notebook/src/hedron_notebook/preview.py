"""Notebook preview: local ASGI server with iframe / external-link modes."""

from __future__ import annotations

import ipaddress
import re
import secrets
import socket
import threading
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import parse_qs, quote, urlencode

__all__ = [
    "PREVIEW_TOKEN_COOKIE",
    "PREVIEW_TOKEN_HEADER",
    "PREVIEW_TOKEN_QUERY",
    "NotebookPreview",
    "PreviewServer",
    "PreviewTokenGate",
    "start_preview",
    "wrap_preview_app",
]

_LOOPBACK_NAMES = frozenset({"localhost", "127.0.0.1", "::1", "0:0:0:0:0:0:0:1"})

PREVIEW_TOKEN_QUERY = "hedron_preview_token"
PREVIEW_TOKEN_HEADER = "x-hedron-preview-token"
PREVIEW_TOKEN_COOKIE = "hedron_preview_token"


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


_ROOT_PATH_SAFE = re.compile(r"^/[A-Za-z0-9._~\-/]*$")


def _normalize_root_path(root_path: str) -> str:
    if not root_path:
        return ""
    path = root_path if root_path.startswith("/") else f"/{root_path}"
    path = path.rstrip("/")
    # Reject cookie-attribute / header injection via Path= (#174).
    if path and (
        any(ch in path for ch in (";", "\r", "\n", "\x00")) or not _ROOT_PATH_SAFE.fullmatch(path)
    ):
        raise ValueError(f"Unsafe root_path for preview cookie Path: {root_path!r}")
    return path


def _header_map(scope: MutableMapping[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_name, raw_value in scope.get("headers") or ():
        name = raw_name.decode("latin-1").lower()
        value = raw_value.decode("latin-1")
        headers[name] = value
    return headers


def _cookie_token(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None
    for part in cookie_header.split(";"):
        name, sep, value = part.strip().partition("=")
        if sep and name == PREVIEW_TOKEN_COOKIE:
            return value
    return None


def _query_token(scope: MutableMapping[str, Any]) -> str | None:
    query = scope.get("query_string") or b""
    query_text = query.decode("latin-1") if isinstance(query, bytes) else str(query)
    values = parse_qs(query_text, keep_blank_values=False).get(PREVIEW_TOKEN_QUERY) or []
    if not values:
        return None
    return values[0]


def _token_presentation(
    scope: MutableMapping[str, Any],
) -> tuple[str | None, str | None]:
    """Return ``(token, source)`` where source is ``header``, ``query``, or ``cookie``."""
    headers = _header_map(scope)
    header_token = headers.get(PREVIEW_TOKEN_HEADER)
    if header_token:
        return header_token, "header"
    query_token = _query_token(scope)
    if query_token:
        return query_token, "query"
    cookie_token = _cookie_token(headers.get("cookie"))
    if cookie_token:
        return cookie_token, "cookie"
    return None, None


def _tokens_match(expected: str, provided: str | None) -> bool:
    if provided is None or not isinstance(provided, str):
        return False
    if len(provided) != len(expected):
        # Keep a digest work unit so length mismatches are not free.
        secrets.compare_digest(expected, expected)
        return False
    return secrets.compare_digest(expected, provided)


def _set_cookie_header(token: str, *, root_path: str) -> bytes:
    path = root_path if root_path else "/"
    # HttpOnly so document JS cannot exfiltrate; SameSite=Lax keeps iframe same-site GETs.
    return f"{PREVIEW_TOKEN_COOKIE}={token}; Path={path}; HttpOnly; SameSite=Lax".encode("latin-1")


class PreviewTokenGate:
    """ASGI middleware that requires the preview session token on HTTP/WebSocket.

    The initial ``external_url()`` / iframe ``src`` carries the token as a query
    parameter. On that first authenticated response the gate sets an HttpOnly
    cookie so subsequent browser requests (static assets, HTMX, WebSockets) are
    authorized without re-attaching the query string.
    """

    def __init__(self, app: Any, token: str) -> None:
        if not token:
            raise ValueError("preview token must be non-empty")
        self.app = app
        self.token = token

    async def __call__(self, scope: MutableMapping[str, Any], receive: Any, send: Any) -> None:
        scope_type = scope.get("type")
        if scope_type == "lifespan":
            await self.app(scope, receive, send)
            return
        if scope_type not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return

        provided, source = _token_presentation(scope)
        if not _tokens_match(self.token, provided):
            if scope_type == "websocket":
                await send({"type": "websocket.close", "code": 4401})
                return
            body = b'{"detail":"Preview token required"}'
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode("ascii")),
                        (b"cache-control", b"no-store"),
                    ],
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        # Seed a session cookie when auth came from query/header so iframe
        # follow-up requests (assets, HTMX, forms) succeed automatically.
        seed_cookie = scope_type == "http" and source in {"header", "query"}
        if not seed_cookie:
            await self.app(scope, receive, send)
            return

        root_path = str(scope.get("root_path") or "")
        cookie = _set_cookie_header(self.token, root_path=root_path)
        cookie_sent = False

        async def send_with_cookie(message: MutableMapping[str, Any]) -> None:
            nonlocal cookie_sent
            if message.get("type") == "http.response.start" and not cookie_sent:
                headers = list(message.get("headers") or [])
                headers.append((b"set-cookie", cookie))
                message = {**message, "headers": headers}
                cookie_sent = True
            await send(message)

        await self.app(scope, receive, send_with_cookie)


def wrap_preview_app(app: Any, token: str) -> PreviewTokenGate:
    """Return ``app`` wrapped so requests must present ``token``."""
    return PreviewTokenGate(app, token)


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
    _app: Any = field(default=None, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    @property
    def url(self) -> str:
        return self.external_url()

    def external_url(self) -> str:
        root = _normalize_root_path(self.root_path)
        host = self.host
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        query = urlencode({PREVIEW_TOKEN_QUERY: self.token})
        return f"http://{host}:{self.port}{root}/?{query}"

    def iframe_html(self, *, width: str | None = None, height: str | None = None) -> str:
        import html as html_lib

        w = html_lib.escape(
            width if width is not None else self.width,
            quote=True,
        )
        h = html_lib.escape(
            height if height is not None else self.height,
            quote=True,
        )
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
        HTTP and WebSocket requests must present this token via the
        ``hedron_preview_token`` query parameter, ``X-Hedron-Preview-Token``
        header, or the HttpOnly ``hedron_preview_token`` cookie seeded after the
        first successful query/header auth. Missing or wrong tokens receive
        HTTP 401 / WebSocket close 4401.
    """
    hosted_warning = not _is_loopback_host(host)
    if hosted_warning:
        raise ValueError(
            f"hedron-notebook preview refuses non-loopback host {host!r}. "
            "Supported preview binds only to loopback (localhost / 127.0.0.1 / ::1). "
            "Remote or public serving is not part of the Supported API."
        )

    bind_port = port if port else (server.port if server is not None else _pick_free_port(host))
    session_token = token if token is not None else secrets.token_urlsafe(32)
    if not session_token:
        raise ValueError("preview token must be non-empty")
    gated_app = wrap_preview_app(app, session_token)

    if server is None:
        server = _UvicornThreadServer(
            app=gated_app,
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
        _app=gated_app,
    )
    server.start()
    return preview
