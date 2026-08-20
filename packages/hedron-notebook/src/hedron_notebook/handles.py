"""Display handles and bounded multi-view notebook sessions.

A :class:`DisplayHandle` is the notebook-side view of one preview or rendered
fragment. It supports the four explicit operations authors need in a cell
(``update``, ``snapshot``, ``open_in_browser``, ``close``) plus static HTML /
text / image fallbacks for saved notebooks and frontends that cannot render
rich output. Snapshots are redacted: no session token or local path leaves the
handle.
"""

from __future__ import annotations

import html as html_lib
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol
from urllib.parse import urlsplit

from hedron_notebook.topology import require_loopback_host

__all__ = [
    "DISPLAY_SNAPSHOT_SCHEMA",
    "REDACTED",
    "DisplayHandle",
    "NotebookSession",
    "PreviewLike",
    "StaleDisplayHandleError",
    "preview_handle",
    "redact_text",
]

DISPLAY_SNAPSHOT_SCHEMA = "hedron-notebook-display-1"

REDACTED = "[redacted]"

_MAX_TEXT_CHARS = 4_000

_TOKEN_PARAM = re.compile(r"(?i)\b([A-Za-z0-9_-]*token[A-Za-z0-9_-]*)=([^&\s\"'>]+)")
_TOKEN_HEADER = re.compile(r"(?i)\b(x-[a-z0-9-]*token[a-z0-9-]*)\s*:\s*([^\s\"'<>]+)")
_POSIX_PATH = re.compile(r"(?<![\w.])/(?:Users|home|root|private|tmp|var|opt)/[^\s\"'<>)]+")
_WINDOWS_PATH = re.compile(r"(?i)\b[a-z]:\\\\?[^\s\"'<>)]+")
_TAG = re.compile(r"<[^>]+>")


class StaleDisplayHandleError(RuntimeError):
    """Raised when a closed handle is updated or reopened."""


class PreviewLike(Protocol):
    """The :class:`~hedron_notebook.preview.NotebookPreview` surface used here."""

    def external_url(self) -> str: ...

    def iframe_html(self) -> str: ...


class RichReprLike(Protocol):
    def _repr_html_(self) -> str: ...


def redact_text(text: str) -> str:
    """Remove session tokens and local filesystem paths from ``text``."""
    redacted = _TOKEN_PARAM.sub(lambda m: f"{m.group(1)}={REDACTED}", text)
    redacted = _TOKEN_HEADER.sub(lambda m: f"{m.group(1)}: {REDACTED}", redacted)
    redacted = _POSIX_PATH.sub(REDACTED, redacted)
    return _WINDOWS_PATH.sub(REDACTED, redacted)


def _as_html(content: Any) -> str:
    """Render ``content`` to HTML, escaping anything that is not already markup."""
    if isinstance(content, str):
        return content
    repr_html = getattr(content, "_repr_html_", None)
    if callable(repr_html):
        return str(repr_html())
    return f"<pre>{html_lib.escape(str(content))}</pre>"


def _as_text(html: str) -> str:
    text = _TAG.sub(" ", html)
    text = html_lib.unescape(text)
    collapsed = " ".join(text.split())
    if len(collapsed) > _MAX_TEXT_CHARS:
        return f"{collapsed[:_MAX_TEXT_CHARS]}…"
    return collapsed


@dataclass
class DisplayHandle:
    """One updatable notebook view with deterministic close semantics."""

    handle_id: str
    title: str = ""
    url: str | None = None
    _html: str = field(default="", repr=False)
    _revision: int = field(default=0, init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)
    _on_close: Callable[[], None] | None = field(default=None, repr=False)

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def revision(self) -> int:
        """Number of ``update`` calls applied; stable across repeated cell runs."""
        return self._revision

    def update(self, content: Any) -> DisplayHandle:
        """Replace the displayed content. Returns ``self`` so cells can chain."""
        if self._closed:
            raise StaleDisplayHandleError(
                f"notebook display handle {self.handle_id!r} is closed; "
                "create a new handle instead of updating a stale view"
            )
        self._html = _as_html(content)
        self._revision += 1
        return self

    def as_html(self) -> str:
        """Static HTML fallback (redacted) for saved notebooks."""
        return redact_text(self._html)

    def as_text(self) -> str:
        """Plain-text fallback for terminals and inaccessible frontends."""
        return redact_text(_as_text(self._html))

    def as_image_placeholder(self) -> str:
        """Alt-text style placeholder for frontends that only render images."""
        state = "closed" if self._closed else "live"
        label = self.title or self.handle_id
        return f"[hedron notebook view: {label} ({state}, revision {self._revision})]"

    def snapshot(self) -> dict[str, Any]:
        """Return a redacted, JSON-serializable record of the current view."""
        url = redact_text(self.url) if self.url else None
        return {
            "schema_version": DISPLAY_SNAPSHOT_SCHEMA,
            "handle_id": self.handle_id,
            "title": self.title,
            "closed": self._closed,
            "revision": self._revision,
            "url": url,
            "html": self.as_html(),
            "text": self.as_text(),
            "image": self.as_image_placeholder(),
        }

    def open_in_browser(self, *, opener: Callable[[str], object] | None = None) -> str:
        """Open the handle's loopback URL in a browser and return the URL used."""
        if self._closed:
            raise StaleDisplayHandleError(
                f"notebook display handle {self.handle_id!r} is closed; nothing to open"
            )
        if not self.url:
            raise ValueError(
                f"notebook display handle {self.handle_id!r} has no URL to open; "
                "static views render through as_html() / as_text()"
            )
        host = urlsplit(self.url).hostname or ""
        require_loopback_host(host, surface="browser open")
        if opener is None:
            import webbrowser

            webbrowser.open(self.url)
        else:
            opener(self.url)
        return self.url

    def close(self) -> None:
        """Release the view. Idempotent, and runs the close hook at most once."""
        if self._closed:
            return
        self._closed = True
        hook = self._on_close
        self._on_close = None
        if hook is not None:
            hook()

    def dispose(self) -> None:
        """Alias of :meth:`close` for IPython/ipywidgets-style call sites."""
        self.close()

    def __enter__(self) -> DisplayHandle:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _repr_html_(self) -> str:
        return self.as_html()

    def __repr__(self) -> str:
        state = "closed" if self._closed else "live"
        return f"DisplayHandle(handle_id={self.handle_id!r}, {state}, revision={self._revision})"


def preview_handle(
    preview: PreviewLike,
    *,
    handle_id: str = "preview",
    title: str = "Hedron notebook preview",
    on_close: Callable[[], None] | None = None,
) -> DisplayHandle:
    """Wrap a running :func:`~hedron_notebook.preview.start_preview` result."""
    handle = DisplayHandle(
        handle_id=handle_id,
        title=title,
        url=preview.external_url(),
        _on_close=on_close,
    )
    handle.update(preview.iframe_html())
    return handle


class NotebookSession:
    """Bounded multi-view session with deterministic cleanup on close."""

    def __init__(self, session_id: str = "notebook", *, max_handles: int = 8) -> None:
        if max_handles < 1:
            raise ValueError(f"max_handles must be >= 1, got {max_handles!r}")
        self.session_id = session_id
        self.max_handles = max_handles
        self._handles: dict[str, DisplayHandle] = {}
        self._cleanups: list[Callable[[], None]] = []
        self._closed = False
        self.closed_order: tuple[str, ...] = ()

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def handles(self) -> tuple[DisplayHandle, ...]:
        """Handles in registration order."""
        return tuple(self._handles.values())

    def display(
        self,
        content: Any = "",
        *,
        handle_id: str | None = None,
        title: str = "",
        url: str | None = None,
        on_close: Callable[[], None] | None = None,
    ) -> DisplayHandle:
        """Register and return a new view."""
        if self._closed:
            raise StaleDisplayHandleError(
                f"notebook session {self.session_id!r} is closed; start a new session"
            )
        key = handle_id or f"view-{len(self._handles) + 1}"
        if key in self._handles:
            raise ValueError(f"notebook session already holds a handle named {key!r}")
        if len(self._handles) >= self.max_handles:
            raise ValueError(
                f"notebook session {self.session_id!r} holds its maximum of "
                f"{self.max_handles} handles; close one before adding another"
            )
        handle = DisplayHandle(handle_id=key, title=title, url=url, _on_close=on_close)
        handle.update(content)
        self._handles[key] = handle
        return handle

    def add(self, handle: DisplayHandle) -> DisplayHandle:
        """Adopt an externally built handle (for example :func:`preview_handle`)."""
        if self._closed:
            raise StaleDisplayHandleError(
                f"notebook session {self.session_id!r} is closed; start a new session"
            )
        if handle.handle_id in self._handles:
            raise ValueError(f"notebook session already holds a handle named {handle.handle_id!r}")
        if len(self._handles) >= self.max_handles:
            raise ValueError(
                f"notebook session {self.session_id!r} holds its maximum of "
                f"{self.max_handles} handles; close one before adding another"
            )
        self._handles[handle.handle_id] = handle
        return handle

    def get(self, handle_id: str) -> DisplayHandle:
        try:
            return self._handles[handle_id]
        except KeyError as exc:
            raise KeyError(
                f"notebook session {self.session_id!r} has no handle {handle_id!r}"
            ) from exc

    def add_cleanup(self, cleanup: Callable[[], None]) -> None:
        """Register a teardown callable (server shutdown, temp dir removal)."""
        self._cleanups.append(cleanup)

    def snapshot(self) -> dict[str, Any]:
        """Redacted snapshot of every view in registration order."""
        return {
            "schema_version": DISPLAY_SNAPSHOT_SCHEMA,
            "session_id": self.session_id,
            "closed": self._closed,
            "max_handles": self.max_handles,
            "handles": [handle.snapshot() for handle in self.handles],
        }

    def close(self) -> None:
        """Close handles then cleanups in reverse registration order. Idempotent."""
        if self._closed:
            return
        self._closed = True
        order: list[str] = []
        for handle in reversed(self.handles):
            handle.close()
            order.append(handle.handle_id)
        self.closed_order = tuple(order)
        while self._cleanups:
            self._cleanups.pop()()

    def __enter__(self) -> NotebookSession:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
