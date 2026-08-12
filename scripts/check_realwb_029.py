#!/usr/bin/env python3
"""Backward-compatible REALWB checker entrypoint (REALWB-030 dual-package smoke)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import check_realwb_smoke as smoke  # noqa: E402

SKIP_EXIT_CODE = smoke.SKIP_EXIT_CODE


def main(argv: list[str] | None = None) -> int:
    return smoke.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
