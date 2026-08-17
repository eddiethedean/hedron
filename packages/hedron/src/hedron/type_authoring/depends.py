"""FastAPI-facing DependsOn compiling Hedron lifetimes to Depends(scope=)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from fastapi import Depends
from fastapi.params import Depends as DependsParam

from hedron_core.lifetime import (
    DependencyLifetime,
    DependencyPlan,
    compile_fastapi_scope,
    forbid_background_capture,
)

__all__ = ["DependsOn", "as_fastapi_depends", "plan_for"]


@dataclass(frozen=True, slots=True)
class DependsOn:
    """Additive Hedron resource identity. User-authored FastAPI Depends() stays valid."""

    resource_id: str
    lifetime: DependencyLifetime = DependencyLifetime.HANDLER
    streaming: bool = False

    def plan(self) -> DependencyPlan:
        return plan_for(self)

    def __call__(self, dependency: Callable[..., Any] | None = None) -> DependsParam:
        return as_fastapi_depends(self, dependency)


def plan_for(marker: DependsOn) -> DependencyPlan:
    return DependencyPlan(
        resource_id=marker.resource_id,
        lifetime=marker.lifetime,
        streaming=marker.streaming,
    )


def as_fastapi_depends(
    marker: DependsOn,
    dependency: Callable[..., Any] | None = None,
    *,
    background: bool = False,
) -> DependsParam:
    if background:
        forbid_background_capture((marker.resource_id,))
    scope = compile_fastapi_scope(marker.lifetime)
    provider = dependency if dependency is not None else _missing_provider(marker.resource_id)
    return Depends(provider, scope=scope)


def _missing_provider(resource_id: str) -> Callable[..., None]:
    def _provider() -> None:
        raise RuntimeError(f"DependsOn({resource_id!r}) needs an application provider")

    _provider.__name__ = f"hedron_depends_on_{resource_id}"
    return _provider
