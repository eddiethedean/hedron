from __future__ import annotations

import argparse
import importlib
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="edron")
    subparsers = parser.add_subparsers(dest="command")
    run = subparsers.add_parser("run", help="run an Edron application")
    run.add_argument("application", help="module:variable, for example app:app")
    run.add_argument("--host", default="127.0.0.1")
    run.add_argument("--port", type=int, default=8000)
    subparsers.add_parser("check", help="validate that an application module imports")
    args = parser.parse_args(argv)
    if args.command in {"run", "check"}:
        module_name, separator, attribute = args.application.partition(":")
        if not separator:
            parser.error("application must use module:variable syntax")
        module = importlib.import_module(module_name)
        application = getattr(module, attribute)
        if args.command == "check":
            return 0
        import uvicorn

        uvicorn.run(application, host=args.host, port=args.port)
        return 0
    parser.print_help()
    return 0
