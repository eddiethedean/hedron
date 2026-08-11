"""CSRF double-submit cookie helpers for Flask (same token semantics as FastAPI adapter)."""

from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from werkzeug.exceptions import Forbidden

from hedron_core.csrf_strategy import DoubleSubmitCookieCsrf
from hedron_core.security_policy import SecurityPolicy, SecurityProfile

if TYPE_CHECKING:
    from flask import Request, Response

__all__ = [
    "assert_flask_csrf_strategy",
    "csrf_cookie_force_secure",
    "csrf_cookie_should_be_secure",
    "csrf_token_for_request",
    "ensure_csrf_cookie",
    "extract_csrf_from_form",
    "generate_csrf_token",
    "validate_csrf",
]

DEFAULT_CSRF_COOKIE = "hedron_csrf"
DEFAULT_CSRF_HEADER = "X-CSRF-Token"


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def assert_flask_csrf_strategy(policy: SecurityPolicy) -> None:
    """Flask only supports double-submit cookie CSRF (or CSRF disabled)."""
    if not policy.csrf_enabled:
        return
    strategy = policy.resolve_csrf_strategy()
    if strategy is None:
        return
    if isinstance(strategy, DoubleSubmitCookieCsrf):
        return
    # Default resolve without explicit csrf= is DoubleSubmitCookieCsrf.
    if policy.csrf is None:
        return
    raise ValueError(
        "Flask CSRF only supports DoubleSubmitCookieCsrf (or csrf_enabled=False); "
        f"got {type(strategy).__name__}. Use the FastAPI host for SessionTokenCsrf."
    )


def csrf_token_for_request(
    request: Request,
    *,
    cookie_name: str = DEFAULT_CSRF_COOKIE,
    policy: SecurityPolicy | None = None,
) -> str:
    if policy is not None:
        if not policy.csrf_enabled:
            return ""
        strategy = policy.resolve_csrf_strategy()
        if strategy is None:
            return ""
        assert_flask_csrf_strategy(policy)
        cookie_name = getattr(strategy, "cookie_name", cookie_name) or cookie_name
    existing = request.cookies.get(cookie_name)
    if isinstance(existing, str) and existing:
        return existing
    cached = getattr(request, "_hedron_csrf_token", None)
    if isinstance(cached, str) and cached:
        return cached
    value = generate_csrf_token()
    request._hedron_csrf_token = value  # type: ignore[attr-defined]
    return value


def _forwarded_proto_https(request: Request) -> bool:
    proto = request.headers.get("X-Forwarded-Proto", "")
    first = proto.split(",")[0].strip().lower() if proto else ""
    return first == "https"


def _trusted_proxy_peers(request: Request) -> set[str]:
    """Peers allowed to supply ``X-Forwarded-*`` (same allowlist model as FastAPI)."""
    import os

    peers: set[str] = set()
    raw_env = os.environ.get("HEDRON_TRUSTED_PROXIES", "")
    peers.update(part.strip() for part in raw_env.split(",") if part.strip())
    app = getattr(request, "app", None)
    if app is not None:
        configured = app.config.get("HEDRON_TRUSTED_PROXIES") if hasattr(app, "config") else None
        if isinstance(configured, str):
            peers.update(part.strip() for part in configured.split(",") if part.strip())
        elif isinstance(configured, (list, tuple, set, frozenset)):
            peers.update(str(item).strip() for item in configured if str(item).strip())
        extension = app.extensions.get("hedron") if hasattr(app, "extensions") else None
        ext_peers = getattr(extension, "trusted_peers", None) if extension is not None else None
        if isinstance(ext_peers, (list, tuple, set, frozenset)):
            peers.update(str(item).strip() for item in ext_peers if str(item).strip())
    return peers


def _forwarded_proto_https_trusted(request: Request) -> bool:
    """Honor ``X-Forwarded-Proto: https`` only from allowlisted proxy peers."""
    if not _forwarded_proto_https(request):
        return False
    peers = _trusted_proxy_peers(request)
    if not peers:
        return False
    # Werkzeug exposes remote_addr; environ REMOTE_ADDR is the TCP peer.
    peer = getattr(request, "remote_addr", None) or request.environ.get("REMOTE_ADDR")
    return peer is not None and peer in peers


def csrf_cookie_force_secure(
    force_secure: bool | None,
    policy: SecurityPolicy | None = None,
) -> bool | None:
    """Resolve the force-Secure override for CSRF cookies.

    Explicit ``True``/``False`` wins. When unset, STRICT profiles force Secure
    (FastAPI STRICT parity) so ``HedronFlask(..., security="strict")`` alone
    emits Secure cookies on plain HTTP.
    """
    if force_secure is True or force_secure is False:
        return force_secure
    if policy is not None and policy.profile is SecurityProfile.STRICT:
        return True
    return None


def csrf_cookie_should_be_secure(
    request: Request,
    *,
    force_secure: bool | None = None,
) -> bool:
    """Resolve Secure flag for CSRF cookies.

    ``force_secure=True`` matches FastAPI STRICT (always Secure, including plain
    HTTP to the app behind a TLS-terminating proxy). ``None`` follows
    ``request.is_secure``, trusted-peer ``X-Forwarded-Proto: https``, or forces
    Secure when ``HEDRON_ENV`` / ``FLASK_ENV`` / ``ENV`` is ``production`` (or
    ``HEDRON_ENV=prod``).
    """
    from hedron_core.csrf_secure import csrf_cookie_should_be_secure as shared

    return shared(
        force_secure=force_secure,
        request_is_secure=bool(request.is_secure),
        forwarded_proto_https_trusted=bool(_forwarded_proto_https_trusted(request)),
        extra_production_env_vars=("FLASK_ENV", "ENV"),
    )


def ensure_csrf_cookie(
    response: Response,
    token: str,
    *,
    cookie_name: str = DEFAULT_CSRF_COOKIE,
    secure: bool = False,
    path: str = "/",
) -> None:
    response.set_cookie(
        cookie_name,
        token,
        httponly=False,
        samesite="Lax",
        secure=secure,
        path=path or "/",
    )


def extract_csrf_from_form(form: dict[str, str], *, field_name: str = "csrf_token") -> str | None:
    value = form.get(field_name)
    return value if isinstance(value, str) and value else None


def validate_csrf(
    request: Request,
    *,
    cookie_name: str = DEFAULT_CSRF_COOKIE,
    header_name: str = DEFAULT_CSRF_HEADER,
    form_field: str = "csrf_token",
    policy: SecurityPolicy | None = None,
) -> None:
    if policy is not None:
        if not policy.csrf_enabled:
            return
        strategy = policy.resolve_csrf_strategy()
        if strategy is None:
            return
        assert_flask_csrf_strategy(policy)
        form_value = None
        if request.form:
            form_value = extract_csrf_from_form(
                dict(request.form),
                field_name=strategy.form_field,
            )
        header_value = request.headers.get(strategy.header_name)
        try:
            strategy.validate(
                request,
                form_value=form_value,
                header_value=header_value if isinstance(header_value, str) else None,
            )
        except Exception as exc:
            from hedron_core.audit import SecurityAuditEventType, emit_security_audit
            from hedron_core.csrf_strategy import CsrfValidationError

            if not isinstance(exc, CsrfValidationError):
                raise
            emit_security_audit(
                SecurityAuditEventType.CSRF_REJECTED,
                "Invalid CSRF token",
                attributes={"path": request.path, "method": request.method},
            )
            raise Forbidden("Invalid CSRF token") from exc
        return

    cookie = request.cookies.get(cookie_name)
    if not cookie:
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "Missing CSRF cookie",
            attributes={"path": request.path, "method": request.method},
        )
        raise Forbidden("Missing CSRF cookie")
    submitted = request.headers.get(header_name)
    if not submitted and request.form:
        submitted = extract_csrf_from_form(dict(request.form), field_name=form_field)
    if not submitted or not secrets.compare_digest(cookie, submitted):
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.CSRF_REJECTED,
            "Invalid CSRF token",
            attributes={"path": request.path, "method": request.method},
        )
        raise Forbidden("Invalid CSRF token")
