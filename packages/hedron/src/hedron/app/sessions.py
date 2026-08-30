"""SessionMiddleware install and default-secret warnings for Hedron."""

from __future__ import annotations

import warnings
from typing import Any, Protocol

from starlette.middleware.sessions import SessionMiddleware

from hedron.security.policy import SecurityPolicy, SecurityProfile

DEFAULT_SESSION_SECRET = "hedron-dev-secret-change-me"


class SessionHost(Protocol):
    hedron_policy: SecurityPolicy
    state: Any

    def add_middleware(self, middleware_class: type[Any], *args: Any, **kwargs: Any) -> None: ...


def configure_sessions(
    app: SessionHost,
    *,
    session_secret: str | None,
    enable_sessions: bool,
    is_prod: bool,
    mount_cookie_path: str,
    warning_stacklevel: int = 3,
) -> None:
    """Install session cookies when enabled; warn or reject the development secret."""
    if enable_sessions:
        if session_secret is None:
            raise ValueError(
                "enable_sessions=True requires a session_secret; do not pass session_secret=None."
            )
        if (
            session_secret == DEFAULT_SESSION_SECRET
            and app.hedron_policy.profile is SecurityProfile.STRICT
        ):
            raise ValueError(
                "security='strict' requires an explicit session_secret "
                "(do not use the development default)."
            )
        if session_secret == DEFAULT_SESSION_SECRET and not is_prod:
            warnings.warn(
                "Hedron is using the default development session_secret; "
                "set session_secret explicitly before production deployment.",
                UserWarning,
                stacklevel=warning_stacklevel,
            )
        app.add_middleware(
            SessionMiddleware,
            secret_key=session_secret,
            https_only=(app.hedron_policy.profile is SecurityProfile.STRICT or is_prod),
            path=mount_cookie_path,
        )
    app.state.hedron_cookie_path = mount_cookie_path
