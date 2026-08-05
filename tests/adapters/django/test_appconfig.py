"""Django AppConfig and system check tests (phase 0.11)."""

from __future__ import annotations

from io import StringIO

from django.apps import apps
from django.core.management import call_command


def test_hedron_django_config_loads() -> None:
    config = apps.get_app_config("hedron_django")
    assert config.name == "hedron_django"
    assert config.verbose_name == "Hedron Django"


def test_system_checks_run() -> None:
    out = StringIO()
    call_command("check", stdout=out, stderr=out)
