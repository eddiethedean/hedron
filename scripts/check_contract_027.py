#!/usr/bin/env python3
"""CONTRACT-027: satellite production-grade inventory agrees with docs and install guards."""

from __future__ import annotations

import importlib
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-027.toml"
REQUIRED_PACKAGES = (
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-extras",
)
REQUIRED_DOCS = (
    ROOT / "docs" / "api" / "STABILITY.md",
    ROOT / "docs" / "api" / "LIVE_DISPOSITION.md",
    ROOT / "docs" / "api" / "DATA.md",
    ROOT / "docs" / "api" / "JINJA.md",
    ROOT / "docs" / "acceptance" / "extras-quarantine-025.toml",
    ROOT / "docs" / "rfcs" / "RFC-0058-PRODUCTION-GRADE-SATELLITES.md",
)
ALLOW_EMPTY_EXPERIMENTAL = frozenset({"hedron-data", "hedron-jinja"})


def main() -> int:
    errors: list[str] = []
    if not INVENTORY.is_file():
        print(f"missing {INVENTORY.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    if data.get("baseline") != "v0.26.0":
        errors.append("inventory baseline must be v0.26.0")
    packages = data.get("packages")
    if packages != list(REQUIRED_PACKAGES):
        errors.append(f"packages must be {list(REQUIRED_PACKAGES)!r}, got {packages!r}")

    for name in REQUIRED_PACKAGES:
        section = data.get(name)
        if not isinstance(section, dict):
            errors.append(f"missing [{name}] section")
            continue
        for key in ("supported", "experimental", "excluded"):
            value = section.get(key)
            if not isinstance(value, list):
                errors.append(f"{name}.{key} must be a list")
            elif not value and key != "experimental":
                errors.append(f"{name}.{key} must be non-empty")
            elif not value and key == "experimental" and name not in ALLOW_EMPTY_EXPERIMENTAL:
                errors.append(f"{name}.experimental must be non-empty")

    flask_exp = set(data.get("hedron-flask", {}).get("experimental", []))
    django_exp = set(data.get("hedron-django", {}).get("experimental", []))
    if "experimental_live_helpers" not in flask_exp:
        errors.append("hedron-flask.experimental must include experimental_live_helpers")
    if "experimental_live_helpers" not in django_exp:
        errors.append("hedron-django.experimental must include experimental_live_helpers")

    extras_exp = set(data.get("hedron-extras", {}).get("experimental", []))
    for required in ("experimental_ui", "codeeditor_host_stub"):
        if required not in extras_exp:
            errors.append(f"hedron-extras.experimental must include {required}")

    guards = data.get("install_guards") or {}
    if guards.get("extras_default_enables_experimental_ui") is not False:
        errors.append("install_guards.extras_default_enables_experimental_ui must be false")
    if guards.get("adapters_import_without_fastapi") is not True:
        errors.append("install_guards.adapters_import_without_fastapi must be true")
    if guards.get("data_default_enables_silent_dataframe_extras") is not False:
        errors.append("install_guards.data_default_enables_silent_dataframe_extras must be false")
    if guards.get("jinja_default_enables_every_extension") is not False:
        errors.append("install_guards.jinja_default_enables_every_extension must be false")

    anchors = data.get("docs_anchors") or {}
    for key, rel in (
        ("stability", "docs/api/STABILITY.md"),
        ("extras_quarantine", "docs/acceptance/extras-quarantine-025.toml"),
        ("live_disposition", "docs/api/LIVE_DISPOSITION.md"),
        ("data_api", "docs/api/DATA.md"),
        ("jinja_api", "docs/api/JINJA.md"),
    ):
        if anchors.get(key) != rel:
            errors.append(f"docs_anchors.{key} must be {rel!r}")

    for path in REQUIRED_DOCS:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
        elif path.name == "LIVE_DISPOSITION.md":
            text = path.read_text(encoding="utf-8")
            if "polling_only" not in text:
                errors.append("LIVE_DISPOSITION.md must retain polling_only")

    # Default curated extras must not export experimental landmines.
    try:
        extras = importlib.import_module("hedron_extras")
        banned = {"TerminalView", "Joystick", "DeviceBridge", "CodeEditor"}
        leaked = banned.intersection(set(getattr(extras, "__all__", ())))
        if leaked:
            errors.append(f"hedron_extras.__all__ must not export {sorted(leaked)}")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"import hedron_extras failed: {exc}")

    # Adapters must import without FastAPI being a hard requirement at import time.
    for mod in ("hedron_flask", "hedron_django"):
        try:
            importlib.import_module(mod)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"import {mod} failed: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: CONTRACT-027 production-grade inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
