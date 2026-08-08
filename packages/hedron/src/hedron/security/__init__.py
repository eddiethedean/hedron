"""Hedron security package."""

from __future__ import annotations

from hedron.security.auth_rate_limit import (
    AuthRateLimiter,
    auth_rate_limit_dependency,
    auth_rate_limit_exception,
    auth_rate_limit_response,
)
from hedron.security.csrf import (
    csrf_token_for_request,
    ensure_csrf_cookie,
    generate_csrf_token,
    validate_csrf,
)
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.login_csrf import (
    LOGIN_CSRF_KEY,
    issue_login_csrf,
    sign_login_csrf,
    validate_login_csrf,
)
from hedron.security.policy import (
    SecurityHeadersPolicy,
    SecurityPolicy,
    SecurityProfile,
    SecurityProfileName,
)
from hedron.security.redirects import redirect_external, redirect_local
from hedron.security.session_timeout import (
    SESSION_CREATED_KEY,
    SESSION_LAST_SEEN_KEY,
    SessionTimeoutError,
    check_session_timeout,
    touch_session,
)
from hedron.security.trusted_header import TrustedHeaderIdentity
from hedron_core.csrf_strategy import (
    CsrfStrategy,
    CsrfValidationError,
    DoubleSubmitCookieCsrf,
    SessionTokenCsrf,
)

__all__ = [
    "LOGIN_CSRF_KEY",
    "SESSION_CREATED_KEY",
    "SESSION_LAST_SEEN_KEY",
    "AuthRateLimiter",
    "CsrfStrategy",
    "CsrfValidationError",
    "DoubleSubmitCookieCsrf",
    "SecurityHeadersMiddleware",
    "SecurityHeadersPolicy",
    "SecurityPolicy",
    "SecurityProfile",
    "SecurityProfileName",
    "SessionTimeoutError",
    "SessionTokenCsrf",
    "TrustedHeaderIdentity",
    "auth_rate_limit_dependency",
    "auth_rate_limit_exception",
    "auth_rate_limit_response",
    "check_session_timeout",
    "csrf_token_for_request",
    "ensure_csrf_cookie",
    "generate_csrf_token",
    "issue_login_csrf",
    "redirect_external",
    "redirect_local",
    "sign_login_csrf",
    "touch_session",
    "validate_csrf",
    "validate_login_csrf",
]
