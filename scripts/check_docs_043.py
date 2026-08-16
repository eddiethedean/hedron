#!/usr/bin/env python3
"""Check DOCS-043 (delegates to _gate_043)."""

from __future__ import annotations

from _gate_043 import check_gate

if __name__ == "__main__":
    raise SystemExit(check_gate("DOCS-043"))
