#!/usr/bin/env python3
"""Check COMPAT-042 (delegates to _gate_042)."""

from __future__ import annotations

from _gate_042 import check_gate

if __name__ == "__main__":
    raise SystemExit(check_gate("COMPAT-042"))
