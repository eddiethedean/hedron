"""Server-authoritative navigation policy and stale-response protection (0.62)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Literal
from urllib.parse import urljoin, urlsplit

__all__ = [
    "NavigationDecision",
    "NavigationIdentity",
    "NavigationMachine",
    "NavigationPhase",
    "NavigationPolicy",
    "NavigationState",
    "PrefetchDecision",
    "is_safe_navigation_url",
    "decide_prefetch",
]


class NavigationPhase(StrEnum):
    IDLE = "idle"
    PENDING = "pending"
    COMMITTED = "committed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class NavigationPolicy:
    """Bounded navigation behavior; all enhancements are opt-in."""

    retain_pending: bool = True
    max_snapshots: int = 3
    focus: Literal["target", "heading", "preserve"] = "target"
    scroll: Literal["top", "preserve", "anchor"] = "top"
    prefetch_enabled: bool = False
    prefetch_methods: tuple[str, ...] = ("GET", "HEAD")
    prefetch_same_origin: bool = True
    prefetch_max_concurrent: int = 2
    prefetch_max_bytes: int = 262_144
    prefetch_cache: Literal["private", "no-store", "default"] = "private"
    transitions_enabled: bool = False

    def __post_init__(self) -> None:
        if self.max_snapshots < 0:
            raise ValueError("max_snapshots cannot be negative")
        if not 1 <= self.prefetch_max_concurrent <= 16:
            raise ValueError("prefetch_max_concurrent must be between 1 and 16")
        if not 1 <= self.prefetch_max_bytes <= 4 * 1024 * 1024:
            raise ValueError("prefetch_max_bytes must be between 1 and 4194304")
        if self.prefetch_cache not in {"private", "no-store", "default"}:
            raise ValueError("prefetch_cache must be private, no-store, or default")
        methods = tuple(method.upper() for method in self.prefetch_methods)
        if any(method not in {"GET", "HEAD", "OPTIONS"} for method in methods):
            raise ValueError("prefetch_methods may contain only safe HTTP methods")
        object.__setattr__(self, "prefetch_methods", methods)


@dataclass(frozen=True, slots=True)
class NavigationIdentity:
    navigation_id: str
    generation: int
    url: str
    target: str = "document"

    def __post_init__(self) -> None:
        if not self.navigation_id or len(self.navigation_id) > 128:
            raise ValueError("navigation_id must be non-empty and at most 128 characters")
        if self.generation < 0:
            raise ValueError("generation must be non-negative")
        if not self.url or len(self.url) > 4096:
            raise ValueError("url must be non-empty and at most 4096 characters")
        if not self.target or len(self.target) > 512:
            raise ValueError("target must be non-empty and at most 512 characters")

    def to_dict(self) -> dict[str, object]:
        return {
            "navigation_id": self.navigation_id,
            "generation": self.generation,
            "url": self.url,
            "target": self.target,
        }


@dataclass(frozen=True, slots=True)
class NavigationState:
    phase: NavigationPhase = NavigationPhase.IDLE
    identity: NavigationIdentity | None = None
    title: str | None = None
    history: Literal["none", "push", "replace", "pop"] = "none"
    focus_target: str | None = None
    scroll: Literal["top", "preserve", "anchor"] = "top"
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class NavigationDecision:
    accepted: bool
    state: NavigationState
    reason: str
    diagnostic_code: str | None = None


class NavigationMachine:
    """Small deterministic state machine for one navigation target."""

    def __init__(self, policy: NavigationPolicy | None = None) -> None:
        self.policy = policy or NavigationPolicy()
        self._state = NavigationState()
        self._generation = -1

    @property
    def state(self) -> NavigationState:
        return self._state

    def start(
        self,
        *,
        navigation_id: str,
        url: str,
        target: str = "document",
        history: Literal["none", "push", "replace", "pop"] = "push",
    ) -> NavigationIdentity:
        self._generation += 1
        identity = NavigationIdentity(navigation_id, self._generation, url, target)
        self._state = NavigationState(
            phase=NavigationPhase.PENDING,
            identity=identity,
            history=history,
            scroll=self.policy.scroll,
        )
        return identity

    def _matches(self, identity: NavigationIdentity) -> bool:
        current = self._state.identity
        return (
            self._state.phase is NavigationPhase.PENDING
            and current is not None
            and current == identity
        )

    def _decision(
        self, identity: NavigationIdentity, *, accepted: bool, reason: str
    ) -> NavigationDecision:
        if self._matches(identity):
            return NavigationDecision(accepted, self._state, reason)
        current = self._state.identity
        code = (
            "HED-NAV-0005"
            if current and current.generation != identity.generation
            else "HED-NAV-0006"
        )
        stale_state = replace(self._state, reason=reason)
        return NavigationDecision(False, stale_state, reason, code)

    def commit(
        self,
        identity: NavigationIdentity,
        *,
        title: str | None = None,
        focus_target: str | None = None,
    ) -> NavigationDecision:
        decision = self._decision(identity, accepted=True, reason="committed")
        if not decision.accepted:
            return decision
        self._state = replace(
            self._state,
            phase=NavigationPhase.COMMITTED,
            title=title,
            focus_target=focus_target,
            reason="committed",
        )
        return NavigationDecision(True, self._state, "committed")

    def reject(
        self, identity: NavigationIdentity, *, reason: str = "rejected"
    ) -> NavigationDecision:
        decision = self._decision(identity, accepted=True, reason=reason)
        if not decision.accepted:
            return decision
        self._state = replace(self._state, phase=NavigationPhase.REJECTED, reason=reason)
        return NavigationDecision(True, self._state, reason)

    def cancel(self, identity: NavigationIdentity) -> NavigationDecision:
        decision = self._decision(identity, accepted=True, reason="cancelled")
        if not decision.accepted:
            return decision
        self._state = replace(self._state, phase=NavigationPhase.CANCELLED, reason="cancelled")
        return NavigationDecision(True, self._state, "cancelled")


@dataclass(frozen=True, slots=True)
class PrefetchDecision:
    allowed: bool
    reason: str
    cache_control: str | None = None
    cancel_on_navigation: bool = True


def is_safe_navigation_url(url: str, *, origin: str, same_origin_only: bool = True) -> bool:
    """Validate a navigation/prefetch URL without granting authority."""
    if any(ord(char) < 32 for char in url) or not url:
        return False
    try:
        resolved = urljoin(origin.rstrip("/") + "/", url)
        target = urlsplit(resolved)
        source = urlsplit(origin)
        _ = target.port
        _ = source.port
    except ValueError:
        return False
    if target.scheme not in {"http", "https"} or target.username or target.password:
        return False
    return not same_origin_only or (target.scheme, target.netloc.lower()) == (
        source.scheme,
        source.netloc.lower(),
    )


def decide_prefetch(
    policy: NavigationPolicy,
    *,
    method: str,
    url: str,
    origin: str,
    concurrent: int = 0,
    response_bytes: int = 0,
    private: bool = False,
) -> PrefetchDecision:
    if not policy.prefetch_enabled:
        return PrefetchDecision(False, "prefetch_disabled")
    normalized = method.upper()
    if normalized not in policy.prefetch_methods:
        return PrefetchDecision(False, "unsafe_method")
    if not is_safe_navigation_url(url, origin=origin, same_origin_only=policy.prefetch_same_origin):
        return PrefetchDecision(False, "unsafe_origin")
    if concurrent >= policy.prefetch_max_concurrent:
        return PrefetchDecision(False, "max_concurrent")
    if response_bytes > policy.prefetch_max_bytes:
        return PrefetchDecision(False, "max_bytes")
    if private and policy.prefetch_cache != "default":
        return PrefetchDecision(False, "private_response")
    cache_control = {
        "private": "private, max-age=0",
        "no-store": "no-store",
        "default": None,
    }[policy.prefetch_cache]
    return PrefetchDecision(True, "allowed", cache_control=cache_control)
