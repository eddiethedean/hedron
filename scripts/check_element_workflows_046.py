#!/usr/bin/env python3
"""Check ELEMENT-046 (delegates to _gate_046)."""

from __future__ import annotations

from _gate_046 import check_gate

if __name__ == "__main__":
    raise SystemExit(check_gate("ELEMENT-046"))
