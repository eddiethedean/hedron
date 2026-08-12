"""ASGI path normalization for Workbench / RStudio Server mounts."""

from __future__ import annotations

import logging
import re
from urllib.parse import quote, unquote, urlsplit

from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from hedron.mount import normalize_mount_path
from hedron_core.codes import HED_WB_0006
from hedron_workbench.config import WorkbenchConfig, WorkbenchMode
from hedron_workbench.detect import is_workbench_scope, path_has_encoded_absolute_url
from hedron_workbench.redact import redact_scope_for_log

log = logging.getLogger("hedron_workbench")
_PROXY_PREFIX = re.compile(r"^/proxy/\d+(?P<rest>/.*)$")
_MAX_TARGET = 8192
_DECODE_ROUNDS = 3


class _RejectedRequestTarget(Exception):
    def __init__(self, status_code: int, reason: str) -> None:
        super().__init__(reason)
        self.status_code = status_code
        self.reason = reason


def encode_raw_path(path: str) -> bytes:
    return quote(path, safe="/:@!$&'()*+,;=").encode("utf-8")


def _copy_scope(scope: Scope) -> Scope:
    return dict(scope)


def _unsafe_decoded_path(path: str) -> bool:
    if path.startswith("//") or "\\" in path or any(ord(char) < 32 for char in path):
        return True
    decoded = path
    for _ in range(_DECODE_ROUNDS):
        for segment in decoded.split("/"):
            if segment in {".", ".."}:
                return True
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if decoded.startswith("//") or "\\" in decoded:
            return True
    return False


class WorkbenchPathMiddleware:
    """Outer ASGI wrapper. Copies scope; never mutates the caller's mapping."""

    __hedron_workbench__ = True

    def __init__(
        self,
        app: ASGIApp,
        *,
        mode: WorkbenchMode | str = WorkbenchMode.AUTO,
        expected_mount: str | None = None,
        active: bool = True,
        decode_absolute_url_path: bool = True,
        strip_root_path_from_path: bool = True,
        debug: bool = False,
    ) -> None:
        self.app = app
        self.mode = WorkbenchMode.parse(mode)
        self.expected_mount = normalize_mount_path(expected_mount)
        self.active = active
        self.decode_absolute_url_path = decode_absolute_url_path
        self.strip_root_path_from_path = strip_root_path_from_path
        self.debug = debug

    def _should_normalize(self, scope: Scope) -> bool:
        if self.mode is WorkbenchMode.OFF:
            return False
        if self.mode is WorkbenchMode.AUTO and not self.active:
            return False
        if self.mode is WorkbenchMode.ON:
            return True
        path = str(scope.get("path") or "")
        if self.expected_mount and (
            path == self.expected_mount or path.startswith(self.expected_mount + "/")
        ):
            return True
        return is_workbench_scope(scope)

    def _maybe_decode_absolute_url_path(self, scope: Scope) -> Scope:
        if not self.decode_absolute_url_path:
            return scope
        raw_path = str(scope.get("path") or "")
        if len(raw_path.encode("utf-8", errors="replace")) > _MAX_TARGET:
            raise _RejectedRequestTarget(414, "oversized Workbench request target")
        if not path_has_encoded_absolute_url(raw_path):
            return scope
        candidate = raw_path.lstrip("/")
        decoded = unquote(candidate)
        parsed = urlsplit(decoded)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            raise _RejectedRequestTarget(400, "malformed absolute Workbench request target")
        decoded_path = parsed.path or "/"
        if _unsafe_decoded_path(decoded_path):
            raise _RejectedRequestTarget(400, "unsafe Workbench request path")
        while "//" in decoded_path:
            decoded_path = decoded_path.replace("//", "/")

        parsed_query = (parsed.query or "").encode()
        existing_query = bytes(scope.get("query_string") or b"")
        if parsed_query and existing_query and parsed_query != existing_query:
            raise _RejectedRequestTarget(400, "conflicting Workbench query strings")

        new_scope = _copy_scope(scope)
        new_scope["path"] = decoded_path
        new_scope["raw_path"] = encode_raw_path(decoded_path)
        if parsed_query:
            new_scope["query_string"] = parsed_query
        return new_scope

    def _apply_expected_mount(self, scope: Scope) -> Scope:
        if not self.expected_mount or scope.get("root_path"):
            return scope
        path = str(scope.get("path") or "")
        if path != self.expected_mount and not path.startswith(self.expected_mount + "/"):
            return scope
        new_scope = _copy_scope(scope)
        new_scope["root_path"] = self.expected_mount
        return new_scope

    def _canonicalize_proxy_root(self, scope: Scope) -> Scope:
        if not self.strip_root_path_from_path:
            return scope
        root_path = str(scope.get("root_path") or "").rstrip("/")
        if not root_path:
            return scope
        path = str(scope.get("path") or "")
        # Starlette get_route_path handles the ordinary root_path-prefixed shape.
        if path == root_path or path.startswith(root_path + "/"):
            return scope
        match = _PROXY_PREFIX.match(root_path)
        if not match:
            return scope
        rest = (match.group("rest") or "").rstrip("/")
        if not rest or not (path == rest or path.startswith(rest + "/")):
            return scope
        new_scope = _copy_scope(scope)
        new_scope["root_path"] = rest
        return new_scope

    def normalize_scope(self, scope: Scope) -> Scope:
        if scope.get("type") not in {"http", "websocket"} or not self._should_normalize(scope):
            return scope
        decoded = self._maybe_decode_absolute_url_path(scope)
        mounted = self._apply_expected_mount(decoded)
        return self._canonicalize_proxy_root(mounted)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return
        if self.debug and self._should_normalize(scope):
            redacted = redact_scope_for_log(scope)
            log.warning(
                "Workbench middleware incoming: method=%r root_path=%r path=%r raw_path=%r qs=%r",
                redacted["method"],
                redacted["root_path"],
                redacted["path"],
                redacted["raw_path"],
                redacted["query_string"],
            )
        try:
            normalized = self.normalize_scope(scope)
        except _RejectedRequestTarget as exc:
            log.warning("%s %s", HED_WB_0006, exc.reason)
            if scope.get("type") == "websocket":
                await send({"type": "websocket.close", "code": 1008, "reason": HED_WB_0006})
            else:
                response = PlainTextResponse(HED_WB_0006, status_code=exc.status_code)
                await response(scope, receive, send)
            return
        if self.debug and normalized is not scope:
            after = redact_scope_for_log(normalized)
            log.warning(
                "Workbench middleware normalized: root_path=%r path=%r",
                after["root_path"],
                after["path"],
            )
        await self.app(normalized, receive, send)


def is_workbenchified(app: object) -> bool:
    """Return whether ``app`` already owns Workbench normalization."""
    return isinstance(app, WorkbenchPathMiddleware) or bool(
        getattr(app, "__hedron_workbench__", False)
    )


def workbenchify(
    app: ASGIApp,
    *,
    config: WorkbenchConfig | None = None,
    mode: WorkbenchMode | str | None = None,
    expected_mount: str | None = None,
    decode_absolute_url_path: bool = True,
    strip_root_path_from_path: bool = True,
    debug: bool = False,
) -> ASGIApp:
    """Wrap ``app`` at most once. Cookie Path must still be set before construction."""
    if is_workbenchified(app):
        return app
    resolved_mode = mode
    resolved_debug = debug
    resolved_mount = expected_mount
    if config is not None:
        from hedron_workbench.resolve import resolve_deployment

        resolved = resolve_deployment(config)
        resolved_mode = resolved_mode or resolved.mode
        resolved_debug = debug or resolved.debug
        resolved_mount = resolved_mount if resolved_mount is not None else resolved.browser_mount
    return WorkbenchPathMiddleware(
        app,
        mode=resolved_mode or WorkbenchMode.AUTO,
        expected_mount=resolved_mount,
        active=True,
        decode_absolute_url_path=decode_absolute_url_path,
        strip_root_path_from_path=strip_root_path_from_path,
        debug=resolved_debug,
    )


def apply_root_path(scope: Scope, mount: str) -> Scope:
    """Set sanitized ``root_path`` on a copied scope (launcher use)."""
    new_scope = _copy_scope(scope)
    new_scope["root_path"] = normalize_mount_path(mount)
    return new_scope
