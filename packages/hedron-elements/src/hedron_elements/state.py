"""ElementStateOwnership helpers (STATE-036)."""

from __future__ import annotations

from typing import Literal

from hedron_core.diagnostics import error
from hedron_core.element_types import (
    ElementFieldOwnership,
    OwnershipMode,
    validate_field_ownership,
)

IncomingPolicy = Literal["replace", "preserve", "rebase", "conflict"]

__all__ = [
    "ElementFieldOwnership",
    "IncomingPolicy",
    "OwnershipMode",
    "apply_incoming_update",
    "refuse_transfer",
    "validate_field_ownership",
]


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
