"""hedron-posit CLI: run, check, --dry-run."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any, cast

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


def _config_from_args(args: argparse.Namespace) -> WorkbenchConfig:
    mode = WorkbenchMode.parse(args.mode) if getattr(args, "mode", None) else WorkbenchMode.AUTO
    return WorkbenchConfig(
        mode=mode,
        host=getattr(args, "host", None),
        port=getattr(args, "port", None),
        mount=getattr(args, "mount", None),
        public_base_url=getattr(args, "public_base_url", None),
        rserver_url_bin=getattr(args, "rserver_url", None) or WorkbenchConfig().rserver_url_bin,
        open_browser=bool(getattr(args, "open_browser", False)),
        reload=bool(getattr(args, "reload", False)),
        workers=int(getattr(args, "workers", 1)),
        forwarded_allow_ips=getattr(args, "forwarded_allow_ips", None),
        allow_external_bind=bool(getattr(args, "allow_external_bind", False)),
        debug=bool(getattr(args, "debug", False)),
        factory=bool(getattr(args, "factory", False)),
        app_target=getattr(args, "app", None),
        topology=WorkbenchTopology.parse(getattr(args, "topology", None)),
    )


def _emit(resolved: Any, *, fmt: str, posit_status: dict[str, object] | None = None) -> None:
    payload = redact_record(resolved.as_dict())
    if posit_status is not None:
        payload["posit_status"] = redact_record(posit_status)
    if fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if posit_status is not None:
        print(f"product: {posit_status.get('product')}")
        print(f"evidence: {posit_status.get('evidence')}")
        print(f"cookie_strategy: {posit_status.get('cookie_strategy')}")
        print(f"bridge_enabled: {posit_status.get('bridge_enabled')}")
    print(f"mode: {payload['mode']}")
    print(f"bind: {payload['bind']}")
    print(f"external_origin: {payload['external_origin']}")
    print(f"browser_mount: {payload['browser_mount']}")
    print(f"cookie_mount: {payload['cookie_mount']}")
    print(f"source: {payload['source']}")
    print(f"discovered: {payload['discovered']}")
    warning_values = payload.get("warnings")
    if isinstance(warning_values, list):
        for warning in cast(list[object], warning_values):
            print(f"warning: {warning}")


def _cmd_check(args: argparse.Namespace) -> int:
    from hedron_posit.config import PositConfig, resolve_posit_deployment

    cfg = _config_from_args(args)
    discovered: str | None = None
    bound_port: int | None = None
    sock = None
    try:
        if (
            getattr(args, "discover", False)
            and rs_server_url()
            and explicit_mount_hint(cfg) is None
        ):
            # Match doctor --live: bind first, then pass the listening port to rserver-url.
            # ``--port 0`` / unset means ephemeral (``or 0``), not a hard-coded 8000.
            sock = bind_loopback(cfg.host or "127.0.0.1", cfg.port or 0)
            bound_port = int(sock.getsockname()[1])
            try:
                discovered = discover_rserver_url(binary=cfg.rserver_url_bin, port=bound_port)
            except HedronError as exc:
                print(redact_text(str(exc)), file=sys.stderr)
                return 1
        try:
            posit = resolve_posit_deployment(
                PositConfig(workbench=cfg),
                discovered_raw=discovered,
                bound_port=bound_port,
            )
            resolved = posit.workbench
        except HedronError as exc:
            print(redact_text(str(exc)), file=sys.stderr)
            return 1
        status: dict[str, object] = {
            "product": posit.product.value,
            "evidence": posit.evidence,
            "cookie_strategy": posit.cookie_mode.value,
            "bridge_enabled": posit.bridge_enabled,
            "compatibility_facade": posit.compatibility_facade,
        }
        _emit(resolved, fmt=args.format, posit_status=status)
        return 0
    finally:
        if sock is not None:
            sock.close()


def _cmd_run(args: argparse.Namespace) -> int:
    cfg = _config_from_args(args)
    try:
        run_target(args.app, config=cfg)
    except HedronError as exc:
        print(redact_text(str(exc)), file=sys.stderr)
        return 1
    return 0


def _normalize_cookie_path(path: str) -> str:
    if not path or path == "/":
        return "/"
    return path.rstrip("/") or "/"


def _parse_set_cookie_path(header: str) -> str | None:
    """Return the RFC6265 Path attribute from a Set-Cookie header.

    Missing Path attributes yield ``None`` (fail closed for mount checks).
    Quoted values are unquoted; comparison callers normalize trailing slashes.
    """
    parts = header.split(";")
    for part in parts[1:]:
        name, sep, value = part.strip().partition("=")
        if not sep or name.lower() != "path":
            continue
        path = value.strip()
        if len(path) >= 2 and path[0] == path[-1] and path[0] in "\"'":
            path = path[1:-1]
        return path
    return None


def _cookie_path_matches_mount(header: str, mount: str) -> bool:
    expected = _normalize_cookie_path(mount or "/")
    path = _parse_set_cookie_path(header)
    if path is None:
        return False
    return _normalize_cookie_path(path) == expected


async def _probe_app(app: Any, mount: str) -> dict[str, object]:
    import re

    import httpx

    target = f"{mount}/" if mount else "/"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="https://doctor.invalid",
        follow_redirects=False,
    ) as client:
        response = await client.get(target)
    html = response.text if "text/html" in response.headers.get("content-type", "") else ""
    unmounted: list[str] = []
    if mount and html:
        pattern = re.compile(r'(?:href|src|action|hx-(?:get|post|put|patch|delete))="(/[^"]*)"')
        for match in pattern.finditer(html):
            value = match.group(1)
            if value != mount and not value.startswith(mount + "/"):
                unmounted.append(value)
    cookie_headers = response.headers.get_list("set-cookie")
    # Empty Set-Cookie list must fail closed (all([]) is True otherwise) — #160.
    cookie_paths_ok = bool(cookie_headers) and all(
        _cookie_path_matches_mount(header, mount) for header in cookie_headers
    )
    return {
        "target": target,
        "status": response.status_code,
        "reachable": response.status_code < 500,
        "unmounted_generated_urls": sorted(set(unmounted)),
        "generated_urls_mounted": not unmounted,
        "cookie_paths_mounted": cookie_paths_ok,
    }


def _cmd_doctor(args: argparse.Namespace) -> int:
    cfg = _config_from_args(args)
    sock = None
    report: dict[str, object] = {"checks": {}}
    try:
        bound_port: int | None = None
        discovered: str | None = None
        if args.live:
            sock = bind_loopback(cfg.host or "127.0.0.1", cfg.port or 0)
            bound_port = int(sock.getsockname()[1])
            if rs_server_url() and explicit_mount_hint(cfg) is None:
                discovered = discover_rserver_url(binary=cfg.rserver_url_bin, port=bound_port)
        resolved = resolve_deployment(
            cfg,
            bound_port=bound_port,
            discovered_raw=discovered,
        )
        report["deployment"] = redact_record(resolved.as_dict())
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
        checks["rserver_url_binary"] = not rs_server_url() or (
            os.path.isabs(resolved.rserver_url_bin) and os.access(resolved.rserver_url_bin, os.X_OK)
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
    if "error" in report:
        return 1
    checks = cast(dict[str, object], report["checks"])
    for value in checks.values():
        if value is False:
            return 1
        if isinstance(value, dict):
            probe = cast(dict[str, object], value)
            if any(
                probe.get(name) is False
                for name in ("reachable", "generated_urls_mounted", "cookie_paths_mounted")
            ):
                return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hedron-posit")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    def add_shared(p: argparse.ArgumentParser) -> None:
        p.add_argument("--mode", choices=("auto", "on", "off"), default="auto")
        p.add_argument("--host")
        p.add_argument("--port", type=int)
        p.add_argument("--mount")
        p.add_argument("--public-base-url")
        p.add_argument("--rserver-url")
        p.add_argument("--forwarded-allow-ips")
        p.add_argument(
            "--allow-external-bind",
            action="store_true",
            help="Permit a non-loopback --host after operator review",
        )
        p.add_argument("--debug", action="store_true")
        p.add_argument(
            "--topology",
            choices=tuple(item.value for item in WorkbenchTopology),
            default="auto",
        )
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument(
            "--reload",
            action="store_true",
            help="Discover once, then exec Uvicorn's reload supervisor",
        )
        p.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Discover once, then exec this many Uvicorn workers",
        )

    check_p = sub.add_parser("check", help="Resolve deployment without importing the app")
    add_shared(check_p)
    check_p.add_argument("--dry-run", action="store_true", help="Alias of check")
    check_p.add_argument(
        "--discover",
        action="store_true",
        help="Call rserver-url when RS_SERVER_URL is set (still no app import)",
    )
    check_p.add_argument("app", nargs="?", help="Ignored; check does not import the app")

    run_p = sub.add_parser("run", help="Discover, export mount, import, wrap, serve")
    add_shared(run_p)
    run_p.add_argument("app", help="module:attr or module:factory")
    run_p.add_argument("--factory", action="store_true")
    run_p.add_argument("--open-browser", action="store_true")

    dry = sub.add_parser("dry-run", help="Same as check")
    add_shared(dry)
    dry.add_argument("app", nargs="?")

    doctor = sub.add_parser("doctor", help="Diagnose topology and optionally probe the app")
    add_shared(doctor)
    doctor.add_argument("app", nargs="?", help="module:attr (required with --live)")
    doctor.add_argument("--factory", action="store_true")
    doctor.add_argument(
        "--live",
        action="store_true",
        help="bind, discover, import, and ASGI-probe",
    )

    args = parser.parse_args(argv)
    if args.command in {"check", "dry-run"}:
        return _cmd_check(args)
    if args.command == "run":
        return _cmd_run(args)
    if args.command == "doctor":
        return _cmd_doctor(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
