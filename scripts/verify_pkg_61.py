#!/usr/bin/env python3
"""Executable phase 0.61 packet verifier."""

from __future__ import annotations

import argparse

from _gate_061 import check_gate, validate_packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args()
    errors = validate_packet(allow_planned=args.allow_planned)
    if errors:
        print("\n".join(errors))
        return 1
    return check_gate("PKG-061", allow_planned=args.allow_planned)


if __name__ == "__main__":
    raise SystemExit(main())
