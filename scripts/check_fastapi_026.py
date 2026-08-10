#!/usr/bin/env python3
"""FASTAPI-026: reference-app operational proof matrix (SSOT + smoke script)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHETYPE = ROOT / "docs" / "api" / "PRODUCTION_ARCHETYPE.md"
COMPOSE = ROOT / "examples" / "reference-app" / "docker-compose.yml"
SMOKE = ROOT / "scripts" / "smoke_fastapi_026.py"
REQUIRED_PHRASES = (
    "multi-worker",
    "Redis",
    "reverse-proxy",
    "HEDRON_ENV=production",
    "Explorer off",
)


def main() -> int:
    errors: list[str] = []
    for path in (ARCHETYPE, COMPOSE, SMOKE):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if ARCHETYPE.is_file():
        text = ARCHETYPE.read_text(encoding="utf-8")
        for phrase in REQUIRED_PHRASES:
            if phrase not in text:
                errors.append(f"PRODUCTION_ARCHETYPE.md missing {phrase!r}")

    if COMPOSE.is_file():
        compose = COMPOSE.read_text(encoding="utf-8")
        for needle in ("redis", "proxy", "HEDRON_ENV: production", "workers"):
            if needle not in compose and needle.replace(":", "") not in compose:
                # workers may be in Dockerfile CMD
                if needle == "workers":
                    dockerfile = ROOT / "examples" / "reference-app" / "Dockerfile"
                    if dockerfile.is_file() and "workers" not in dockerfile.read_text():
                        errors.append("reference-app must configure multi-worker")
                elif needle not in compose:
                    errors.append(f"docker-compose.yml missing {needle!r}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    cmd = [sys.executable, str(SMOKE)]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"FASTAPI-026 smoke failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: FASTAPI-026 operational proof")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
