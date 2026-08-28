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

from hedron_core.alpine import AlpineFeatureDemand, AlpineMaturity, _json_value
from hedron_core.compat import StrEnum

__all__ = [
    "Interaction",
    "InteractionKind",
    "LocalEffect",
    "Outcome",
    "OutcomeKind",
    "RequestEffect",
]

_EVENT = re.compile(r"^[a-z][a-z0-9:.-]{0,63}$")
_METHODS = frozenset({"GET", "POST", "PUT", "PATCH", "DELETE"})


class InteractionKind(StrEnum):
    LOCAL = "local"
    REQUEST = "request"
    COMBINED = "combined"


@dataclass(frozen=True, slots=True)
class LocalEffect:
    """A disposable browser-local effect."""

    action: str
    state_keys: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        action = self.action.strip()
        if not action or len(action) > 128 or any(ord(char) < 32 for char in action):
            raise ValueError("local action must be a bounded non-empty name")
        keys = tuple(sorted({key.strip() for key in self.state_keys if key.strip()}))
        if any(not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$.-]{0,63}", key) for key in keys):
            raise ValueError("local state keys must be bounded identifiers")
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "state_keys", keys)

    def to_dict(self) -> dict[str, object]:
        return {"action": self.action, "state_keys": list(self.state_keys)}


@dataclass(frozen=True, slots=True)
class RequestEffect:
    """A server-owned handle operation lowered through HTMX/native HTTP."""

    handle: str
    method: str = "POST"
    target: str | None = None
    swap: str = "outerHTML"
    operation: str | None = None

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
        object.__setattr__(self, "handle", handle)
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "swap", self.swap.strip())

    def to_dict(self) -> dict[str, object]:
        return {
            "handle": self.handle,
            "method": self.method,
            "target": self.target,
            "swap": self.swap,
            "operation": self.operation,
        }


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
        if self.local_effect is not None and not isinstance(self.local_effect, LocalEffect):
            raise TypeError("local_effect must be a LocalEffect")
        if self.request_effect is not None and not isinstance(self.request_effect, RequestEffect):
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
        fallback: str = "native",
        source: str = "python",
    ) -> Interaction:
        return cls(
            InteractionKind.LOCAL,
            event=event,
            local_effect=LocalEffect(action, tuple(state_keys)),
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
        fallback: str = "native",
        source: str = "python",
    ) -> Interaction:
        return cls(
            InteractionKind.REQUEST,
            event=event,
            request_effect=RequestEffect(handle, method, target, swap, operation),
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
        method: str = "POST",
        target: str | None = None,
        swap: str = "outerHTML",
        operation: str | None = None,
        fallback: str = "native",
        source: str = "python",
    ) -> Interaction:
        return cls(
            InteractionKind.COMBINED,
            event=event,
            local_effect=LocalEffect(action, tuple(state_keys)),
            request_effect=RequestEffect(handle, method, target, swap, operation),
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

    def to_attributes(self) -> dict[str, str]:
        """Return inspectable lowering facts, not an executable request."""
        attrs = {
            "data-hedron-interaction": InteractionKind(self.kind).value,
            "data-hedron-event": self.event,
        }
        if self.local_effect:
            attrs["data-hedron-local-action"] = self.local_effect.action
            if self.local_effect.state_keys:
                attrs["data-hedron-state-keys"] = ",".join(self.local_effect.state_keys)
        if self.request_effect:
            attrs["data-hedron-handle"] = self.request_effect.handle
            attrs["data-hedron-method"] = self.request_effect.method
            if self.request_effect.target:
                attrs["data-hedron-target"] = self.request_effect.target
            attrs["data-hedron-swap"] = self.request_effect.swap
        return attrs


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
    payload: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        role = OutcomeKind(self.role)
        payload = _json_value(self.payload, path="payload")
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
        if set(payload) != expected and role is not OutcomeKind.SUCCESS:
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
            OutcomeKind.PATCH, {"target": target, "content": _json_value(content, path="content")}
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
        return cls(OutcomeKind.VALIDATION, {"errors": _json_value(errors, path="errors")})

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
