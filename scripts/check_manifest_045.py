#!/usr/bin/env python3
"""Check MANIFEST-045 (delegates to _gate_045)."""

from __future__ import annotations

from _gate_045 import check_gate

if __name__ == "__main__":
    raise SystemExit(check_gate("MANIFEST-045"))
