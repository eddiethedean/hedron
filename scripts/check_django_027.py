#!/usr/bin/env python3
"""DJANGO-027: host-only Django adapter graduation evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_027 import (  # noqa: E402
    require_files,
    require_inventory_supported,
    run_pytest,
    run_script,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "examples" / "django-reference" / "asgi.py",
            ROOT / "docs" / "getting-started" / "django.md",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-django",
        (
            "django_views",
            "django_middleware",
            "django_forms",
            "source_queryset_bounded",
            "polling_jobs",
            "system_checks",
        ),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_script("scripts/smoke_django_027.py", "DJANGO-027 smoke"):
        return 1
    if run_pytest(
        [
            "tests/adapters/django/test_django_adapter.py",
            "tests/adapters/django/test_django_hardening.py",
            "tests/adapters/django/test_forms_bridge.py",
            "tests/upgrade/test_0_26_0_to_0_27_satellites.py::test_adapter_interaction_polling_only",
        ],
        "DJANGO-027",
    ):
        return 1
    print("ok: DJANGO-027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
