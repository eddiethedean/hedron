"""Portable dependency lifetime plans (phase 0.49). No FastAPI imports."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

from hedron_core.codes import HED_FP_0001
from hedron_core.diagnostics import error

__all__ = [
    "FASTAPI_HANDLER_SCOPE",
    "FASTAPI_RESPONSE_SCOPE",
    "MAX_DEPENDENCY_EDGES",
    "DependencyLifetime",
    "DependencyPlan",
    "compile_fastapi_scope",
    "forbid_background_capture",
]

FASTAPI_HANDLER_SCOPE: Literal["function"] = "function"
FASTAPI_RESPONSE_SCOPE: Literal["request"] = "request"
MAX_DEPENDENCY_EDGES = 32


class DependencyLifetime(StrEnum):
    """Hedron public names. FastAPI compile targets are function/request."""

    HANDLER = "handler"
    RESPONSE = "response"


@dataclass(frozen=True, slots=True)
class DependencyPlan:
    """Inspectable resource lifetime. Compilation to FastAPI lives in hedron."""

    resource_id: str
    lifetime: DependencyLifetime = DependencyLifetime.HANDLER
    streaming: bool = False
    edges: tuple[str, ...] = ()
    adapter_disposition: str = "fastapi"
    cleanup: tuple[str, ...] = ()
    portability: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.edges) > MAX_DEPENDENCY_EDGES:
            raise error(
                HED_FP_0001,
                title="Dependency graph too large",
                explanation=f"Plan has {len(self.edges)} edges; max is {MAX_DEPENDENCY_EDGES}.",
                remediation="Split the resource graph.",
            )
        object.__setattr__(self, "portability", dict(self.portability))
        if self.streaming and self.lifetime is not DependencyLifetime.RESPONSE:
            raise error(
                HED_FP_0001,
                title="Streaming resources require RESPONSE lifetime",
                explanation="SSE/download streams still need the resource after handler return.",
                remediation="Use DependencyLifetime.RESPONSE (FastAPI scope='request').",
            )


def compile_fastapi_scope(lifetime: DependencyLifetime) -> Literal["function", "request"]:
    if lifetime is DependencyLifetime.RESPONSE:
        return FASTAPI_RESPONSE_SCOPE
    return FASTAPI_HANDLER_SCOPE


def forbid_background_capture(names: Sequence[str]) -> None:
    """D-020: background work must not capture request-owned values."""
    owned = [name for name in names if name]
    if owned:
        raise error(
            HED_FP_0001,
            title="Background capture of request-owned values is forbidden",
            explanation=f"Cannot capture {owned!r} after the request lifetime ends.",
            remediation="Pass identifiers or re-resolve inside the background worker.",
        )
