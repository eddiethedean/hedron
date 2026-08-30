"""Django AppConfig and system checks for hedron-django."""

from __future__ import annotations

from django.apps import AppConfig
from django.core.checks import CheckMessage, Error, Warning, register

__all__ = ["HedronDjangoConfig", "register_checks", "run_django_production_gates"]

_checks_registered = False


class HedronDjangoConfig(AppConfig):
    """Installable Django app for Hedron integration (idempotent, no I/O in ready)."""

    name = "hedron_django"
    label = "hedron_django"
    verbose_name = "Hedron Django"
    default_auto_field = "django.db.models.AutoField"  # pyright: ignore[reportIncompatibleVariableOverride]

    def ready(self) -> None:
        register_checks()
        run_django_production_gates()


def run_django_production_gates() -> None:
    """Fail closed on insecure production config (FastAPI Hedron() parity, #401)."""
    from django.core.exceptions import ImproperlyConfigured

    from hedron_core.compile_gate import is_production_env
    from hedron_core.production_gate import (
        assert_durable_backends,
        assert_production_security_config,
    )
    from hedron_core.security_policy import SecurityProfile
    from hedron_django.middleware import security_policy_from_settings

    try:
        from django.conf import settings

        secret = getattr(settings, "SECRET_KEY", None)
    except ImproperlyConfigured:
        return
    is_prod = is_production_env()
    policy = security_policy_from_settings()
    assert_durable_backends(
        production=is_prod,
        strict_profile=policy.profile is SecurityProfile.STRICT,
    )
    session_secret = secret if isinstance(secret, str) else (str(secret) if secret else None)
    assert_production_security_config(
        production=is_prod,
        security_profile=policy.profile.value,
        session_secret=session_secret,
        sessions_enabled=True,
        explorer_mode="off",
        allow_external_redirects=policy.allow_external_redirects,
        content_security_policy=policy.content_security_policy,
    )


def register_checks() -> None:
    """Register ``hedron.*`` system checks (safe to call multiple times)."""
    global _checks_registered
    if _checks_registered:
        return
    _checks_registered = True

    @register(deploy=True)  # type: ignore[misc,untyped-decorator]
    def hedron_django_version_check(  # pyright: ignore[reportUnusedFunction]
        app_configs: object, **kwargs: object
    ) -> list[CheckMessage]:
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
    def hedron_middleware_check(  # pyright: ignore[reportUnusedFunction]
        app_configs: object, **kwargs: object
    ) -> list[CheckMessage]:
        del app_configs, kwargs
        from django.conf import settings

        messages: list[CheckMessage] = []
        middleware = list(getattr(settings, "MIDDLEWARE", []))
        if "django.middleware.csrf.CsrfViewMiddleware" not in middleware:
            messages.append(
                Error(
                    "CsrfViewMiddleware is not installed; Hedron Django CSRF helpers require it.",
                    hint="Add 'django.middleware.csrf.CsrfViewMiddleware' to MIDDLEWARE.",
                    id="hedron.E003",
                )
            )
        if "django.contrib.sessions.middleware.SessionMiddleware" not in middleware:
            messages.append(
                Warning(
                    "SessionMiddleware is not installed; AuthSignal tenant/session facts need it.",
                    id="hedron.W002",
                )
            )
        security_mw = "hedron_django.middleware.HedronSecurityHeadersMiddleware"
        if security_mw not in middleware:
            messages.append(
                Warning(
                    "HedronSecurityHeadersMiddleware is not installed; "
                    "CSP / X-Frame-Options from HEDRON_SECURITY_PROFILE will not apply.",
                    hint=f"Add {security_mw!r} to MIDDLEWARE "
                    f"(and optionally set HEDRON_SECURITY_PROFILE).",
                    id="hedron.W003",
                )
            )
        return messages

    @register()  # type: ignore[misc,untyped-decorator]
    def hedron_capability_honesty_check(  # pyright: ignore[reportUnusedFunction]
        app_configs: object, **kwargs: object
    ) -> list[CheckMessage]:
        del app_configs, kwargs
        from hedron_core.adapter import DJANGO_CAPABILITIES

        messages: list[CheckMessage] = []
        qs_cap = next(
            (c for c in DJANGO_CAPABILITIES.capabilities if c.name == "queryset_datasource"),
            None,
        )
        if qs_cap is not None and not qs_cap.supported:
            messages.append(
                Error(
                    "queryset_datasource capability must be Supported (D-046).",
                    id="hedron.E002",
                )
            )
        return messages
