#!/usr/bin/env python3
"""Audit pinned browser assets (HTMX core digest + extension contract)."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTMX_PATH = ROOT / "packages" / "hedron" / "src" / "hedron" / "static" / "htmx.min.js"
# Exact pin for the 0.8 freeze (HTMX 2.0.10).
EXPECTED_VERSION = "2.0.10"
EXPECTED_SHA256 = "71ea67185bfa8c98c39d31717c6fce5d852370fcdfd129db4543774d3145c0de"


def main() -> int:
    errors: list[str] = []
    if not HTMX_PATH.is_file():
        errors.append(f"missing HTMX asset: {HTMX_PATH}")
    else:
        data = HTMX_PATH.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        text = data.decode("utf-8", errors="ignore")
        if EXPECTED_VERSION not in text:
            errors.append(f"HTMX asset missing version marker {EXPECTED_VERSION!r}")
        if digest != EXPECTED_SHA256:
            errors.append(f"HTMX digest mismatch: got {digest}, expected {EXPECTED_SHA256}")

    # Extension contract importable and SSE deferred
    sys.path.insert(0, str(ROOT / "packages" / "hedron-core" / "src"))
    from hedron_core.htmx_extensions import SSE_EXTENSION_DEFERRED, known_extensions

    if not SSE_EXTENSION_DEFERRED:
        errors.append("SSE_EXTENSION_DEFERRED must remain True through 0.8")
    exts = known_extensions()
    if not exts:
        errors.append("known_extensions() returned empty")

    report = {
        "htmx_version": EXPECTED_VERSION,
        "htmx_path": str(HTMX_PATH.relative_to(ROOT)),
        "htmx_sha256": EXPECTED_SHA256 if not errors else None,
        "sse_deferred": True,
        "extensions": [
            {"name": e.name, "version": e.version, "deferred": e.deferred, "digest": e.digest}
            for e in exts
        ],
    }
    out = ROOT / "dist" / "evidence-bundle"
    out.mkdir(parents=True, exist_ok=True)
    (out / "asset-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: asset audit (HTMX {EXPECTED_VERSION}, sha256={EXPECTED_SHA256[:12]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
