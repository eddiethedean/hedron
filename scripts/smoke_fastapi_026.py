#!/usr/bin/env python3
"""FASTAPI-026 smoke: min-deps import, production gates, reference-app ingredients.

Does not require Docker. Exercises the Supported FastAPI path locally.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []

    # Minimum-dependency import of flagship + core (no optional extras required).
    for mod in ("hedron_core", "hedron"):
        try:
            importlib.import_module(mod)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"import {mod} failed: {exc}")

    # Experimental live helpers must not appear on the default package __all__.
    import hedron

    banned = {
        "job_status_sse_response",
        "SseResponse",
        "WebSocketChannel",
        "EventSourceResponse",
    }
    leaked = banned.intersection(set(hedron.__all__))
    if leaked:
        errors.append(f"experimental live APIs leaked into hedron.__all__: {sorted(leaked)}")

    # Production archetype files present for rollback/proxy/multi-worker ops.
    ref = ROOT / "examples" / "reference-app"
    for rel in (
        "docker-compose.yml",
        "Dockerfile",
        "Caddyfile",
        "app.py",
    ):
        if not (ref / rel).is_file():
            errors.append(f"missing reference-app/{rel}")

    dockerfile = (ref / "Dockerfile").read_text(encoding="utf-8")
    if "--workers 2" not in dockerfile:
        errors.append("Dockerfile must run uvicorn with --workers 2")
    compose = (ref / "docker-compose.yml").read_text(encoding="utf-8")
    if "redis" not in compose.lower():
        errors.append("compose must include Redis")
    if "proxy" not in compose.lower():
        errors.append("compose must include reverse proxy")

    # Offline-wheel / min-deps narrative retained in COMPATIBILITY + archetype.
    compat = (ROOT / "docs" / "COMPATIBILITY.md").read_text(encoding="utf-8")
    if "3.11" not in compat or "3.14" not in compat:
        errors.append("COMPATIBILITY.md must advertise Python 3.10–3.14")

    # Production startup gate module importable.
    try:
        from hedron import Hedron

        app = Hedron(
            title="fastapi-026-smoke",
            security="standard",
            explorer="off",
            session_secret="test-secret-fastapi-026-smoke",
        )
        # ASGI app constructible without Explorer.
        assert app is not None
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Hedron construct failed: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: smoke_fastapi_026")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
