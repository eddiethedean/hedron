"""CLI command: language-neutral conformance kit."""

from __future__ import annotations

import argparse
import sys

from hedron.cli.arguments import boolean_argument


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
    if boolean_argument(args, "json"):
        argv.append("--json")
    return int(conformance_main(argv))


cmd_conformance = _cmd_conformance
