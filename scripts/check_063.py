"""CLI entry point for phase 0.63 packet and gate validation."""

from __future__ import annotations

import argparse

from _gate_063 import EXPECTED_GATES, check_gate, validate_packet


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", choices=EXPECTED_GATES, default=None)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args()
    if args.gate:
        return check_gate(args.gate, verify=args.verify, allow_planned=args.allow_planned)
    errors = validate_packet(allow_planned=args.allow_planned)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
