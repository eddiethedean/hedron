"""Pre-import launcher: bind, discover, export, import, wrap, serve (Hedron specialization)."""

from __future__ import annotations

import os
import socket
import sys
from collections.abc import Mapping
from typing import Any

from fastapi_workbench.config import ResolvedDeployment, WorkbenchConfig
from fastapi_workbench.diagnostics import WorkbenchError
from fastapi_workbench.runner import bind_loopback as _bind_loopback
from fastapi_workbench.runner import discover_rserver_url as _discover_rserver_url
from fastapi_workbench.runner import load_app as _load_app
from fastapi_workbench.runner import serve as _serve
from hedron_core.codes import HED_WB_0009
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_posit.detect import is_workbench_job, rs_server_url
from hedron_posit.middleware import workbenchify
from hedron_posit.resolve import (
    RESOLVED_MODE_ENV,
    RESOLVED_MOUNT_ENV,
    RESOLVED_PUBLIC_BASE_ENV,
    RESOLVED_SOURCE_ENV,
    _merge_environ,  # pyright: ignore[reportPrivateUsage]  # adapter compatibility seam
    _translate_error,  # pyright: ignore[reportPrivateUsage]  # adapter compatibility seam
    explicit_mount_hint,
    resolve_deployment,
)

HEDRON_ROOT_PATH = "HEDRON_ROOT_PATH"
HEDRON_PUBLIC_BASE = RESOLVED_PUBLIC_BASE_ENV
_SUPERVISED_TARGET_ENV = "HEDRON_WORKBENCH_APP_TARGET"
_SUPERVISED_FACTORY_ENV = "HEDRON_WORKBENCH_APP_FACTORY"

__all__ = [
    "HEDRON_PUBLIC_BASE",
    "HEDRON_ROOT_PATH",
    "app_from_environ",
    "bind_loopback",
    "discover_rserver_url",
    "export_hedron_state",
    "load_app",
    "prepare_app",
    "run_target",
    "serve",
    "supervised_uvicorn_command",
]


def bind_loopback(host: str, port: int) -> socket.socket:
    try:
        return _bind_loopback(host, port)
    except WorkbenchError as exc:
        raise _translate_error(exc) from exc


def serve(app: Any, resolved: ResolvedDeployment, *, sock: socket.socket | None = None) -> None:
    try:
        _serve(app, resolved, sock=sock)
    except WorkbenchError as exc:
        raise _translate_error(exc) from exc


def discover_rserver_url(*, binary: str, port: int) -> str:
    try:
        return _discover_rserver_url(binary=binary, port=port)
    except WorkbenchError as exc:
        raise _translate_error(exc) from exc


def load_app(target: str, *, factory: bool = False) -> Any:
    try:
        return _load_app(target, factory=factory)
    except WorkbenchError as exc:
        raise _translate_error(exc) from exc


def export_hedron_state(
    resolved: ResolvedDeployment,
    *,
    environ: dict[str, str] | None = None,
) -> None:
    env = os.environ if environ is None else environ
    for name in (
        HEDRON_ROOT_PATH,
        RESOLVED_MOUNT_ENV,
        HEDRON_PUBLIC_BASE,
        RESOLVED_MODE_ENV,
        RESOLVED_SOURCE_ENV,
        "HEDRON_TRUSTED_PROXIES",
        "FASTAPI_WORKBENCH_ROOT_PATH",
        "FASTAPI_WORKBENCH_RESOLVED_MOUNT",
        "FASTAPI_WORKBENCH_RESOLVED_PUBLIC_BASE",
        "FASTAPI_WORKBENCH_RESOLVED_MODE",
        "FASTAPI_WORKBENCH_RESOLVED_SOURCE",
        "FASTAPI_WORKBENCH_TRUSTED_PROXIES",
    ):
        env.pop(name, None)
    if resolved.browser_mount:
        env[HEDRON_ROOT_PATH] = resolved.browser_mount
        env[RESOLVED_MOUNT_ENV] = resolved.browser_mount
        env["FASTAPI_WORKBENCH_ROOT_PATH"] = resolved.browser_mount
        env["FASTAPI_WORKBENCH_RESOLVED_MOUNT"] = resolved.browser_mount
    if resolved.active and resolved.external_origin:
        origin = resolved.external_origin.rstrip("/")
        mount = resolved.browser_mount
        public_base = f"{origin}{mount}" if mount and mount != "/" else origin
        env[HEDRON_PUBLIC_BASE] = public_base
        env["FASTAPI_WORKBENCH_RESOLVED_PUBLIC_BASE"] = public_base
    env[RESOLVED_MODE_ENV] = resolved.mode.value
    env[RESOLVED_SOURCE_ENV] = resolved.source
    env["FASTAPI_WORKBENCH_RESOLVED_MODE"] = resolved.mode.value
    env["FASTAPI_WORKBENCH_RESOLVED_SOURCE"] = resolved.source
    env["HEDRON_TRUSTED_PROXIES"] = resolved.forwarded_allow_ips
    env["FASTAPI_WORKBENCH_TRUSTED_PROXIES"] = resolved.forwarded_allow_ips


def prepare_app(
    *,
    target: str,
    config: WorkbenchConfig | None = None,
    environ: Mapping[str, str] | None = None,
    bound_port: int | None = None,
    discovered_raw: str | None = None,
    wrap: bool = True,
    apply_environ: bool = True,
) -> tuple[Any, ResolvedDeployment]:
    cfg = config or WorkbenchConfig(app_target=target)
    merged = _merge_environ(environ)
    resolved = resolve_deployment(
        cfg,
        environ=merged,
        bound_port=bound_port,
        discovered_raw=discovered_raw,
    )
    if apply_environ:
        if environ is None:
            export_hedron_state(resolved)
        elif isinstance(environ, dict):
            export_hedron_state(resolved, environ=environ)
        else:
            # Immutable Mapping: do not mutate process os.environ; caller cannot
            # observe writes into a throwaway copy either.
            export_hedron_state(resolved, environ=dict(environ))
    app = load_app(target, factory=cfg.factory)
    if wrap:
        app = workbenchify(
            app,
            config=cfg,
            mode=resolved.mode,
            expected_mount=resolved.browser_mount,
            debug=resolved.debug,
            relative_redirects=resolved.source == "rserver-url:path",
        )
    return app, resolved


def supervised_uvicorn_command(
    resolved: ResolvedDeployment,
    *,
    fd: int,
) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "hedron_posit.runner:app_from_environ",
        "--factory",
        "--fd",
        str(fd),
        "--proxy-headers",
        "--forwarded-allow-ips",
        resolved.forwarded_allow_ips,
        "--log-level",
        "debug" if resolved.debug else "info",
    ]
    if resolved.reload:
        command.append("--reload")
    if resolved.workers > 1:
        command.extend(("--workers", str(resolved.workers)))
    return command


def _exec_supervised(
    resolved: ResolvedDeployment,
    *,
    sock: socket.socket,
    target: str,
    factory: bool,
) -> None:
    if resolved.reload and resolved.workers > 1:
        raise HedronError(
            make_diagnostic(
                HED_WB_0009,
                severity=DiagnosticSeverity.ERROR,
                title="Conflicting Workbench launch topology",
                explanation="Uvicorn reload and multiple workers are mutually exclusive.",
                remediation="Choose reload for development or multiple workers for serving.",
            )
        )
    export_hedron_state(resolved)
    # Never pass a full Workbench URL as Uvicorn's root_path during reload or
    # worker supervision; the resolved public base is handed off separately.
    os.environ.pop("UVICORN_ROOT_PATH", None)
    os.environ[_SUPERVISED_TARGET_ENV] = target
    os.environ[_SUPERVISED_FACTORY_ENV] = "1" if factory else "0"
    sock.set_inheritable(True)
    command = supervised_uvicorn_command(resolved, fd=sock.fileno())
    os.execv(sys.executable, command)


def run_target(
    target: str,
    *,
    config: WorkbenchConfig | None = None,
    environ: Mapping[str, str] | None = None,
) -> None:
    cfg = config or WorkbenchConfig(app_target=target)
    env = _merge_environ(environ)
    initial = resolve_deployment(cfg, environ=env)
    sock = bind_loopback(initial.host, initial.port)
    try:
        bound_port = int(sock.getsockname()[1])
        discovered: str | None = None
        if (
            rs_server_url(env)
            and not is_workbench_job(env)
            and explicit_mount_hint(cfg, env, bound_port=bound_port) is None
        ):
            discovered = discover_rserver_url(
                binary=resolve_deployment(cfg, environ=env).rserver_url_bin,
                port=bound_port,
            )
        resolved = resolve_deployment(
            cfg,
            environ=env,
            bound_port=bound_port,
            discovered_raw=discovered,
        )
        if resolved.reload or resolved.workers > 1:
            _exec_supervised(
                resolved,
                sock=sock,
                target=target,
                factory=cfg.factory,
            )
            return
        # Pass the caller's environ (often None), not the merged copy. A merged
        # dict would make prepare_app treat the handoff as isolated (#136) and
        # skip writing HEDRON_ROOT_PATH into process os.environ before import,
        # leaving HedronPosit inactive under workbenchify (REALWB-030).
        app, resolved = prepare_app(
            target=target,
            config=cfg,
            environ=environ,
            bound_port=bound_port,
            discovered_raw=discovered,
        )
        serve(app, resolved, sock=sock)
    finally:
        sock.close()


def app_from_environ() -> Any:
    target = os.environ.get(_SUPERVISED_TARGET_ENV, "").strip()
    if not target:
        raise RuntimeError(f"{_SUPERVISED_TARGET_ENV} is missing")
    factory = os.environ.get(_SUPERVISED_FACTORY_ENV, "").strip() == "1"
    resolved = resolve_deployment(WorkbenchConfig(), compatibility_aliases=False)
    app = load_app(target, factory=factory)
    return workbenchify(
        app,
        config=WorkbenchConfig(
            mode=resolved.mode,
            mount=resolved.browser_mount or None,
            public_base_url=(
                f"{resolved.external_origin}{resolved.browser_mount}" if resolved.active else None
            ),
            debug=resolved.debug,
        ),
        mode=resolved.mode,
        expected_mount=resolved.browser_mount,
        debug=resolved.debug,
        relative_redirects=resolved.source == "rserver-url:path",
    )
