"""ASGI path normalization for Workbench / RStudio Server mounts (Hedron specialization)."""

from __future__ import annotations

from starlette.types import ASGIApp

from fastapi_workbench.config import ResolvedDeployment, WorkbenchConfig, WorkbenchMode
from fastapi_workbench.middleware import WorkbenchPathMiddleware as _WorkbenchPathMiddleware
from fastapi_workbench.middleware import (
    apply_root_path,
    encode_raw_path,
    workbenchified_for_asgi_app,
)
from fastapi_workbench.middleware import is_workbenchified as _is_workbenchified
from fastapi_workbench.middleware import workbenchify as _generic_workbenchify

__all__ = [
    "WorkbenchPathMiddleware",
    "apply_root_path",
    "encode_raw_path",
    "is_workbenchified",
    "workbenchify",
]


class WorkbenchPathMiddleware(_WorkbenchPathMiddleware):
    """Hedron-branded middleware marker for compatibility checks."""

    __hedron_posit__ = True


def is_workbenchified(app: object) -> bool:
    if bool(getattr(app, "__hedron_posit__", False)) or bool(
        getattr(app, "__hedron_workbench__", False)
    ):
        return True
    return _is_workbenchified(app)


def workbenchify(
    app: ASGIApp,
    *,
    config: WorkbenchConfig | None = None,
    mode: WorkbenchMode | str | None = None,
    expected_mount: str | None = None,
    decode_absolute_url_path: bool = True,
    strip_root_path_from_path: bool = True,
    debug: bool = False,
    expected_origins: tuple[str, ...] | None = None,
    absolute_redirects: bool = False,
    absolute_origin: str | None = None,
    relative_redirects: bool | None = None,
) -> ASGIApp:
    """Wrap ``app`` at most once with Hedron-owned cookie repair."""
    resolved_mode = mode
    resolved_debug = debug
    resolved_mount = expected_mount
    resolved_absolute_origin = absolute_origin
    resolved_relative_redirects = relative_redirects
    resolved_deployment: ResolvedDeployment | None = None
    if config is not None:
        from hedron_posit.resolve import resolve_deployment

        resolved_deployment = resolve_deployment(config)
        resolved_mode = resolved_mode or resolved_deployment.mode
        resolved_debug = debug or resolved_deployment.debug
        resolved_mount = (
            resolved_mount if resolved_mount is not None else resolved_deployment.browser_mount
        )
        if expected_origins is None:
            expected_origins = (resolved_deployment.external_origin,)
        if absolute_redirects and resolved_absolute_origin is None:
            resolved_absolute_origin = resolved_deployment.external_origin
        if resolved_relative_redirects is None:
            resolved_relative_redirects = resolved_deployment.source == "rserver-url:path"

    state_owner = app
    if getattr(state_owner, "state", None) is None:
        state_owner = getattr(app, "app", app)
    state = getattr(state_owner, "state", None)
    owned = {"session", "hedron_color_mode"}
    policy = getattr(state, "hedron_security", None)
    csrf_name = getattr(policy, "csrf_cookie_name", None)
    if isinstance(csrf_name, str) and csrf_name:
        owned.add(csrf_name)

    if getattr(app, "__hedron_posit__", False) or getattr(app, "__hedron_workbench__", False):
        existing = (
            app
            if isinstance(app, _WorkbenchPathMiddleware)
            else getattr(app, "_workbench_asgi", None)
        )
        requested = WorkbenchMode.parse(mode) if mode is not None else WorkbenchMode.AUTO
        deployment = getattr(app, "hedron_workbench", None)
        deployment_active = bool(getattr(deployment, "active", False))
        activation_requested = (
            requested is WorkbenchMode.ON
            or bool(resolved_deployment and resolved_deployment.active)
            or bool(resolved_mount)
        )
        if activation_requested and deployment is not None and not deployment_active:
            raise ValueError(
                "cannot activate an already-constructed inactive HedronPosit; "
                "construct it with workbench_mode='on'/workbench_mount=..., or use "
                "hedron-posit run so cookie and asset paths are configured before import"
            )
        # Trust metadata and an explicit AUTO/OFF mode are not activation
        # evidence.  Leaving an inactive HedronPosit facade untouched keeps its
        # constructor-time cookie/asset state aligned with the inner middleware.
        if isinstance(existing, _WorkbenchPathMiddleware) and (
            deployment is None or deployment_active or activation_requested
        ):
            existing.apply_runtime_handoff(
                mode=resolved_mode,
                expected_mount=resolved_mount,
                expected_origins=expected_origins,
                debug=resolved_debug,
                relative_redirects=resolved_relative_redirects,
                owned_cookie_names=tuple(sorted(owned)),
                absolute_redirects=absolute_redirects,
                absolute_origin=resolved_absolute_origin,
            )
        return app
    if workbenchified_for_asgi_app(app):
        return _generic_workbenchify(
            app,
            mode=resolved_mode,
            expected_mount=resolved_mount,
            debug=resolved_debug,
            expected_origins=expected_origins,
            relative_redirects=resolved_relative_redirects,
            owned_cookie_names=tuple(sorted(owned)),
            absolute_redirects=absolute_redirects,
            absolute_origin=resolved_absolute_origin,
        )
    return WorkbenchPathMiddleware(
        app,
        mode=resolved_mode or WorkbenchMode.AUTO,
        expected_mount=resolved_mount,
        active=True,
        decode_absolute_url_path=decode_absolute_url_path,
        strip_root_path_from_path=strip_root_path_from_path,
        debug=resolved_debug,
        expected_origins=expected_origins or (),
        runtime_mounts=True,
        mounted_response_headers=True,
        absolute_redirects=absolute_redirects,
        absolute_origin=resolved_absolute_origin,
        relative_redirects=bool(resolved_relative_redirects),
        owned_cookie_names=tuple(sorted(owned)),
    )
