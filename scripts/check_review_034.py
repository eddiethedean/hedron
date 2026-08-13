#!/usr/bin/env python3
"""REVIEW-034: security review packet for hedron-gradio."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import REVIEW_BRIEF, fail_errors, require_files  # noqa: E402


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
    packet = REVIEW_BRIEF.parent
    if not args.allow_planned:
        for name in ("REDACTED_REPORT.md", "DISPOSITION.toml"):
            path = packet / name
            if not path.is_file():
                errors.append(f"missing review artifact: {path.relative_to(ROOT)}")
        disposition = packet / "DISPOSITION.toml"
        if disposition.is_file() and "critical_high_open = true" in disposition.read_text():
            errors.append("REVIEW-034: critical_high_open must be false at cut")
    if fail_errors(errors, "REVIEW-034"):
        return 1
    print("ok: REVIEW-034")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
