#!/usr/bin/env python3
"""CONTRACT-026: production-grade inventory agrees with docs and install guards."""

from __future__ import annotations

import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-026.toml"
REQUIRED_DOCS = (
    ROOT / "docs" / "api" / "STABILITY.md",
    ROOT / "docs" / "api" / "STABLE_FACADE.md",
    ROOT / "docs" / "api" / "LIVE_DISPOSITION.md",
    ROOT / "docs" / "rfcs" / "RFC-0057-PRODUCTION-GRADE-CORE.md",
)
REQUIRED_PACKAGES = ("hedron-core", "hedron", "hedron-explorer")
REQUIRED_HEDRON_EXPERIMENTAL = ("sse", "websocket", "streaming", "preload", "hedron.experimental")


def main() -> int:
    errors: list[str] = []
    if not INVENTORY.is_file():
        print(f"missing {INVENTORY.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    if data.get("baseline") != "v0.25.2":
        errors.append("inventory baseline must be v0.25.2")
    packages = data.get("packages")
    if packages != list(REQUIRED_PACKAGES):
        errors.append(f"packages must be {list(REQUIRED_PACKAGES)!r}, got {packages!r}")

    for name in REQUIRED_PACKAGES:
        section = data.get(name)
        if not isinstance(section, dict):
            errors.append(f"missing [{name}] section")
            continue
        for key in ("supported", "experimental", "excluded"):
            if not isinstance(section.get(key), list) or not section[key]:
                if name == "hedron-explorer" and key == "experimental":
                    continue
                if not isinstance(section.get(key), list):
                    errors.append(f"{name}.{key} must be a list")
                elif key != "experimental":
                    errors.append(f"{name}.{key} must be non-empty")

    hedron_exp = set(data.get("hedron", {}).get("experimental", []))
    missing_live = [item for item in REQUIRED_HEDRON_EXPERIMENTAL if item not in hedron_exp]
    if missing_live:
        errors.append(f"hedron.experimental inventory missing live items: {missing_live}")

    guards = data.get("install_guards") or {}
    if guards.get("hedron_default_enables_experimental_live") is not False:
        errors.append("install_guards.hedron_default_enables_experimental_live must be false")
    if guards.get("explorer_public_by_default") is not False:
        errors.append("install_guards.explorer_public_by_default must be false")
    if guards.get("explorer_required_at_runtime") is not False:
        errors.append("install_guards.explorer_required_at_runtime must be false")

    anchors = data.get("docs_anchors") or {}
    for key, rel in (
        ("stability", "docs/api/STABILITY.md"),
        ("stable_facade", "docs/api/STABLE_FACADE.md"),
        ("live_disposition", "docs/api/LIVE_DISPOSITION.md"),
    ):
        if anchors.get(key) != rel:
            errors.append(f"docs_anchors.{key} must be {rel!r}")

    for path in REQUIRED_DOCS:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
        else:
            text = path.read_text(encoding="utf-8")
            if path.name == "LIVE_DISPOSITION.md" and "polling_only" not in text:
                errors.append("LIVE_DISPOSITION.md must retain polling_only")
            if path.name == "STABLE_FACADE.md" and "hedron.experimental" not in text:
                errors.append("STABLE_FACADE.md must deny experimental live exports")

    # Default hedron import must not pull experimental live helpers into __all__.
    init = (ROOT / "packages" / "hedron" / "src" / "hedron" / "__init__.py").read_text(
        encoding="utf-8"
    )
    for banned in (
        "job_status_sse_response",
        "SseResponse",
        "WebSocketChannel",
        "StreamingResponse",
    ):
        # Presence in __getattr__ path is OK; must not be a static __all__ export.
        if f'"{banned}"' in init.split("__all__")[-1].split("]")[0]:
            errors.append(f"hedron.__all__ must not export experimental {banned}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: CONTRACT-026 production-grade inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
