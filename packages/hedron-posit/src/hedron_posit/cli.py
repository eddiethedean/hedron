"""hedron-posit CLI: run, check, --dry-run."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Protocol, cast

from fastapi_workbench.cli_support import (
    cookie_path_matches_mount,
    deployment_payload,
    deployment_text_lines,
    probe_asgi_app,
    report_checks_ok,
    resolve_check,
)
from hedron_core.diagnostics import HedronError
from hedron_posit import __version__
from hedron_posit.config import WorkbenchConfig, WorkbenchMode, WorkbenchTopology
from hedron_posit.detect import rs_server_url
from hedron_posit.redact import redact_record, redact_text
from hedron_posit.resolve import explicit_mount_hint, resolve_deployment
from hedron_posit.runner import (
    bind_loopback,
    discover_rserver_url,
    prepare_app,
    run_target,
)


class _WorkbenchArgs(Protocol):
    command: str
    format: str
    mode: str | None
    host: str
    port: int
    mount: str | None
    public_base_url: str | None
    rserver_url: str | None
    open_browser: bool
    reload: bool
    workers: int | None
    forwarded_allow_ips: str | None
    allow_external_bind: bool
    debug: bool
    factory: bool
    app: str | None
    topology: str | None
    discover: bool
    live: bool
    matrix: bool


class _SocketAddress(Protocol):
    def getsockname(self) -> tuple[object, ...]: ...


class _ResponseHeaders(Protocol):
    def get(self, name: str, default: str | None = None) -> str | None: ...


class _ResponseWithHeaders(Protocol):
    headers: _ResponseHeaders


def _bound_port(sock: object) -> int:
    address = cast(_SocketAddress, sock).getsockname()
    if len(address) < 2 or not isinstance(address[1], int):
        raise ValueError("bound socket address does not contain an integer port")
    return address[1]


def _config_from_args(args: _WorkbenchArgs) -> WorkbenchConfig:
    mode = WorkbenchMode.parse(args.mode) if args.mode else WorkbenchMode.AUTO
    return WorkbenchConfig(
        mode=mode,
        host=args.host,
        port=args.port,
        mount=args.mount,
        public_base_url=args.public_base_url,
        rserver_url_bin=args.rserver_url or WorkbenchConfig().rserver_url_bin,
        open_browser=args.open_browser,
        reload=args.reload,
        workers=args.workers,
        forwarded_allow_ips=args.forwarded_allow_ips,
        allow_external_bind=args.allow_external_bind,
        debug=args.debug,
        factory=args.factory,
        app_target=args.app,
        topology=WorkbenchTopology.parse(args.topology),
    )


def _emit(resolved: object, *, fmt: str, posit_status: dict[str, object] | None = None) -> None:
    payload = deployment_payload(resolved, status=posit_status)
    if fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print("\n".join(deployment_text_lines(payload, status=posit_status)))


def _cmd_check(args: _WorkbenchArgs) -> int:
    from hedron_posit.config import PositConfig, resolve_posit_deployment

    if args.matrix:
        from hedron_posit.matrix import run_deployment_matrix

        report = run_deployment_matrix()
        if args.format == "json":
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"matrix_ok: {report['ok']}")
            for case in report["cases"]:
                print(
                    f"case {case['id']}: mount={case['mount']!r} "
                    + f"cookie_path={case['cookie_path']!r} ok={case['ok']}"
                )
            if report["failed"]:
                print(f"failed: {', '.join(report['failed'])}", file=sys.stderr)
        return 0 if report["ok"] else 1

    cfg = _config_from_args(args)
    try:
        result = resolve_check(
            host=cfg.host or "127.0.0.1",
            port=cfg.port or 0,
            discover=args.discover,
            discovery_available=bool(rs_server_url()) or args.discover,
            explicit_mount=lambda _port: explicit_mount_hint(cfg, bound_port=cfg.port) is not None,
            bind=bind_loopback,
            discover_url=lambda port: discover_rserver_url(binary=cfg.rserver_url_bin, port=port),
            resolve=lambda bound_port, discovered: resolve_posit_deployment(
                PositConfig(workbench=cfg),
                discovered_raw=discovered,
                bound_port=bound_port,
            ),
        )
        posit = result.value
        resolved = posit.workbench
        status: dict[str, object] = {
            "product": posit.product.value,
            "evidence": posit.evidence,
            "cookie_strategy": posit.cookie_mode.value,
            "bridge_enabled": posit.bridge_enabled,
            "compatibility_facade": posit.compatibility_facade,
        }
        _emit(resolved, fmt=args.format, posit_status=status)
        return 0
    except HedronError as exc:
        print(redact_text(str(exc)), file=sys.stderr)
        return 1


def _cmd_run(args: _WorkbenchArgs) -> int:
    if not args.app:
        print("run requires an application target", file=sys.stderr)
        return 2
    cfg = _config_from_args(args)
    try:
        if args.discover:
            run_target(args.app, config=cfg, discover=True)
        else:
            run_target(args.app, config=cfg)
    except HedronError as exc:
        print(redact_text(str(exc)), file=sys.stderr)
        return 1
    return 0


_cookie_path_matches_mount = cookie_path_matches_mount


async def _probe_app(app: object, mount: str) -> dict[str, object]:
    from hedron_posit.diagnostics import scan_location_header, scan_set_cookie_headers

    def posit_checks(response: object, cookie_headers: list[str]) -> dict[str, object]:
        response_headers = cast(_ResponseWithHeaders, response).headers
        diagnostics = [
            item.as_dict()
            for item in (
                *scan_set_cookie_headers(cookie_headers, mount=mount or "/"),
                *scan_location_header(response_headers.get("location"), mount=mount or "/"),
            )
        ]
        return {"diagnostics": diagnostics, "diagnostics_clean": not diagnostics}

    return await probe_asgi_app(app, mount, extra_checks=posit_checks)


def _cmd_doctor(args: _WorkbenchArgs) -> int:
    cfg = _config_from_args(args)
    sock = None
    report: dict[str, object] = {"checks": {}}
    try:
        bound_port: int | None = None
        discovered: str | None = None
        # Validate host policy before opening a live listener.
        _ignored = resolve_deployment(cfg)
        if args.live:
            sock = bind_loopback(cfg.host or "127.0.0.1", cfg.port or 0)
            bound_port = _bound_port(sock)
            if (args.discover or rs_server_url()) and explicit_mount_hint(
                cfg, bound_port=bound_port
            ) is None:
                discovered = discover_rserver_url(binary=cfg.rserver_url_bin, port=bound_port)
        resolved = resolve_deployment(
            cfg,
            bound_port=bound_port,
            discovered_raw=discovered,
        )
        report["deployment"] = redact_record(resolved.as_dict())
        from hedron_posit.config import PositConfig, resolve_posit_deployment

        posit = resolve_posit_deployment(
            PositConfig(workbench=cfg),
            discovered_raw=discovered,
            bound_port=bound_port,
        )
        report["posit_status"] = {
            "product": posit.product.value,
            "evidence": posit.evidence,
            "cookie_strategy": posit.cookie_mode.value,
            "bridge_enabled": posit.bridge_enabled,
            "compatibility_facade": posit.compatibility_facade,
        }
        checks = cast(dict[str, object], report["checks"])
        checks["listener_host_safe"] = (
            resolved.host in {"127.0.0.1", "::1", "localhost"}
            or cfg.allow_external_bind
            or resolved.topology
            in {
                WorkbenchTopology.LAUNCHER_KUBERNETES,
                WorkbenchTopology.LAUNCHER_SLURM,
            }
        )
        discovery_requested = bool(args.discover or rs_server_url())
        checks["rserver_url_binary"] = not discovery_requested or (
            Path(resolved.rserver_url_bin).is_absolute()
            and os.access(resolved.rserver_url_bin, os.X_OK)
        )
        if args.live:
            if not args.app:
                raise ValueError("doctor --live requires app as module:attribute")
            app, _ = prepare_app(
                target=args.app,
                config=cfg,
                bound_port=bound_port,
                discovered_raw=discovered,
            )
            checks["app_probe"] = asyncio.run(_probe_app(app, resolved.browser_mount))
    except (HedronError, ValueError) as exc:
        report["error"] = redact_text(str(exc))
    finally:
        if sock is not None:
            sock.close()

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report, sort_keys=True))
    return 0 if report_checks_ok(report) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hedron-posit")
    _ignored = parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_shared(p: argparse.ArgumentParser) -> None:
        _ignored = p.add_argument("--mode", choices=("auto", "on", "off"), default="auto")
        _ignored = p.add_argument("--host")
        _ignored = p.add_argument("--port", type=int)
        _ignored = p.add_argument("--mount")
        _ignored = p.add_argument("--public-base-url")
        _ignored = p.add_argument("--rserver-url")
        _ignored = p.add_argument("--forwarded-allow-ips")
        _ignored = p.add_argument(
            "--allow-external-bind",
            action="store_true",
            help="Permit a non-loopback --host after operator review",
        )
        _ignored = p.add_argument("--debug", action="store_true")
        _ignored = p.add_argument(
            "--topology",
            choices=tuple(item.value for item in WorkbenchTopology),
            default="auto",
        )
        _ignored = p.add_argument("--format", choices=("text", "json"), default="text")
        _ignored = p.add_argument(
            "--reload",
            action="store_true",
            help="Discover once, then exec Uvicorn's reload supervisor",
        )
        _ignored = p.add_argument(
            "--workers",
            type=int,
            default=None,
            help="Discover once, then exec this many Uvicorn workers",
        )

    check_p = sub.add_parser("check", help="Resolve deployment without importing the app")
    add_shared(check_p)
    _ignored = check_p.add_argument("--dry-run", action="store_true", help="Alias of check")
    _ignored = check_p.add_argument(
        "--discover",
        action="store_true",
        help="Always call rserver-url after binding (still no app import)",
    )
    _ignored = check_p.add_argument(
        "--matrix",
        action="store_true",
        help="Evaluate protocol-level deployment-matrix fixtures (no app import)",
    )
    _ignored = check_p.add_argument("app", nargs="?", help="Ignored; check does not import the app")

    run_p = sub.add_parser("run", help="Discover, export mount, import, wrap, serve")
    add_shared(run_p)
    _ignored = run_p.add_argument("app", help="module:attr or module:factory")
    _ignored = run_p.add_argument("--factory", action="store_true")
    _ignored = run_p.add_argument("--open-browser", action="store_true")
    _ignored = run_p.add_argument(
        "--discover",
        action="store_true",
        help="Always call rserver-url after binding, even without RS_SERVER_URL",
    )

    dry = sub.add_parser("dry-run", help="Same as check")
    add_shared(dry)
    _ignored = dry.add_argument("app", nargs="?")

    doctor = sub.add_parser("doctor", help="Diagnose topology and optionally probe the app")
    add_shared(doctor)
    _ignored = doctor.add_argument("app", nargs="?", help="module:attr (required with --live)")
    _ignored = doctor.add_argument("--factory", action="store_true")
    _ignored = doctor.add_argument(
        "--live",
        action="store_true",
        help="bind, discover, import, and ASGI-probe",
    )
    _ignored = doctor.add_argument(
        "--discover",
        action="store_true",
        help="Always call rserver-url during --live, even without RS_SERVER_URL",
    )

    for command_parser in (check_p, run_p, dry, doctor):
        command_parser.set_defaults(
            open_browser=False,
            factory=False,
            discover=False,
            live=False,
            matrix=False,
        )

    args = cast(_WorkbenchArgs, cast(object, parser.parse_args(argv)))
    if args.command in {"check", "dry-run"}:
        return _cmd_check(args)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "doctor":
        return _cmd_doctor(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
