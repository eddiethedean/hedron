"""Django AppConfig and system check tests (phase 0.11)."""

from __future__ import annotations

from django.apps import apps
from django.core.checks import Error, run_checks


def test_hedron_django_config_loads() -> None:
    config = apps.get_app_config("hedron_django")
    assert config.name == "hedron_django"
    assert config.verbose_name == "Hedron Django"


def test_system_checks_run() -> None:
    messages = run_checks()
    errors = [
        m for m in messages if isinstance(m, Error) or getattr(m, "id", "").startswith("hedron.E")
    ]
    assert errors == [], f"unexpected system check errors: {errors}"
    ids = {getattr(m, "id", "") for m in messages}
    # Middleware fixture installs CSRF + Session; capability honesty must agree.
    assert "hedron.E001" not in ids
    assert "hedron.E002" not in ids
    assert "hedron.E003" not in ids
    assert "hedron.W002" not in ids
    assert "hedron.W003" not in ids


def test_register_checks_idempotent() -> None:
    from hedron_django.apps import register_checks

    register_checks()
    register_checks()
    messages = run_checks()
    errors = [m for m in messages if getattr(m, "id", "").startswith("hedron.E")]
    assert errors == []
