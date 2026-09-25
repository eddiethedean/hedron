"""CLI command: read-only installed-fleet diagnosis (FLEET-053)."""

from __future__ import annotations

import argparse
import json
from typing import cast

from hedron.cli.arguments import string_argument


def _mapping(value: object) -> dict[str, object]:
    return cast(dict[str, object], value) if isinstance(value, dict) else {}


def _cmd_fleet(args: argparse.Namespace) -> int:
    from hedron.fleet import diagnose_installed_fleet

    report = diagnose_installed_fleet()
    if string_argument(args, "format", "human") == "json":
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
    else:
        dists = _mapping(report.get("distributions"))
        print(f"read_only={report.get('read_only')} package_doctor={report.get('package_doctor')}")
        print(f"hedron={dists.get('hedron')} hedron-core={dists.get('hedron-core')}")
        skew = _mapping(report.get("train_skew"))
        if skew:
            print(
                "train_skew "
                + f"mismatch={skew.get('train_version_mismatch')} "
                + f"multi={skew.get('multi_version_train')}"
            )
        recommendations: object = report.get("recommendations") or []
        for rec_value in (
            cast(list[object], recommendations) if isinstance(recommendations, list) else []
        ):
            rec = _mapping(rec_value)
            print(f"- {rec.get('message')} (evidence: {rec.get('evidence')})")
    return 0


cmd_fleet = _cmd_fleet
