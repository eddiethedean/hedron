"""CLI command: run an ASGI app."""

from __future__ import annotations

import argparse
import sys


def _cmd_run_app(args: argparse.Namespace) -> int:
    """Run locally, or delegate to the optional Workbench pre-import launcher."""
    import os

    target = str(args.target or args.app or "").strip()
    if not target or ":" not in target:
        print("hedron run requires module:attribute", file=sys.stderr)
        return 2
    workbench_runtime = bool(str(os.environ.get("RS_SERVER_URL") or "").strip())
    if args.workbench or workbench_runtime:
        try:
            from hedron_posit.config import (
                WorkbenchConfig,
                WorkbenchMode,
                WorkbenchTopology,
            )
            from hedron_posit.runner import run_target
        except ImportError:
            print(
                "Posit Workbench runtime detected but hedron-posit is not installed; "
                "install hedron[posit]",
                file=sys.stderr,
            )
            return 2
        config = WorkbenchConfig(
            mode=WorkbenchMode.parse(args.workbench_mode),
            host=args.host,
            port=args.port,
            mount=args.mount,
            public_base_url=args.public_base_url,
            forwarded_allow_ips=args.forwarded_allow_ips,
            allow_external_bind=args.allow_external_bind,
            reload=args.reload,
            workers=args.workers,
            debug=args.debug,
            factory=args.factory,
            app_target=target,
            topology=WorkbenchTopology.parse(args.topology),
        )
        run_target(target, config=config)
        return 0

    import uvicorn

    uvicorn.run(
        target,
        host=args.host or "127.0.0.1",
        port=args.port or 8000,
        reload=args.reload,
        workers=args.workers,
        factory=args.factory,
        log_level="debug" if args.debug else "info",
    )
    return 0
