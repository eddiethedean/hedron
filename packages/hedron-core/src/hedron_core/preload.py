"""Opt-in navigation preload policy (phase 0.10)."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "HX_PRELOADED",
    "NavigationPreloadPolicy",
    "PreloadDecision",
    "decide_preload",
]

HX_PRELOADED = "HX-Preloaded"


@dataclass(frozen=True, slots=True)
class NavigationPreloadPolicy:
    """Safe-GET speculative preload controls. Disabled by default."""

    enabled: bool = False
    max_concurrent: int = 2
    max_per_navigation: int = 4
    only_same_origin: bool = True
    respect_private_cache: bool = True
    cancel_on_navigation: bool = True


@dataclass(frozen=True, slots=True)
class PreloadDecision:
    allowed: bool
    reason: str
    header_value: str | None = None
    cache_control: str | None = None
    cancel_on_navigation: bool = False


def decide_preload(
    policy: NavigationPreloadPolicy,
    *,
    method: str,
    same_origin: bool,
    speculative_count: int,
    concurrent: int,
    cache_control_request: str | None = None,
    navigation_cancelled: bool = False,
) -> PreloadDecision:
    if not policy.enabled:
        return PreloadDecision(False, "preload_disabled")
    if method.upper() != "GET":
        return PreloadDecision(False, "unsafe_method")
    if policy.only_same_origin and not same_origin:
        return PreloadDecision(False, "cross_origin")
    if policy.cancel_on_navigation and navigation_cancelled:
        return PreloadDecision(False, "navigation_cancelled", cancel_on_navigation=True)
    if concurrent >= policy.max_concurrent:
        return PreloadDecision(False, "max_concurrent")
    if speculative_count >= policy.max_per_navigation:
        return PreloadDecision(False, "max_per_navigation")
    if policy.respect_private_cache and cache_control_request:
        lowered = cache_control_request.lower()
        if "no-store" in lowered or "private" in lowered:
            return PreloadDecision(
                False,
                "private_cache",
                cache_control="no-store",
            )
    cache_control = "private, max-age=0" if policy.respect_private_cache else None
    return PreloadDecision(
        True,
        "allowed",
        header_value="1",
        cache_control=cache_control,
        cancel_on_navigation=policy.cancel_on_navigation,
    )
