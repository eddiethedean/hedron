"""Pre-import launcher: bind, discover, export, import, wrap, serve."""

from __future__ import annotations

import contextlib
import importlib
import os
import socket
import subprocess
import threading
import webbrowser
from collections.abc import Mapping
from typing import IO, Any

from hedron_core.codes import HED_WB_0002, HED_WB_0003, HED_WB_0004, HED_WB_0005, HED_WB_0009
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_workbench.config import ResolvedDeployment, WorkbenchConfig
from hedron_workbench.detect import rs_server_url
from hedron_workbench.middleware import workbenchify
from hedron_workbench.redact import redact_text
from hedron_workbench.resolve import (
    RESOLVED_MODE_ENV,
    RESOLVED_MOUNT_ENV,
    RESOLVED_PUBLIC_BASE_ENV,
    RESOLVED_SOURCE_ENV,
    resolve_deployment,
)

HEDRON_ROOT_PATH = "HEDRON_ROOT_PATH"
HEDRON_PUBLIC_BASE = RESOLVED_PUBLIC_BASE_ENV
_MAX_DISCOVERY_STREAM = 4096


def _read_bounded(
    stream: IO[bytes],
    *,
    limit: int,
    chunks: list[bytes],
    overflow: threading.Event,
    proc: subprocess.Popen[bytes],
) -> None:
    size = 0
    while True:
        chunk = stream.read(1024)
        if not chunk:
            return
        remaining = limit - size
        if len(chunk) > remaining:
            if remaining > 0:
                chunks.append(chunk[:remaining])
            overflow.set()
            with contextlib.suppress(OSError):
                proc.kill()
            return
        chunks.append(chunk)
        size += len(chunk)


def bind_loopback(host: str, port: int) -> socket.socket:
    family = socket.AF_INET6 if ":" in host else socket.AF_INET
    sock = socket.socket(family, socket.SOCK_STREAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(128)
    except OSError as exc:
        sock.close()
        raise HedronError(
            make_diagnostic(
                HED_WB_0004,
                severity=DiagnosticSeverity.ERROR,
                title="Failed to bind Workbench listener",
                explanation=str(exc),
                remediation="Choose another port or omit --port to bind port 0.",
            )
        ) from exc
    return sock


def discover_rserver_url(*, binary: str, port: int) -> str:
    if not binary.startswith("/"):
        raise HedronError(
            make_diagnostic(
                HED_WB_0003,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url path must be absolute",
                explanation=f"Refusing to exec {binary!r}.",
                remediation="Set HEDRON_WORKBENCH_RSERVER_URL to an absolute path.",
            )
        )
    try:
        proc = subprocess.Popen(
            [binary, "-l", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise HedronError(
            make_diagnostic(
                HED_WB_0003,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url binary missing",
                explanation=f"{binary} was not found.",
                remediation="Install Posit Workbench or pass --mount for local reproduction.",
            )
        ) from exc
    except OSError as exc:
        raise HedronError(
            make_diagnostic(
                HED_WB_0003,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url execution failed",
                explanation=str(exc),
                remediation="Check permissions and that the binary is the official rserver-url.",
            )
        ) from exc
    assert proc.stdout is not None
    assert proc.stderr is not None
    stdout_chunks: list[bytes] = []
    stderr_chunks: list[bytes] = []
    overflow = threading.Event()
    readers = [
        threading.Thread(
            target=_read_bounded,
            kwargs={
                "stream": proc.stdout,
                "limit": _MAX_DISCOVERY_STREAM,
                "chunks": stdout_chunks,
                "overflow": overflow,
                "proc": proc,
            },
            daemon=True,
        ),
        threading.Thread(
            target=_read_bounded,
            kwargs={
                "stream": proc.stderr,
                "limit": _MAX_DISCOVERY_STREAM,
                "chunks": stderr_chunks,
                "overflow": overflow,
                "proc": proc,
            },
            daemon=True,
        ),
    ]
    for reader in readers:
        reader.start()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired as exc:
        proc.kill()
        proc.wait()
        for reader in readers:
            reader.join(timeout=1)
        raise HedronError(
            make_diagnostic(
                HED_WB_0003,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url execution timed out",
                explanation="Discovery exceeded the 10 second startup bound.",
                remediation="Check the Workbench session and the configured binary.",
            )
        ) from exc
    for reader in readers:
        reader.join(timeout=1)
    if overflow.is_set():
        raise HedronError(
            make_diagnostic(
                HED_WB_0002,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url output too large",
                explanation="Discovery stdout or stderr exceeded 4096 bytes and was terminated.",
                remediation="Inspect the configured binary and use the official rserver-url.",
            )
        )

    stdout = b"".join(stdout_chunks).decode("utf-8", errors="replace")
    stderr = b"".join(stderr_chunks).decode("utf-8", errors="replace")
    if proc.returncode != 0:
        raise HedronError(
            make_diagnostic(
                HED_WB_0003,
                severity=DiagnosticSeverity.ERROR,
                title="rserver-url exited non-zero",
                explanation=redact_text(stderr.strip()) or f"exit {proc.returncode}",
                remediation="Confirm the session is active and the port is the bound listener.",
            )
        )
    return stdout.strip()


def export_hedron_state(
    resolved: ResolvedDeployment,
    *,
    environ: dict[str, str] | None = None,
) -> None:
    env = os.environ if environ is None else environ
    if resolved.browser_mount:
        env[HEDRON_ROOT_PATH] = resolved.browser_mount
        env[RESOLVED_MOUNT_ENV] = resolved.browser_mount
    else:
        env.pop(RESOLVED_MOUNT_ENV, None)
        if resolved.active:
            env.pop(HEDRON_ROOT_PATH, None)
    if resolved.active and resolved.external_origin:
        env[HEDRON_PUBLIC_BASE] = resolved.external_origin
    else:
        env.pop(HEDRON_PUBLIC_BASE, None)
    env[RESOLVED_MODE_ENV] = resolved.mode.value
    env[RESOLVED_SOURCE_ENV] = resolved.source
    env["HEDRON_TRUSTED_PROXIES"] = resolved.forwarded_allow_ips


def load_app(target: str, *, factory: bool = False) -> Any:
    if ":" not in target:
        raise HedronError(
            make_diagnostic(
                HED_WB_0005,
                severity=DiagnosticSeverity.ERROR,
                title="Invalid application target",
                explanation="Expected module:attr.",
                remediation="Pass app:app or app:create_app --factory.",
            )
        )
    module_name, attr = target.split(":", 1)
    try:
        module = importlib.import_module(module_name)
        obj: Any = module
        for part in attr.split("."):
            obj = getattr(obj, part)
    except (ModuleNotFoundError, AttributeError) as exc:
        raise HedronError(
            make_diagnostic(
                HED_WB_0005,
                severity=DiagnosticSeverity.ERROR,
                title="Failed to import application",
                explanation=str(exc),
                remediation="Fix the module:attr target and PYTHONPATH.",
            )
        ) from exc
    if factory or (callable(obj) and not hasattr(obj, "routes")):
        try:
            obj = obj()
        except Exception as exc:
            raise HedronError(
                make_diagnostic(
                    HED_WB_0005,
                    severity=DiagnosticSeverity.ERROR,
                    title="Application factory failed",
                    explanation=str(exc),
                    remediation=(
                        "Ensure the factory returns an ASGI app after HEDRON_ROOT_PATH is set."
                    ),
                )
            ) from exc
    return obj


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
    resolved = resolve_deployment(
        cfg,
        environ=environ,
        bound_port=bound_port,
        discovered_raw=discovered_raw,
    )
    if apply_environ:
        export_hedron_state(resolved)
    app = load_app(target, factory=cfg.factory)
    if wrap:
        app = workbenchify(
            app,
            config=cfg,
            mode=resolved.mode,
            expected_mount=resolved.browser_mount,
            debug=resolved.debug,
        )
    return app, resolved


def serve(
    app: Any,
    resolved: ResolvedDeployment,
    *,
    sock: socket.socket | None = None,
) -> None:
    import uvicorn

    _assert_supported_topology(resolved)

    if resolved.open_browser:
        docs = (
            f"{resolved.external_origin}{resolved.browser_mount}/docs"
            if resolved.browser_mount
            else f"{resolved.external_origin}/docs"
        )
        with contextlib.suppress(OSError):
            webbrowser.open(docs)
    kwargs: dict[str, Any] = {
        "host": resolved.host,
        "proxy_headers": True,
        "forwarded_allow_ips": resolved.forwarded_allow_ips,
        "log_level": "debug" if resolved.debug else "info",
    }
    if sock is not None:
        kwargs["fd"] = sock.fileno()
    else:
        kwargs["port"] = resolved.port or 8000
    uvicorn.run(app, **kwargs)


def _assert_supported_topology(resolved: ResolvedDeployment) -> None:
    if resolved.reload or resolved.workers > 1:
        raise HedronError(
            make_diagnostic(
                HED_WB_0009,
                severity=DiagnosticSeverity.ERROR,
                title="Unsupported Workbench launch topology",
                explanation=(
                    "Reload and multiple workers cannot safely reuse the pre-bound listener "
                    "and imported application object."
                ),
                remediation="Run one worker without reload, or use an external process supervisor.",
            )
        )


def run_target(
    target: str,
    *,
    config: WorkbenchConfig | None = None,
    environ: Mapping[str, str] | None = None,
) -> None:
    cfg = config or WorkbenchConfig(app_target=target)
    env = os.environ if environ is None else environ
    initial = resolve_deployment(cfg, environ=env)
    _assert_supported_topology(initial)
    sock = bind_loopback(initial.host, initial.port)
    try:
        bound_port = int(sock.getsockname()[1])
        discovered: str | None = None
        mount_hint = cfg.mount or env.get("HEDRON_WORKBENCH_MOUNT") or env.get("BASE_PATH")
        if rs_server_url(env) and not mount_hint:
            discovered = discover_rserver_url(
                binary=resolve_deployment(cfg, environ=env).rserver_url_bin,
                port=bound_port,
            )
        app, resolved = prepare_app(
            target=target,
            config=cfg,
            environ=env,
            bound_port=bound_port,
            discovered_raw=discovered,
        )
        serve(app, resolved, sock=sock)
    finally:
        sock.close()
