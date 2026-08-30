"""Closed Phase 0.67 interaction and outcome algebra.

These values describe ownership and lowering; they do not dispatch requests or
mutate application state.  The existing HTMX interaction contracts remain the
transport and response authorities.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal, TypeGuard, cast

from hedron_core.alpine import (
    AlpineAttrs,
    AlpineDirective,
    AlpineExpression,
    AlpineFeatureDemand,
    AlpineMaturity,
    json_value,
)
from hedron_core.compat import StrEnum
from hedron_core.htmx.attrs import HtmxAttrs
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = [
    "Interaction",
    "InteractionLowering",
    "InteractionKind",
    "LocalEffect",
    "Outcome",
    "OutcomeKind",
    "RequestEffect",
]

_EVENT = re.compile(r"^[a-z][a-z0-9:.-]{0,63}$")
_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})


def _empty_native_fallback() -> dict[str, HtmlAttrValue]:
    return {}


def _false_state(paths: Sequence[str]) -> dict[str, object]:
    """Build a bounded nested Alpine scope for legacy ownerless toggles."""
    state: dict[str, object] = {}
    for path in paths:
        cursor = state
        parts = path.split(".")
        for part in parts[:-1]:
            child = cursor.get(part)
            if child is None:
                nested: dict[str, object] = {}
                cursor[part] = nested
                cursor = nested
                continue
            if not isinstance(child, dict):
                raise ValueError(f"local state keys overlap at {path!r}")
            cursor = cast(dict[str, object], child)
        leaf = parts[-1]
        if isinstance(cursor.get(leaf), dict):
            raise ValueError(f"local state keys overlap at {path!r}")
        cursor[leaf] = False
    return state


def _is_state_mapping(value: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(value, Mapping)


def _state_has_path(state: Mapping[str, object], path: str) -> bool:
    cursor: object = state
    for part in path.split("."):
        if not _is_state_mapping(cursor) or part not in cursor:
            return False
        cursor = cursor[part]
    return True


class InteractionKind(StrEnum):
    LOCAL = "local"
    REQUEST = "request"
    COMBINED = "combined"


@dataclass(frozen=True, slots=True)
class LocalEffect:
    """A disposable browser-local effect."""

    action: str
    state_keys: tuple[str, ...] = ()
    state: Mapping[str, object] | None = None
    scope: Literal["self", "ancestor"] = "self"
    scope_owner: str | None = None

    def __post_init__(self) -> None:
        action = self.action.strip()
        if (
            not action
            or len(action) > 128
            or re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*", action)
            is None
        ):
            raise ValueError("local action must be a bounded dotted identifier")
        keys = tuple(sorted({key.strip() for key in self.state_keys if key.strip()}))
        if any(
            re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*", key) is None
            for key in keys
        ):
            raise ValueError("local state keys must be bounded identifiers")
        scope = str(self.scope).strip().lower()
        if scope not in {"self", "ancestor"}:
            raise ValueError("local scope must be self or ancestor")
        owner = self.scope_owner.strip() if self.scope_owner is not None else None
        if scope == "ancestor":
            if not owner or re.fullmatch(r"#[A-Za-z][A-Za-z0-9_.:-]{0,95}", owner) is None:
                raise ValueError("ancestor local scope requires a bounded #id scope_owner")
            if self.state is not None:
                raise ValueError("ancestor local scope cannot carry self-owned state")
        elif owner is not None:
            raise ValueError("self local scope cannot declare scope_owner")
        state = None if self.state is None else json_value(self.state, path="local state")
        if state is not None and not isinstance(state, dict):
            raise TypeError("local state must be a mapping")
        if scope == "self":
            # The 0.67 API allowed ownerless local effects. Keep that source valid
            # while ensuring the executable Alpine directive always has a real
            # scope: explicit keys become false-valued toggles, and a bare action
            # becomes its own toggle key.
            keys = keys or (action,)
            if state is None:
                state = _false_state(keys)
        if state is not None and any(not _state_has_path(state, key) for key in keys):
            missing = sorted(key for key in keys if not _state_has_path(state, key))
            raise ValueError(f"local state must initialize every state key: {missing!r}")
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "state_keys", keys)
        object.__setattr__(self, "state", MappingProxyType(state) if state is not None else None)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "scope_owner", owner)

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "action": self.action,
            "state_keys": list(self.state_keys),
            "scope": self.scope,
        }
        if self.scope_owner is not None:
            result["scope_owner"] = self.scope_owner
        if self.state is not None:
            result["state"] = dict(self.state)
        return result


@dataclass(frozen=True, slots=True)
class RequestEffect:
    """A server-owned handle operation lowered through HTMX/native HTTP."""

    handle: str
    method: str = "POST"
    target: str | None = None
    swap: str = "outerHTML"
    operation: str | None = None
    sync: str | None = None

    def __post_init__(self) -> None:
        handle = self.handle.strip()
        method = self.method.strip().upper()
        if not handle or len(handle) > 192 or any(ord(char) < 32 for char in handle):
            raise ValueError("request handle must be a bounded identifier")
        if method not in _METHODS:
            raise ValueError(f"method must be one of {sorted(_METHODS)}")
        if self.target is not None and (
            not self.target.startswith("#")
            or not re.fullmatch(r"#[A-Za-z][A-Za-z0-9_.:-]{0,95}", self.target)
        ):
            raise ValueError("target must be a bounded id selector")
        if (
            not self.swap.strip()
            or len(self.swap) > 64
            or any(ord(char) < 32 for char in self.swap)
        ):
            raise ValueError("swap must be a bounded HTMX swap name")
        if self.operation is not None and not re.fullmatch(
            r"[A-Za-z][A-Za-z0-9_.:-]{0,95}", self.operation
        ):
            raise ValueError("operation must be a bounded identifier")
        if self.sync is not None:
            sync = self.sync.strip()
            if (
                not sync
                or len(sync) > 128
                or any(ord(char) < 32 for char in sync)
                or any(token in sync for token in ("<", ">", '"', "'", ";"))
            ):
                raise ValueError("sync must be a bounded HTMX synchronization policy")
            if sync.rsplit(":", 1)[-1].strip() not in {
                "drop",
                "abort",
                "replace",
                "queue first",
                "queue last",
                "queue all",
            }:
                raise ValueError("sync must use a supported HTMX synchronization strategy")
        object.__setattr__(self, "handle", handle)
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "swap", self.swap.strip())

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "handle": self.handle,
            "method": self.method,
            "target": self.target,
            "swap": self.swap,
            "operation": self.operation,
        }
        if self.sync is not None:
            result["sync"] = self.sync
        return result


@dataclass(frozen=True, slots=True)
class InteractionLowering:
    """Typed lanes produced by an :class:`Interaction` declaration."""

    metadata: Mapping[str, HtmlAttrValue]
    alpine: AlpineAttrs | None = None
    htmx: HtmxAttrs | None = None
    native_fallback: Mapping[str, HtmlAttrValue] = field(default_factory=_empty_native_fallback)
    demands: tuple[AlpineFeatureDemand, ...] = ()

    def to_attributes(self) -> dict[str, HtmlAttrValue]:
        attrs = dict(self.metadata)
        if self.alpine is not None:
            for name, value in self.alpine.to_attributes().items():
                if name in attrs:
                    raise ValueError(f"duplicate interaction attribute writer {name!r}")
                attrs[name] = value
        if self.htmx is not None:
            for name, value in self.htmx.as_html_attrs().items():
                if name in attrs:
                    raise ValueError(f"duplicate interaction attribute writer {name!r}")
                attrs[name] = value
        for name, value in self.native_fallback.items():
            if name in attrs:
                raise ValueError(f"duplicate interaction attribute writer {name!r}")
            attrs[name] = value
        return attrs


@dataclass(frozen=True, slots=True)
class Interaction:
    """One closed local/request/combined interaction declaration."""

    kind: InteractionKind | str
    event: str = "click"
    local_effect: LocalEffect | None = None
    request_effect: RequestEffect | None = None
    fallback: str = "native"
    source: str = "python"
    maturity: AlpineMaturity = AlpineMaturity.SUPPORTED

    def __post_init__(self) -> None:
        kind = InteractionKind(self.kind)
        event = self.event.strip().lower()
        if _EVENT.fullmatch(event) is None:
            raise ValueError("event must be a bounded DOM event name")
        if self.fallback not in {"native", "none", "full-page", "full-fragment"}:
            raise ValueError("fallback must be native, none, full-page, or full-fragment")
        if not self.source.strip():
            raise ValueError("interaction source is required")
        local_effect = cast(object, self.local_effect)
        request_effect = cast(object, self.request_effect)
        if local_effect is not None and not isinstance(local_effect, LocalEffect):
            raise TypeError("local_effect must be a LocalEffect")
        if request_effect is not None and not isinstance(request_effect, RequestEffect):
            raise TypeError("request_effect must be a RequestEffect")
        has_local = self.local_effect is not None
        has_request = self.request_effect is not None
        expected = {
            InteractionKind.LOCAL: (True, False),
            InteractionKind.REQUEST: (False, True),
            InteractionKind.COMBINED: (True, True),
        }[kind]
        if (has_local, has_request) != expected:
            raise ValueError(
                f"{kind.value} interaction must carry exactly its declared effect lanes; "
                "cross-lane fields are rejected"
            )
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "event", event)
        object.__setattr__(self, "maturity", AlpineMaturity(self.maturity))

    @classmethod
    def local(
        cls,
        action: str,
        *,
        event: str = "click",
        state_keys: Sequence[str] = (),
        state: Mapping[str, object] | None = None,
        scope: Literal["self", "ancestor"] = "self",
        scope_owner: str | None = None,
        fallback: str = "native",
        source: str = "python",
    ) -> Interaction:
        return cls(
            InteractionKind.LOCAL,
            event=event,
            local_effect=LocalEffect(action, tuple(state_keys), state, scope, scope_owner),
            fallback=fallback,
            source=source,
        )

    @classmethod
    def request(
        cls,
        handle: str,
        *,
        event: str = "click",
        method: str = "POST",
        target: str | None = None,
        swap: str = "outerHTML",
        operation: str | None = None,
        sync: str | None = None,
        fallback: str = "native",
        source: str = "python",
    ) -> Interaction:
        return cls(
            InteractionKind.REQUEST,
            event=event,
            request_effect=RequestEffect(handle, method, target, swap, operation, sync),
            fallback=fallback,
            source=source,
        )

    @classmethod
    def combined(
        cls,
        action: str,
        handle: str,
        *,
        event: str = "click",
        state_keys: Sequence[str] = (),
        state: Mapping[str, object] | None = None,
        scope: Literal["self", "ancestor"] = "self",
        scope_owner: str | None = None,
        method: str = "POST",
        target: str | None = None,
        swap: str = "outerHTML",
        operation: str | None = None,
        sync: str | None = None,
        fallback: str = "native",
        source: str = "python",
    ) -> Interaction:
        return cls(
            InteractionKind.COMBINED,
            event=event,
            local_effect=LocalEffect(action, tuple(state_keys), state, scope, scope_owner),
            request_effect=RequestEffect(handle, method, target, swap, operation, sync),
            fallback=fallback,
            source=source,
        )

    @property
    def fingerprint(self) -> str:
        payload = json.dumps(
            self.to_dict(include_fingerprint=False), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def demands(self) -> tuple[AlpineFeatureDemand, ...]:
        if self.kind is InteractionKind.REQUEST:
            return ()
        return (AlpineFeatureDemand("interaction", self.source, self.maturity),)

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        kind = InteractionKind(self.kind)
        maturity = AlpineMaturity(self.maturity)
        result: dict[str, object] = {
            "kind": kind.value,
            "event": self.event,
            "local": self.local_effect.to_dict() if self.local_effect else None,
            "request": self.request_effect.to_dict() if self.request_effect else None,
            "fallback": self.fallback,
            "source": self.source,
            "maturity": maturity.value,
        }
        if include_fingerprint:
            result["fingerprint"] = self.fingerprint
        return result

    def to_attributes(self, *, tag: str | None = None) -> dict[str, HtmlAttrValue]:
        """Lower the interaction into inspectable and executable HTML facts.

        The interaction algebra remains framework-neutral, so the request lane is
        resolved through the active core route registry rather than importing an
        adapter.  When a route is available, HTMX receives the same method, target,
        swap, and event described by the interaction.  The ``data-hedron-*`` facts
        remain useful for inspection and the native fallback path; they are never a
        substitute for server-side authorization.
        """
        return self.to_lowering(tag=tag).to_attributes()

    def to_lowering(self, *, tag: str | None = None) -> InteractionLowering:
        """Lower once into typed Alpine/HTMX lanes plus inspectable metadata."""
        attrs: dict[str, HtmlAttrValue] = {
            "data-hedron-interaction": InteractionKind(self.kind).value,
            "data-hedron-event": self.event,
            "data-hedron-fallback": self.fallback,
        }
        alpine: AlpineAttrs | None = None
        htmx = None
        route: tuple[str, str] | None = None
        if self.local_effect:
            attrs["data-hedron-local-action"] = self.local_effect.action
            if self.local_effect.state_keys:
                attrs["data-hedron-state-keys"] = ",".join(self.local_effect.state_keys)
            if self.local_effect.state is not None:
                attrs["data-hedron-local-scope"] = "self"
            elif self.local_effect.scope == "ancestor":
                attrs["data-hedron-local-scope"] = "ancestor"
                attrs["data-hedron-scope-owner"] = self.local_effect.scope_owner or ""
            if self.local_effect.state_keys:
                key = self.local_effect.state_keys[0]
                expression = AlpineExpression.assign(
                    key, AlpineExpression.not_(AlpineExpression.name(key))
                )
            else:
                expression = AlpineExpression.call(self.local_effect.action)
            alpine = AlpineAttrs(
                directives=(AlpineDirective(f"x-on:{self.event}", expression),),
                state=self.local_effect.state or {},
                source=f"interaction:{self.source}",
            )
        if self.request_effect:
            attrs["data-hedron-handle"] = self.request_effect.handle
            attrs["data-hedron-method"] = self.request_effect.method
            if self.request_effect.target:
                attrs["data-hedron-target"] = self.request_effect.target
            attrs["data-hedron-swap"] = self.request_effect.swap
            route = _resolve_route(self.request_effect.handle)
            if route is not None:
                method, path = route
                if method != self.request_effect.method:
                    raise ValueError(
                        f"interaction method {self.request_effect.method!r} does not match "
                        f"registered route method {method!r} for {self.request_effect.handle!r}"
                    )
                htmx = HtmxAttrs(
                    method=cast(Literal["get", "post", "put", "patch", "delete"], method.lower()),
                    url=path,
                    target=self.request_effect.target,
                    swap=self.request_effect.swap,
                    trigger=self.event if self.event != "click" else None,
                    sync=self.request_effect.sync,
                )
        native_fallback: dict[str, HtmlAttrValue] = {}
        normalized_tag = tag.strip().lower() if tag is not None else None
        if self.request_effect and route is not None and normalized_tag is not None:
            method, path = route
            if self.fallback in {"native", "full-page"}:
                if normalized_tag == "a":
                    if method != "GET":
                        raise ValueError("native anchor fallback requires a GET interaction")
                    native_fallback["href"] = SafeUrl.parse(path, purpose=UrlPurpose.NAVIGATION)
                elif normalized_tag == "form":
                    if method not in {"GET", "POST"}:
                        raise ValueError("native form fallback supports only GET and POST")
                    native_fallback["action"] = SafeUrl.parse(path, purpose=UrlPurpose.FORM_ACTION)
                    native_fallback["method"] = method.lower()
                elif normalized_tag == "button":
                    if method not in {"GET", "POST"}:
                        raise ValueError("native button fallback supports only GET and POST")
                    native_fallback["formaction"] = SafeUrl.parse(
                        path, purpose=UrlPurpose.FORM_ACTION
                    )
                    native_fallback["formmethod"] = method.lower()
                else:
                    raise ValueError(
                        f"native fallback is unsupported for <{normalized_tag}>; "
                        "use an anchor, form, or button"
                    )
        return InteractionLowering(
            attrs,
            alpine=alpine,
            htmx=htmx,
            native_fallback=native_fallback,
            demands=self.demands(),
        )


def _resolve_route(logical_id: str) -> tuple[str, str] | None:
    """Resolve a registered handle without coupling core to a web adapter."""
    try:
        from hedron_core.registry import get_registry

        for route in get_registry().routes():
            if route.logical_id != logical_id and route.name != logical_id:
                continue
            method = route.methods[0].upper() if route.methods else "GET"
            if method in _METHODS and route.path.startswith("/"):
                return method, route.path
    except (ImportError, RuntimeError):
        # Portable rendering and standalone simulations may not have an active
        # route registry.  Their metadata remains inspectable and native-safe.
        return None
    return None


class OutcomeKind(StrEnum):
    SUCCESS = "success"
    NO_CONTENT = "no-content"
    REFRESH = "refresh"
    PATCH = "patch"
    REDIRECT = "redirect"
    JOB = "job"
    VALIDATION = "validation"
    CONFLICT = "conflict"
    DOWNLOAD = "download"


@dataclass(frozen=True, slots=True)
class Outcome:
    """Closed, role-indexed server outcome description."""

    role: OutcomeKind | str
    payload: Mapping[str, object] = field(default_factory=dict[str, object])

    def __post_init__(self) -> None:
        role = OutcomeKind(self.role)
        payload = json_value(self.payload, path="payload")
        if not isinstance(payload, dict):
            raise TypeError("Outcome payload must be a mapping")
        required: dict[OutcomeKind, frozenset[str]] = {
            OutcomeKind.SUCCESS: frozenset(),
            OutcomeKind.NO_CONTENT: frozenset(),
            OutcomeKind.REFRESH: frozenset({"handles"}),
            OutcomeKind.PATCH: frozenset({"target", "content"}),
            OutcomeKind.REDIRECT: frozenset({"location"}),
            OutcomeKind.JOB: frozenset({"job_id"}),
            OutcomeKind.VALIDATION: frozenset({"errors"}),
            OutcomeKind.CONFLICT: frozenset({"revision"}),
            OutcomeKind.DOWNLOAD: frozenset({"url"}),
        }
        expected = required[role]
        if set(payload) != set(expected) and role is not OutcomeKind.SUCCESS:
            raise ValueError(
                f"{role.value} outcome payload must contain exactly {sorted(expected)!r}"
            )
        if role is OutcomeKind.REFRESH:
            handles = payload.get("handles")
            if (
                not isinstance(handles, list)
                or not handles
                or any(not isinstance(handle, str) or not handle.strip() for handle in handles)
            ):
                raise ValueError("refresh outcome handles must be a non-empty string list")
        if role is OutcomeKind.PATCH:
            target = payload.get("target")
            if (
                not isinstance(target, str)
                or re.fullmatch(r"#[A-Za-z][A-Za-z0-9_.:-]{0,95}", target) is None
            ):
                raise ValueError("patch outcome target must be a bounded id selector")
        if role is OutcomeKind.REDIRECT:
            location = payload.get("location")
            if (
                not isinstance(location, str)
                or not location.startswith("/")
                or location.startswith("//")
            ):
                raise ValueError("redirect outcome location must be a local root-relative path")
        if role is OutcomeKind.JOB and (
            not isinstance(payload.get("job_id"), str) or not str(payload["job_id"]).strip()
        ):
            raise ValueError("job outcome job_id is required")
        if role is OutcomeKind.VALIDATION and not isinstance(payload.get("errors"), dict):
            raise ValueError("validation outcome errors must be a mapping")
        if role is OutcomeKind.DOWNLOAD:
            url = payload.get("url")
            if not isinstance(url, str) or not url.startswith("/") or url.startswith("//"):
                raise ValueError("download outcome URL must be a local root-relative path")
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "payload", MappingProxyType(payload))

    @classmethod
    def success(cls, **payload: object) -> Outcome:
        return cls(OutcomeKind.SUCCESS, payload)

    @classmethod
    def no_content(cls) -> Outcome:
        return cls(OutcomeKind.NO_CONTENT)

    @classmethod
    def refresh(cls, *handles: object) -> Outcome:
        """Refresh one or more registered view handles by logical id.

        Callers may pass a handle object (anything exposing ``dom_id`` or
        ``logical_id``) or an already-normalized logical-id string.  The wire
        payload stays a redacted string so outcomes never serialize application
        objects; bound handles retain their exact instance identity.
        """
        normalized: list[str] = []
        for handle in handles:
            if isinstance(handle, str):
                value = handle.strip()
            else:
                value = str(
                    getattr(handle, "dom_id", None) or getattr(handle, "logical_id", "") or ""
                ).strip()
            if not value:
                raise ValueError("refresh handles must be non-empty logical ids or view handles")
            normalized.append(value)
        if not normalized:
            raise ValueError("refresh requires at least one handle")
        return cls(OutcomeKind.REFRESH, {"handles": normalized})

    @classmethod
    def patch(cls, target: str, content: object) -> Outcome:
        return cls(
            OutcomeKind.PATCH, {"target": target, "content": json_value(content, path="content")}
        )

    @classmethod
    def redirect(cls, location: str) -> Outcome:
        if not location.startswith("/") or location.startswith("//"):
            raise ValueError("redirect must be a local root-relative path")
        return cls(OutcomeKind.REDIRECT, {"location": location})

    @classmethod
    def job(cls, job_id: str) -> Outcome:
        return cls(OutcomeKind.JOB, {"job_id": job_id})

    @classmethod
    def validation(cls, errors: Mapping[str, object]) -> Outcome:
        return cls(OutcomeKind.VALIDATION, {"errors": json_value(errors, path="errors")})

    @classmethod
    def conflict(cls, revision: str | int) -> Outcome:
        return cls(OutcomeKind.CONFLICT, {"revision": revision})

    @classmethod
    def download(cls, url: str) -> Outcome:
        if not url.startswith("/") or url.startswith("//"):
            raise ValueError("download URL must be a local root-relative path")
        return cls(OutcomeKind.DOWNLOAD, {"url": url})

    def to_dict(self) -> dict[str, object]:
        return {"role": OutcomeKind(self.role).value, "payload": dict(self.payload)}
