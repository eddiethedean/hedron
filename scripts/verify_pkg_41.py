#!/usr/bin/env python3
"""Verify the untagged phase 0.41 release candidate (historical after 0.42 tip)."""

from __future__ import annotations

import tomllib

from _gate_041 import EXPECTED, GATE, ROOT, check

data = tomllib.loads(GATE.read_text())
rows = data["evidence"]
if tuple(row["id"] for row in rows) != EXPECTED or any(row["state"] != "Verified" for row in rows):
    raise SystemExit("all 0.41 gates must be Verified")
version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
if version not in {
    "0.41.0",
    "0.42.0",
    "0.43.0",
    "0.44.0",
    "0.45.0",
    "0.46.0",
    "0.47.0",
    "0.48.0",
    "0.49.0",
    "0.50.0",
    "0.51.0",
} and not version.startswith(
    (
        "0.42.",
        "0.43.",
        "0.44.",
        "0.45.",
        "0.46.",
        "0.47.",
        "0.48.",
        "0.49.",
        "0.50.",
        "0.51.",
        "0.52.",
        "0.53.",
        "0.54.", "0.55.", "0.56.", "0.57.", "0.58.", "0.59.",
    )
):
    raise SystemExit(f"workspace version must be 0.41.0 or post-cut 0.42.x–0.59.x, got {version}")
raise SystemExit(check("PKG-041"))
