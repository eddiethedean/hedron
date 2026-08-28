"""Scaffold for ``hedron new --django``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hedron.cli.discovery import _scaffold_dep


def _scaffold_django(args: argparse.Namespace, dest: Path) -> int:
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "{_scaffold_dep("hedron-django")}",
    "{_scaffold_dep("hedron-core")}",
    "django>=5.2,<6",
    "waitress>=3,<4",
]

[tool.hedron]
component_roots = ["components"]
''',
        encoding="utf-8",
    )
    project = dest / "project"
    project.mkdir(exist_ok=True)
    (project / "__init__.py").write_text("", encoding="utf-8")
    (project / "settings.py").write_text(
        """import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production")
# Default off; set DJANGO_DEBUG=1 for local development.
DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "hedron_django",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "hedron_django.middleware.HedronSecurityHeadersMiddleware",
]
ROOT_URLCONF = "project.urls"
TEMPLATES = []
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
STATIC_URL = "static/"
HEDRON_SECURITY_PROFILE = "standard"
# Accept portable Hedron HTMX CSRF header (X-CSRF-Token) with stock CsrfViewMiddleware.
CSRF_HEADER_NAME = "HTTP_X_CSRF_TOKEN"
""",
        encoding="utf-8",
    )
    (project / "urls.py").write_text(
        """from datetime import datetime, timezone

from django.urls import path
from hedron_core import FragmentRegion, InteractionResult, Page, Text, html
from hedron_core.interaction import InteractionPolicy
from hedron_django import hedron_static_urlpatterns, hedron_view

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Django status · {stamp}"), id="panel")


@hedron_view(fragment_regions=(PANEL,))
def home(request):
    return Page(
        html.div(
            Text("Hello from hedron new --django"),
            panel_body(),
            html.button(
                Text("Refresh"),
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Home",
    )


@hedron_view(fragment_regions=(PANEL,))
def status(request):
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
    )


urlpatterns = [
    *hedron_static_urlpatterns(),
    path("", home, name="home"),
    path("status", status, name="status"),
]
""",
        encoding="utf-8",
    )
    (dest / "manage.py").write_text(
        """#!/usr/bin/env python
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
""",
        encoding="utf-8",
    )
    (dest / "wsgi.py").write_text(
        """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
application = get_wsgi_application()
""",
        encoding="utf-8",
    )
    (dest / "README.md").write_text(
        "# Hedron Django app\n\n"
        "Set `HEDRON_SESSION_SECRET` before production. "
        "Placeholder secrets are refused under `HEDRON_ENV=production` "
        "unless accepted via `HEDRON_SECURITY_RISK_ACCEPTANCE`.\n\n"
        "```bash\nuv sync && uv run waitress-serve --port=8000 wsgi:application\n```\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "django",
                "files": [
                    "pyproject.toml",
                    "manage.py",
                    "wsgi.py",
                    "project/",
                    "README.md",
                    "components/",
                ],
            },
            indent=2,
        )
    )
    return 0
