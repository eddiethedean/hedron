"""CLI command: read-only installed-fleet diagnosis (FLEET-053)."""

from __future__ import annotations

import argparse
import json


def _cmd_fleet(args: argparse.Namespace) -> int:
    from hedron.fleet import diagnose_installed_fleet

    report = diagnose_installed_fleet()
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
    else:
        dists = report.get("distributions") or {}
        print(f"read_only={report.get('read_only')} package_doctor={report.get('package_doctor')}")
        print(f"hedron={dists.get('hedron')} hedron-core={dists.get('hedron-core')}")
        skew = report.get("train_skew")
        if skew:
            print(
                "train_skew "
                f"mismatch={skew.get('train_version_mismatch')} "
                f"multi={skew.get('multi_version_train')}"
            )
        for rec in report.get("recommendations") or []:
            print(f"- {rec.get('message')} (evidence: {rec.get('evidence')})")
    return 0
