"""Pre-seal registration. FastAPI alpha matches/handle stay unused."""

from __future__ import annotations

from typing import Any

from hedron_core.codes import HED_FP_0005
from hedron_core.diagnostics import error

__all__ = ["ALPHA_ROUTER_HOOKS", "fail_closed_late_registration", "router_excludes_alpha_hooks"]

ALPHA_ROUTER_HOOKS = ("matches", "handle")


def fail_closed_late_registration(
    *,
    registry_sealed: bool = False,
    catalog_sealed: bool = False,
    openapi_cached: bool = False,
) -> None:
    if not (registry_sealed or catalog_sealed or openapi_cached):
        return
    raise error(
        HED_FP_0005,
        title="Late registration is closed",
        explanation=(
            "Routes cannot be added after seal_registry, seal_app_catalog, or OpenAPI cache."
        ),
        remediation="Register routers and features before lifespan seal.",
    )


def router_excludes_alpha_hooks(router: Any) -> bool:
    router_value: object = router
    cls: type[object] = type(router_value)
    for name in ALPHA_ROUTER_HOOKS:
        owned = name in vars(cls)
        if owned:
            return False
    return True
