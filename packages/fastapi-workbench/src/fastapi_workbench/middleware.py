"""ASGI path normalization for Workbench / RStudio Server mounts."""

from __future__ import annotations

import json
import logging
import re
from typing import cast
from urllib.parse import quote, unquote, urlsplit

from starlette.responses import PlainTextResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from fastapi_workbench.codes import FWB_0006
from fastapi_workbench.config import WorkbenchConfig, WorkbenchMode
from fastapi_workbench.detect import (
    is_posit_connect_scope,
    is_workbench_scope,
    path_has_encoded_absolute_url,
)
from fastapi_workbench.mount import is_local_path, normalize_mount_path, prefix_local_path
from fastapi_workbench.redact import redact_scope_for_log
from fastapi_workbench.urls import normalize_http_origin

log = logging.getLogger("fastapi_workbench")
_PROXY_PREFIX = re.compile(r"^/proxy/\d+(?P<rest>/.*)$")
_MAX_TARGET = 8192
_DECODE_ROUNDS = 3
_LOCAL_RESPONSE_HEADERS = {
    b"location",
    b"hx-redirect",
    b"hx-push-url",
    b"hx-replace-url",
}
_COOKIE_PATH_ROOT = re.compile(rb"(?i)(;[ \t]*path=)/(?=;|$)")
_COOKIE_PATH = re.compile(rb"(?i)(;[ \t]*path=)([^;]*)")


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

    __fastapi_workbench__ = True

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
        expected_origins: tuple[str, ...] = (),
        runtime_mounts: bool = False,
        mounted_response_headers: bool = True,
        owned_cookie_names: tuple[str, ...] = (),
    ) -> None:
        self.app = app
        self.mode = WorkbenchMode.parse(mode)
        self.expected_mount = normalize_mount_path(expected_mount)
        self.active = active
        self.decode_absolute_url_path = decode_absolute_url_path
        self.strip_root_path_from_path = strip_root_path_from_path
        self.debug = debug
        origins: set[str] = set()
        for origin in expected_origins:
            try:
                origins.add(normalize_http_origin(origin))
            except ValueError:
                continue
        self.expected_origins = frozenset(origins)
        self.runtime_mounts = runtime_mounts
        self.mounted_response_headers = mounted_response_headers
        self.owned_cookie_names = frozenset(owned_cookie_names)

    def _should_normalize(self, scope: Scope) -> bool:
        if self.mode is WorkbenchMode.OFF:
            return False
        if self.mode is WorkbenchMode.AUTO and not self.active:
            root_path = normalize_mount_path(str(scope.get("root_path") or ""))
            return self.runtime_mounts and bool(root_path)
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
        try:
            candidate_origin = normalize_http_origin(f"{parsed.scheme}://{parsed.netloc}")
        except ValueError as exc:
            raise _RejectedRequestTarget(
                400, "malformed absolute Workbench request origin"
            ) from exc
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise _RejectedRequestTarget(400, "unsafe absolute Workbench request origin")
        if not self.expected_origins or candidate_origin not in self.expected_origins:
            raise _RejectedRequestTarget(400, "unexpected absolute Workbench request origin")
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
        decoded = (
            self._maybe_decode_absolute_url_path(scope)
            if self.active or self.expected_mount
            else scope
        )
        mounted = self._apply_expected_mount(decoded)
        return self._canonicalize_proxy_root(mounted)

    @staticmethod
    def _rewrite_hx_location(value: bytes, mount: str) -> bytes:
        text = value.decode("latin-1")
        if not text.startswith("{"):
            if is_local_path(text):
                return prefix_local_path(text, mount).encode("latin-1")
            return value
        try:
            payload_object = json.loads(text)
        except (TypeError, ValueError):
            return value
        if not isinstance(payload_object, dict):
            return value
        payload = cast(dict[str, object], payload_object)
        path = payload.get("path")
        if not isinstance(path, str) or not is_local_path(path):
            return value
        payload["path"] = prefix_local_path(path, mount)
        return json.dumps(payload, separators=(",", ":")).encode("latin-1")

    def _rewrite_set_cookie(self, value: bytes, mount: str) -> bytes:
        if not self.owned_cookie_names:
            return value
        first = value.split(b"=", 1)[0].strip().decode("latin-1")
        if first not in self.owned_cookie_names:
            return value
        return _COOKIE_PATH_ROOT.sub(
            lambda match: match.group(1) + mount.encode("ascii"),
            value,
            count=1,
        )

    def _prepare_connect_cookie(self, value: bytes, mount: str) -> bytes:
        """Undo app-side scoping that Connect will apply at its outer proxy."""
        if not self.owned_cookie_names:
            return value
        first = value.split(b"=", 1)[0].strip().decode("latin-1")
        if first not in self.owned_cookie_names:
            return value
        match = _COOKIE_PATH.search(value)
        if match is None:
            return value
        path = match.group(2).rstrip(b"/") or b"/"
        if path != mount.encode("ascii"):
            return value
        return value[: match.start(2)] + b"/" + value[match.end(2) :]

    def _rewrite_response_start(
        self, message: Message, mount: str, *, connect_proxy: bool = False
    ) -> Message:
        if message.get("type") != "http.response.start" or not mount:
            return message
        headers = cast(list[tuple[bytes, bytes]], message.get("headers") or [])
        changed = False
        rewritten: list[tuple[bytes, bytes]] = []
        for name, value in headers:
            lower = name.lower()
            new_value = value
            if lower in _LOCAL_RESPONSE_HEADERS:
                text = value.decode("latin-1")
                if text.lower() not in {"true", "false"} and is_local_path(text):
                    new_value = prefix_local_path(text, mount).encode("latin-1")
            elif lower == b"hx-location":
                new_value = self._rewrite_hx_location(value, mount)
            elif lower == b"set-cookie":
                new_value = (
                    self._prepare_connect_cookie(value, mount)
                    if connect_proxy
                    else self._rewrite_set_cookie(value, mount)
                )
            changed = changed or new_value != value
            rewritten.append((name, new_value))
        if not changed:
            return message
        out = dict(message)
        out["headers"] = rewritten
        return out

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
            log.warning("%s %s", FWB_0006, exc.reason)
            if scope.get("type") == "websocket":
                await send({"type": "websocket.close", "code": 1008, "reason": FWB_0006})
            else:
                response = PlainTextResponse(FWB_0006, status_code=exc.status_code)
                await response(scope, receive, send)
            return
        if self.debug and normalized is not scope:
            after = redact_scope_for_log(normalized)
            log.warning(
                "Workbench middleware normalized: root_path=%r path=%r",
                after["root_path"],
                after["path"],
            )
        if not self.mounted_response_headers or scope.get("type") != "http":
            await self.app(normalized, receive, send)
            return
        mount = normalize_mount_path(str(normalized.get("root_path") or ""))
        if not mount and self.active:
            mount = self.expected_mount
        connect_proxy = not self.active and is_posit_connect_scope(normalized)

        async def mounted_send(message: Message) -> None:
            await send(self._rewrite_response_start(message, mount, connect_proxy=connect_proxy))

        await self.app(normalized, receive, mounted_send)


def is_workbenchified(app: object) -> bool:
    """Return whether ``app`` already owns Workbench normalization."""
    return isinstance(app, WorkbenchPathMiddleware) or bool(
        getattr(app, "__fastapi_workbench__", False)
    )


def workbenchified_for_asgi_app(app: object) -> bool:
    """Return whether ``app`` or an nested ASGI wrapper owns Workbench normalization."""
    seen: set[int] = set()
    current: object | None = app
    while current is not None and id(current) not in seen:
        if is_workbenchified(current):
            return True
        seen.add(id(current))
        current = getattr(current, "app", None)
    return False


def workbenchify(
    app: ASGIApp,
    *,
    config: WorkbenchConfig | None = None,
    mode: WorkbenchMode | str | None = None,
    expected_mount: str | None = None,
    decode_absolute_url_path: bool = True,
    strip_root_path_from_path: bool = True,
    debug: bool = False,
    owned_cookie_names: tuple[str, ...] = (),
) -> ASGIApp:
    """Wrap ``app`` at most once. Cookie Path must still be set before construction."""
    if is_workbenchified(app):
        requested = WorkbenchMode.parse(mode)
        deployment = getattr(app, "fastapi_workbench", None)
        if (
            requested is WorkbenchMode.ON
            and deployment is not None
            and not bool(getattr(deployment, "active", False))
        ):
            raise ValueError(
                "cannot activate an already-constructed inactive Workbench wrapper; "
                "construct it with workbench_mode='on'/workbench_mount=..., or use "
                "fastapi-workbench run so cookie and asset paths are configured before import"
            )
        return app
    resolved_mode = mode
    resolved_debug = debug
    resolved_mount = expected_mount
    expected_origins: tuple[str, ...] = ()
    if config is not None:
        from fastapi_workbench.resolve import resolve_deployment

        resolved = resolve_deployment(config)
        resolved_mode = resolved_mode or resolved.mode
        resolved_debug = debug or resolved.debug
        resolved_mount = resolved_mount if resolved_mount is not None else resolved.browser_mount
        expected_origins = (resolved.external_origin,)
    return WorkbenchPathMiddleware(
        app,
        mode=resolved_mode or WorkbenchMode.AUTO,
        expected_mount=resolved_mount,
        active=True,
        decode_absolute_url_path=decode_absolute_url_path,
        strip_root_path_from_path=strip_root_path_from_path,
        debug=resolved_debug,
        expected_origins=expected_origins,
        runtime_mounts=True,
        mounted_response_headers=True,
        owned_cookie_names=owned_cookie_names,
    )


def apply_root_path(scope: Scope, mount: str) -> Scope:
    """Set sanitized ``root_path`` on a copied scope (launcher use)."""
    new_scope = _copy_scope(scope)
    new_scope["root_path"] = normalize_mount_path(mount)
    return new_scope
