#!/usr/bin/env python3
"""REVIEW-033: security review brief present (full packet at cut)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import REVIEW_BRIEF, fail_errors, require_files  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-planned",
        action="store_true",
        help="Accept brief-only packet during refine",
    )
    args = parser.parse_args(argv)
    errors: list[str] = []
    require_files([REVIEW_BRIEF], errors)
    if not args.allow_planned:
        packet = REVIEW_BRIEF.parent
        for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
            path = packet / name
            if not path.is_file():
                errors.append(f"missing review artifact: {path.relative_to(ROOT)}")
    if fail_errors(errors, "REVIEW-033"):
        return 1
    print("ok: REVIEW-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
