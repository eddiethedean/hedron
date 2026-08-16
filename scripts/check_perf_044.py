#!/usr/bin/env python3
"""Check PERF-044 (delegates to _gate_044)."""

from __future__ import annotations

from _gate_044 import check_gate

if __name__ == "__main__":
    raise SystemExit(check_gate("PERF-044"))
