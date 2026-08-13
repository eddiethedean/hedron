"""Shared CSRF cookie Secure-flag resolution for host adapters."""

from __future__ import annotations

import os

from hedron_core.compile_gate import is_production_env

__all__ = ["csrf_cookie_should_be_secure"]


def csrf_cookie_should_be_secure(
    *,
    force_secure: bool | None = None,
    request_is_secure: bool = False,
    forwarded_proto_https_trusted: bool = False,
    extra_production_env_vars: tuple[str, ...] = (),
) -> bool:
    """Resolve whether a CSRF cookie should set the Secure flag.

    ``force_secure=True`` always Secure (STRICT / TLS-terminating proxy).
    ``force_secure=False`` never Secure from this helper.
    ``None`` follows production env (``HEDRON_ENV`` plus optional host env vars such
    as ``FLASK_ENV`` / ``ENV``), then trusted forwarded HTTPS, then the request's
    own secure flag.
    """
    if force_secure is True:
        return True
    if force_secure is False:
        return False
    if is_production_env():
        return True
    for name in extra_production_env_vars:
        # Strip mirrors ``is_production_env`` so ``FLASK_ENV=production `` still
        # enables Secure cookies (#195).
        if (os.environ.get(name) or "").strip().lower() == "production":
            return True
    if forwarded_proto_https_trusted:
        return True
    return bool(request_is_secure)
