#!/usr/bin/env python3
"""Generate a minimal CycloneDX-like SBOM from uv.lock / package metadata."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]


def _lock_packages() -> list[dict[str, str]]:
    lock = ROOT / "uv.lock"
    if not lock.is_file():
        return []
    # uv.lock is TOML
    data = tomllib.loads(lock.read_text(encoding="utf-8"))
    packages = []
    for row in data.get("package", []):
        name = str(row.get("name", ""))
        version = str(row.get("version", ""))
        if name and version:
            packages.append({"name": name, "version": version, "type": "library"})
    return packages


def main() -> int:
    first_party = []
    for pyproject in sorted((ROOT / "packages").glob("*/pyproject.toml")):
        project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
        first_party.append(
            {
                "name": project["name"],
                "version": project["version"],
                "type": "library",
                "bom-ref": f"pkg:pypi/{project['name']}@{project['version']}",
            }
        )

    components = first_party + [
        {
            "name": row["name"],
            "version": row["version"],
            "type": "library",
            "bom-ref": f"pkg:pypi/{row['name']}@{row['version']}",
        }
        for row in _lock_packages()
        if row["name"] not in {p["name"] for p in first_party}
    ]

    lock_bytes = (ROOT / "uv.lock").read_bytes() if (ROOT / "uv.lock").is_file() else b""
    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": {
                "type": "application",
                "name": "hedron-workspace",
                "version": tomllib.loads((ROOT / "pyproject.toml").read_text())["project"][
                    "version"
                ],
            },
            "properties": [
                {
                    "name": "hedron:uv.lock.sha256",
                    "value": hashlib.sha256(lock_bytes).hexdigest() if lock_bytes else "",
                }
            ],
        },
        "components": components,
    }

    out_dir = ROOT / "dist" / "evidence-bundle"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "sbom.cdx.json"
    out.write_text(json.dumps(bom, indent=2) + "\n", encoding="utf-8")
    print(f"ok: wrote {out.relative_to(ROOT)} ({len(components)} components)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
