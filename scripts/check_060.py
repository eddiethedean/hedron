#!/usr/bin/env python3
"""Run one phase 0.60 gate's executable evidence."""

from __future__ import annotations

import argparse

from _gate_060 import check_gate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args()
    return check_gate(args.gate, allow_planned=args.allow_planned)


if __name__ == "__main__":
    raise SystemExit(main())
