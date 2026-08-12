"""hedron-workbench CLI: run, check, --dry-run."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, cast

from hedron_core.diagnostics import HedronError
from hedron_workbench import __version__
from hedron_workbench.config import WorkbenchConfig, WorkbenchMode
from hedron_workbench.detect import rs_server_url
from hedron_workbench.redact import redact_record, redact_text
from hedron_workbench.resolve import resolve_deployment
from hedron_workbench.runner import discover_rserver_url, run_target


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
    )


def _emit(resolved: Any, *, fmt: str) -> None:
    payload = redact_record(resolved.as_dict())
    if fmt == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
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
    cfg = _config_from_args(args)
    discovered: str | None = None
    if getattr(args, "discover", False) and rs_server_url() and not cfg.mount:
        try:
            discovered = discover_rserver_url(binary=cfg.rserver_url_bin, port=cfg.port or 8000)
        except HedronError as exc:
            print(redact_text(str(exc)), file=sys.stderr)
            return 1
    try:
        resolved = resolve_deployment(cfg, discovered_raw=discovered)
    except HedronError as exc:
        print(redact_text(str(exc)), file=sys.stderr)
        return 1
    _emit(resolved, fmt=args.format)
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    cfg = _config_from_args(args)
    try:
        run_target(args.app, config=cfg)
    except HedronError as exc:
        print(redact_text(str(exc)), file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hedron-workbench")
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
        p.add_argument("--format", choices=("text", "json"), default="text")
        p.add_argument(
            "--reload",
            action="store_true",
            help="Rejected by the pre-bound runner; use an external supervisor",
        )
        p.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Must be 1; use an external supervisor for multiple processes",
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

    args = parser.parse_args(argv)
    if args.command in {"check", "dry-run"}:
        return _cmd_check(args)
    if args.command == "run":
        return _cmd_run(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
