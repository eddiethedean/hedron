"""Django AppConfig and system checks for hedron-django."""

from __future__ import annotations

from typing import Any, ClassVar

from django.apps import AppConfig
from django.core.checks import CheckMessage, Error, Warning, register

__all__ = ["HedronDjangoConfig", "register_checks"]

_checks_registered = False


class HedronDjangoConfig(AppConfig):
    """Installable Django app for Hedron integration (idempotent, no I/O in ready)."""

    name = "hedron_django"
    label = "hedron_django"
    verbose_name = "Hedron Django"
    default_auto_field: ClassVar[str] = "django.db.models.AutoField"

    def ready(self) -> None:
        register_checks()


def register_checks() -> None:
    """Register ``hedron.*`` system checks (safe to call multiple times)."""
    global _checks_registered
    if _checks_registered:
        return
    _checks_registered = True

    @register(deploy=True)  # type: ignore[misc,untyped-decorator]
    def hedron_django_version_check(app_configs: Any, **kwargs: Any) -> list[CheckMessage]:
        del app_configs, kwargs
        messages: list[CheckMessage] = []
        import django

        major_minor = tuple(int(p) for p in django.get_version().split(".")[:2])
        if major_minor < (5, 2):
            messages.append(
                Error(
                    f"hedron-django requires Django >=5.2 (found {django.get_version()}).",
                    id="hedron.E001",
                )
            )
        return messages

    @register()  # type: ignore[misc,untyped-decorator]
    def hedron_middleware_check(app_configs: Any, **kwargs: Any) -> list[CheckMessage]:
        del app_configs, kwargs
        from django.conf import settings

        messages: list[CheckMessage] = []
        middleware = list(getattr(settings, "MIDDLEWARE", []))
        if "django.middleware.csrf.CsrfViewMiddleware" not in middleware:
            messages.append(
                Warning(
                    "CsrfViewMiddleware is not installed; Hedron Django CSRF helpers expect it.",
                    id="hedron.W001",
                )
            )
        if "django.contrib.sessions.middleware.SessionMiddleware" not in middleware:
            messages.append(
                Warning(
                    "SessionMiddleware is not installed; AuthSignal tenant/session facts need it.",
                    id="hedron.W002",
                )
            )
        return messages

    @register()  # type: ignore[misc,untyped-decorator]
    def hedron_capability_honesty_check(app_configs: Any, **kwargs: Any) -> list[CheckMessage]:
        del app_configs, kwargs
        from hedron_core.adapter import DJANGO_CAPABILITIES
        from hedron_django.app import QUERYSET_DATASOURCE_DEFERRED

        messages: list[CheckMessage] = []
        qs_cap = next(
            (c for c in DJANGO_CAPABILITIES.capabilities if c.name == "queryset_datasource"),
            None,
        )
        if qs_cap is not None and qs_cap.supported == QUERYSET_DATASOURCE_DEFERRED:
            messages.append(
                Error(
                    "queryset_datasource capability and QUERYSET_DATASOURCE_DEFERRED disagree.",
                    id="hedron.E002",
                )
            )
        return messages
