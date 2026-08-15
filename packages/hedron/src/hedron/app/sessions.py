"""SessionMiddleware install and default-secret warnings for Hedron."""

from __future__ import annotations

import warnings
from typing import Any, Protocol

from starlette.middleware.sessions import SessionMiddleware

from hedron.security.policy import SecurityPolicy, SecurityProfile

DEFAULT_SESSION_SECRET = "hedron-dev-secret-change-me"


class _SessionHost(Protocol):
    hedron_policy: SecurityPolicy
    state: Any

    def add_middleware(self, middleware_class: type[Any], *args: Any, **kwargs: Any) -> None: ...


def configure_sessions(
    app: _SessionHost,
    *,
    session_secret: str,
    enable_sessions: bool,
    is_prod: bool,
    mount_cookie_path: str,
) -> None:
    """Install session cookies when enabled; warn or reject the development secret."""
    if enable_sessions:
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
                stacklevel=3,
            )
        app.add_middleware(
            SessionMiddleware,
            secret_key=session_secret,
            https_only=(
                app.hedron_policy.profile is SecurityProfile.STRICT
                or (is_prod and app.hedron_policy.profile is SecurityProfile.STANDARD)
            ),
            path=mount_cookie_path,
        )
    app.state.hedron_cookie_path = mount_cookie_path
