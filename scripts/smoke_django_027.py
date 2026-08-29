#!/usr/bin/env python3
"""DJANGO-027 smoke: import hedron_django without FastAPI; system checks."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    try:
        django_mod = importlib.import_module("hedron_django")
    except Exception as exc:  # noqa: BLE001
        print(f"import hedron_django failed: {exc}", file=sys.stderr)
        return 1

    src = (ROOT / "packages" / "hedron-django" / "src" / "hedron_django").rglob("*.py")
    for path in src:
        text = path.read_text(encoding="utf-8")
        if "import fastapi" in text or "from fastapi" in text:
            errors.append(f"{path.relative_to(ROOT)} imports FastAPI")

    ref = ROOT / "examples" / "django-reference"
    if (
        not (ref / "manage.py").is_file()
        and not (ref / "asgi.py").is_file()
        and not (ref / "hedron_django_ref").is_dir()
    ):
        # Reference may be a package layout without manage.py.
        errors.append("missing examples/django-reference package")

    # Lightweight Django configure + system check using package AppConfig.
    try:
        import django
        from django.conf import settings

        if not settings.configured:
            settings.configure(
                DEBUG=True,
                SECRET_KEY="django-027-smoke",
                ROOT_URLCONF="tests.adapters.django.urls",
                ALLOWED_HOSTS=["testserver"],
                MIDDLEWARE=[
                    "django.middleware.security.SecurityMiddleware",
                    "django.contrib.sessions.middleware.SessionMiddleware",
                    "django.middleware.common.CommonMiddleware",
                    "django.middleware.csrf.CsrfViewMiddleware",
                    "django.contrib.auth.middleware.AuthenticationMiddleware",
                ],
                INSTALLED_APPS=[
                    "django.contrib.contenttypes",
                    "django.contrib.auth",
                    "django.contrib.sessions",
                    "hedron_django.apps.HedronDjangoConfig",
                ],
                DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
                USE_TZ=True,
            )
            django.setup()
        from django.core.management import call_command

        call_command("check", verbosity=0)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"django system check failed: {exc}")

    if not hasattr(django_mod, "hedron_view") and not hasattr(django_mod, "Hedron"):
        # Accept either public helper naming used by the adapter.
        public = [n for n in dir(django_mod) if not n.startswith("_")]
        if "respond" not in public and "hedron_view" not in public:
            errors.append("hedron_django missing expected public helpers")

    # Keep unused import warning quiet for optional env toggles.
    _ = os.environ.get("DJANGO_SETTINGS_MODULE")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: smoke_django_027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
