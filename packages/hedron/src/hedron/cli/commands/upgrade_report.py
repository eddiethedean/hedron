"""CLI: offline application upgrade compatibility report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hedron.workflow import build_upgrade_report, load_baseline


def _cmd_upgrade_report(args: argparse.Namespace) -> None:
    baseline = None
    if args.baseline:
        baseline = load_baseline(Path(args.baseline))
    report = build_upgrade_report(
        from_version=args.from_version,
        to_version=args.to_version,
        baseline=baseline,
    )
    payload = report.to_dict()
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(text + "\n")
    raise SystemExit(report.exit_code(fail_on_definite=not args.allow_definite))
