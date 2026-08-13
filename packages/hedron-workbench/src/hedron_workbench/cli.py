"""hedron-workbench CLI: delegates to hedron-posit with Workbench branding."""

from __future__ import annotations

import argparse

from hedron_posit.cli import _cmd_check, _cmd_doctor, _cmd_run
from hedron_posit.config import WorkbenchTopology


def main(argv: list[str] | None = None) -> int:
    """Preserve the ``hedron-workbench`` command name and exit codes."""
    parser = argparse.ArgumentParser(prog="hedron-workbench")
    from hedron_posit import __version__

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
