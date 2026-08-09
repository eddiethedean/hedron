#!/usr/bin/env python3
"""STABLE-023: STABILITY expanded-tier section matches the locked 0.23 allowlist.

Requires ``docs/api/STABILITY.md`` to contain a section headed
``## Expanded stable tier (0.23)`` that mentions every symbol from the
machine-checked inventory in ``docs/api/STABLE_FACADE.md``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STABILITY = ROOT / "docs" / "api" / "STABILITY.md"
FACADE = ROOT / "docs" / "api" / "STABLE_FACADE.md"

SECTION = "## Expanded stable tier (0.23)"
INVENTORY_HEADING = "## Inventory (machine-checked)"
FENCE_RE = re.compile(r"```text\n(.*?)```", re.S)

REQUIRED_PHRASES = (
    "Published on the 0.23 train",
    "Out of 0.23",
    "job_status_sse_response",  # must be called out as excluded
    "STABLE_FACADE",
    "Migration",
)


def facade_symbols(text: str) -> list[str]:
    idx = text.find(INVENTORY_HEADING)
    if idx < 0:
        raise ValueError(f"missing {INVENTORY_HEADING!r} in {FACADE}")
    match = FENCE_RE.search(text[idx:])
    if not match:
        raise ValueError("missing facade inventory fence")
    symbols: list[str] = []
    for raw in match.group(1).splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        _, attr = line.split(":", 1)
        # Use leaf name for presence check (Hedron.region -> region also ok via full attr)
        symbols.append(attr.split(".")[-1])
        symbols.append(attr)
    return symbols


def main() -> int:
    errors: list[str] = []
    if not STABILITY.is_file():
        print(f"missing {STABILITY}", file=sys.stderr)
        return 1
    if not FACADE.is_file():
        print(f"missing {FACADE}", file=sys.stderr)
        return 1

    stability = STABILITY.read_text(encoding="utf-8")
    facade = FACADE.read_text(encoding="utf-8")

    idx = stability.find(SECTION)
    if idx < 0:
        print(f"STABILITY.md missing section {SECTION!r}", file=sys.stderr)
        return 1

    # Section body until next ## at column 0
    rest = stability[idx + len(SECTION) :]
    next_h = re.search(r"\n## ", rest)
    body = rest[: next_h.start()] if next_h else rest

    section_text = stability[idx:]
    next_major = re.search(r"\n## Artifact classes", section_text)
    scoped = section_text[: next_major.start()] if next_major else section_text[:8000]
    for phrase in REQUIRED_PHRASES:
        if phrase not in scoped:
            errors.append(f"expanded tier section missing required phrase: {phrase!r}")

    try:
        symbols = facade_symbols(facade)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    # Unique leaf names that must appear in the expanded-tier section body
    leaves = sorted({s.split(".")[-1] for s in symbols if s})
    missing = [name for name in leaves if name not in body]
    # html is tiny / easy to false-negative; Page/Text already in minimal tier — still require
    for name in missing:
        errors.append(f"expanded tier section missing allowlist symbol mention: {name}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: stable tier 0.23 allowlist ({len(leaves)} symbol mentions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
