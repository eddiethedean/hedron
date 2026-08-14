"""ElementStateOwnership types and validation (STATE-036)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from hedron_core.diagnostics import error

OwnershipMode = Literal["controlled", "local", "draft", "preference"]

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


@dataclass(frozen=True, slots=True)
class ElementFieldOwnership:
    """Per-field ElementStateOwnership declaration (phase 0.36)."""

    name: str
    mode: OwnershipMode
    reflection: str = "attribute"
    incoming_update: str = "replace"
    persistence: str = "none"
    event: str | None = None


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
