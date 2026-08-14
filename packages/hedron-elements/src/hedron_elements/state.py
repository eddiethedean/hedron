"""ElementStateOwnership helpers (STATE-036)."""

from __future__ import annotations

from typing import Literal

from hedron_core.diagnostics import error
from hedron_core.registry import ElementFieldOwnership

OwnershipMode = Literal["controlled", "local", "draft", "preference"]
IncomingPolicy = Literal["replace", "preserve", "rebase", "conflict"]

_CAPABILITY_FIELDS = frozenset(
    {
        "auth",
        "authorization",
        "csrf",
        "secret",
        "token",
        "capability",
        "trusted_html",
        "tenant",
    }
)

__all__ = [
    "IncomingPolicy",
    "OwnershipMode",
    "apply_incoming_update",
    "refuse_transfer",
    "validate_field_ownership",
]


def validate_field_ownership(field: ElementFieldOwnership) -> ElementFieldOwnership:
    if field.mode not in {"controlled", "local", "draft", "preference"}:
        raise error(
            "HED-ELEMENT-STATE-0001",
            title="Unknown ownership mode",
            explanation=f"Field {field.name!r} has invalid mode {field.mode!r}.",
            remediation="Use controlled, local, draft, or preference.",
        )
    lowered = field.name.lower()
    if any(token in lowered for token in _CAPABILITY_FIELDS) and field.mode != "controlled":
        raise error(
            "HED-ELEMENT-STATE-0002",
            title="Illegal element-owned capability",
            explanation=f"Field {field.name!r} cannot use mode {field.mode!r}.",
            remediation="Keep capabilities under server-controlled ownership.",
        )
    if field.persistence not in {"none", "preference", "draft"}:
        raise error(
            "HED-ELEMENT-STATE-0002",
            title="Illegal persistence policy",
            explanation=f"Persistence {field.persistence!r} is not allowed.",
            remediation="Use none, preference, or draft persistence.",
        )
    if field.persistence == "preference" and field.mode != "preference":
        raise error(
            "HED-ELEMENT-STATE-0002",
            title="Illegal persistence for ownership mode",
            explanation="Only preference fields may persist as preference.",
            remediation="Align persistence with ownership mode.",
        )
    return field


def apply_incoming_update(
    *,
    mode: OwnershipMode,
    dirty: bool,
    policy: IncomingPolicy | None,
    allow_rebase: bool = False,
) -> IncomingPolicy:
    """Resolve dirty-draft / controlled incoming-update policy (no silent LWW)."""
    if mode == "local":
        return "preserve"
    if mode == "controlled":
        return "replace"
    if mode == "preference":
        return policy or "preserve"
    # draft
    if not dirty:
        return "replace"
    chosen = policy or "conflict"
    if chosen == "rebase" and not allow_rebase:
        raise error(
            "HED-ELEMENT-STATE-0004",
            title="Unproven draft rebase",
            explanation="Rebase requires a proven typed merge.",
            remediation="Use conflict, preserve, or a proven rebase.",
        )
    if chosen not in {"replace", "preserve", "rebase", "conflict"}:
        raise error(
            "HED-ELEMENT-STATE-0004",
            title="Missing draft incoming policy",
            explanation=f"Policy {chosen!r} is not supported.",
            remediation="Declare replace, preserve, rebase, or conflict.",
        )
    if chosen == "conflict":
        # Explicit conflict path — never last-write-wins.
        return "conflict"
    return chosen


def refuse_transfer() -> None:
    """Cross-instance draft transfer is out of scope until phase 0.41."""
    raise error(
        "HED-ELEMENT-STATE-0006",
        title="Draft transfer not available",
        explanation="Cross-instance draft transfer is deferred to phase 0.41.",
        remediation="Keep draft state instance-local until STATE-040.",
    )
