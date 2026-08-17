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
if version not in {"0.41.0", "0.42.0", "0.43.0", "0.44.0", "0.45.0", "0.46.0"} and not version.startswith(
    ("0.42.", "0.43.", "0.44.", "0.45.", "0.46.")
):
    raise SystemExit(
        f"workspace version must be 0.41.0 or post-cut 0.42.x/0.43.x/0.44.x/0.45.x/0.46.x, got {version}"
    )
raise SystemExit(check("PKG-041"))
