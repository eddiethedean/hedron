"""Request-bound authorization-aware component capabilities (CAP-055)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol

ReasonCode = Literal[
    "allowed",
    "denied",
    "hidden",
    "disabled",
    "replayed",
    "rejected",
    "uploaded",
    "conflict",
]


@dataclass(frozen=True, slots=True)
class Capability:
    """Stable capability identifier (not an authorization token)."""

    name: str
    description: str | None = None

    def __post_init__(self) -> None:
        if not self.name or not self.name.replace(".", "").replace("_", "").isalnum():
            raise ValueError(f"Invalid capability name: {self.name!r}")


@dataclass(frozen=True, slots=True)
class CapabilityDecision:
    """Render-time presentation decision; never reuse as an enforcement token."""

    capability: str
    allowed: bool
    reason: ReasonCode
    presentation: Literal["show", "hide", "disable", "explain"] = "show"
    explanation: str | None = None

    def redacted(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "allowed": self.allowed,
            "reason": self.reason,
            "presentation": self.presentation,
            # explanation may be shown to users; never include policy internals
            "explanation": self.explanation,
        }


class CapabilityProvider(Protocol):
    def decide(self, capability: str, *, request: Any) -> CapabilityDecision: ...


class AllowAllCapabilities:
    """Development helper — not a production policy."""

    def decide(self, capability: str, *, request: Any) -> CapabilityDecision:
        return CapabilityDecision(
            capability=capability,
            allowed=True,
            reason="allowed",
            presentation="show",
        )


class DenyAllCapabilities:
    def decide(self, capability: str, *, request: Any) -> CapabilityDecision:
        return CapabilityDecision(
            capability=capability,
            allowed=False,
            reason="denied",
            presentation="hide",
            explanation="Not permitted",
        )


class MappingCapabilityProvider:
    """Simple set/dict provider for tests and small apps."""

    def __init__(self, allowed: set[str] | dict[str, bool]) -> None:
        if isinstance(allowed, dict):
            self._allowed = {k for k, v in allowed.items() if v}
        else:
            self._allowed = set(allowed)

    def decide(self, capability: str, *, request: Any) -> CapabilityDecision:
        ok = capability in self._allowed
        return CapabilityDecision(
            capability=capability,
            allowed=ok,
            reason="allowed" if ok else "denied",
            presentation="show" if ok else "disable",
            explanation=None if ok else "Not permitted",
        )


def resolve_capability_provider(request: Any) -> CapabilityProvider | None:
    app = getattr(request, "app", None)
    state = getattr(app, "state", None) if app is not None else None
    return getattr(state, "hedron_capabilities", None) if state is not None else None


def evaluate_capability(
    request: Any,
    capability: str | Capability | None,
    *,
    require_provider: bool = False,
) -> CapabilityDecision:
    if capability is None:
        return CapabilityDecision(
            capability="",
            allowed=True,
            reason="allowed",
            presentation="show",
        )
    name = capability.name if isinstance(capability, Capability) else str(capability)
    provider = resolve_capability_provider(request)
    if provider is None:
        if require_provider:
            return CapabilityDecision(
                capability=name,
                allowed=False,
                reason="denied",
                presentation="hide",
                explanation="Capability provider is not configured",
            )
        return CapabilityDecision(
            capability=name,
            allowed=True,
            reason="allowed",
            presentation="show",
        )
    return provider.decide(name, request=request)


def enforce_capability(request: Any, capability: str | Capability | None) -> CapabilityDecision:
    """Server-side enforcement immediately before a protected side effect.

    Declaring ``capability=`` on an action fails closed when no provider is installed.
    """
    decision = evaluate_capability(request, capability, require_provider=True)
    if not decision.allowed:
        from hedron_core.diagnostics import error

        raise error(
            "HED-CAP-0001",
            title="Capability denied",
            explanation=f"Capability {decision.capability!r} is not permitted.",
            remediation="Obtain authorization or remove the action.",
        )
    return decision


__all__ = [
    "AllowAllCapabilities",
    "Capability",
    "CapabilityDecision",
    "CapabilityProvider",
    "DenyAllCapabilities",
    "MappingCapabilityProvider",
    "ReasonCode",
    "enforce_capability",
    "evaluate_capability",
    "resolve_capability_provider",
]
