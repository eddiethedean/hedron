"""CLI command: curated public API / stability discovery (DISCOVER-053)."""

from __future__ import annotations

import argparse
import json


def _cmd_discover(args: argparse.Namespace) -> int:
    from hedron.discover_api import discover_public_api

    payload = discover_public_api(format=args.format)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload, end="" if str(payload).endswith("\n") else "\n")
    return 0


cmd_discover = _cmd_discover
