#!/usr/bin/env python3
"""Verify downloaded or locally built release assets against their manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        help="Directory containing downloaded assets (defaults to manifest directory)",
    )
    args = parser.parse_args()
    artifact_dir = args.artifact_dir or args.manifest.parent
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    problems: list[str] = []
    for asset in data.get("assets", []):
        name = asset["name"]
        matches = list(artifact_dir.rglob(name))
        if len(matches) != 1:
            problems.append(f"{name}: expected one file, found {len(matches)}")
            continue
        path = matches[0]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != asset["sha256"]:
            problems.append(f"{name}: SHA-256 mismatch")
        if path.stat().st_size != asset["size"]:
            problems.append(f"{name}: size mismatch")
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"ok: verified {len(data['assets'])} release assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
