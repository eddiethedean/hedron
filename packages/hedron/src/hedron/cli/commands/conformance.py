"""CLI command: language-neutral conformance kit."""

from __future__ import annotations

import argparse
import sys


def _cmd_conformance(args: argparse.Namespace) -> int:
    """Run the published language-neutral conformance kit (phase 0.14)."""
    try:
        from hedron_conformance.cli import main as conformance_main
    except ImportError:
        print(
            "hedron-conformance is not installed. Install with: pip install 'hedron[conformance]'",
            file=sys.stderr,
        )
        return 2
    argv = ["run"]
    if args.json:
        argv.append("--json")
    return int(conformance_main(argv))
