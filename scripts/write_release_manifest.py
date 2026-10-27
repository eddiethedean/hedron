#!/usr/bin/env python3
"""Write checksums and sizes for every distributable release asset."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def asset_record(path: Path, *, root: Path = ROOT) -> dict[str, object]:
    return {
        "name": path.name,
        "source": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "size": path.stat().st_size,
    }


def git_commit() -> str:
    if value := os.environ.get("GITHUB_SHA"):
        return value
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[a-zA-Z0-9.-]+)?", args.version):
        raise SystemExit(f"invalid release version: {args.version!r}")

    assets = sorted(DIST.glob("*.whl")) + sorted(DIST.glob("*.tar.gz"))
    assets += sorted(path for path in (DIST / "evidence-bundle").glob("*") if path.is_file())
    if not assets:
        raise SystemExit("no release assets under dist/")
    names = [path.name for path in assets]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise SystemExit(f"duplicate release asset names: {', '.join(duplicates)}")

    payload = {
        "schema_version": 1,
        "project": "hedron",
        "release_version": args.version,
        "git_commit": git_commit(),
        "generated_at": datetime.now(UTC).isoformat(),
        "assets": [asset_record(path) for path in assets],
    }
    output = DIST / "release-manifest.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"ok: wrote {output.relative_to(ROOT)} with {len(assets)} checksums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
