#!/usr/bin/env python3
"""Check PLUGIN-040 (delegates to _gate_040)."""

from __future__ import annotations

from _gate_040 import check_gate

if __name__ == "__main__":
    raise SystemExit(check_gate("PLUGIN-040"))
