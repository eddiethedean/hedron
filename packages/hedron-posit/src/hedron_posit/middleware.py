"""ASGI path normalization for Workbench / RStudio Server mounts (Hedron specialization)."""

from __future__ import annotations

from starlette.types import ASGIApp

from fastapi_workbench.config import WorkbenchConfig, WorkbenchMode
from fastapi_workbench.middleware import WorkbenchPathMiddleware as _WorkbenchPathMiddleware
from fastapi_workbench.middleware import apply_root_path, encode_raw_path
from fastapi_workbench.middleware import is_workbenchified as _is_workbenchified

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
    absolute_redirects: bool = False,
    absolute_origin: str | None = None,
) -> ASGIApp:
    """Wrap ``app`` at most once with Hedron-owned cookie repair."""
    if getattr(app, "__hedron_posit__", False) or getattr(app, "__hedron_workbench__", False):
        requested = WorkbenchMode.parse(mode) if mode is not None else WorkbenchMode.AUTO
        deployment = getattr(app, "hedron_workbench", None)
        if (
            requested is WorkbenchMode.ON
            and deployment is not None
            and not bool(getattr(deployment, "active", False))
        ):
            raise ValueError(
                "cannot activate an already-constructed inactive HedronPosit; "
                "construct it with workbench_mode='on'/workbench_mount=..., or use "
                "hedron-posit run so cookie and asset paths are configured before import"
            )
        return app
    if is_workbenchified(app):
        return app
    resolved_mode = mode
    resolved_debug = debug
    resolved_mount = expected_mount
    expected_origins: tuple[str, ...] = ()
    if config is not None:
        from hedron_posit.resolve import resolve_deployment

        resolved = resolve_deployment(config)
        resolved_mode = resolved_mode or resolved.mode
        resolved_debug = debug or resolved.debug
        resolved_mount = resolved_mount if resolved_mount is not None else resolved.browser_mount
        expected_origins = (resolved.external_origin,)
    state = getattr(app, "state", None)
    owned = {"session", "hedron_color_mode"}
    policy = getattr(state, "hedron_security", None)
    csrf_name = getattr(policy, "csrf_cookie_name", None)
    if isinstance(csrf_name, str) and csrf_name:
        owned.add(csrf_name)
    return WorkbenchPathMiddleware(
        app,
        mode=resolved_mode or WorkbenchMode.AUTO,
        expected_mount=resolved_mount,
        active=True,
        decode_absolute_url_path=decode_absolute_url_path,
        strip_root_path_from_path=strip_root_path_from_path,
        debug=resolved_debug,
        expected_origins=expected_origins,
        runtime_mounts=True,
        mounted_response_headers=True,
        absolute_redirects=absolute_redirects,
        absolute_origin=absolute_origin,
        owned_cookie_names=tuple(sorted(owned)),
    )
