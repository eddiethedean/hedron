#!/usr/bin/env python3
"""Verify the untagged phase 0.41 release candidate."""

from __future__ import annotations

import tomllib

from _gate_041 import EXPECTED, GATE, ROOT, check

data = tomllib.loads(GATE.read_text())
rows = data["evidence"]
if tuple(row["id"] for row in rows) != EXPECTED or any(row["state"] != "Verified" for row in rows):
    raise SystemExit("all 0.41 gates must be Verified")
version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
if version != "0.41.0":
    raise SystemExit(f"workspace version must be 0.41.0, got {version}")
raise SystemExit(check("PKG-041"))
