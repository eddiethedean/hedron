"""Color mode preference persistence helpers for FastAPI apps."""

from __future__ import annotations

from typing import Literal

from starlette.requests import Request
from starlette.responses import Response

from hedron.security.csrf import _forwarded_proto_https_trusted
from hedron_core.color_mode import ColorMode, resolve_color_mode
from hedron_core.csrf_secure import csrf_cookie_should_be_secure

COOKIE_NAME = "hedron_color_mode"
SESSION_KEY = "color_mode"

__all__ = [
    "COOKIE_NAME",
    "SESSION_KEY",
    "apply_color_mode_cookie",
    "read_color_mode_preference",
    "resolved_theme_from_request",
]


def read_color_mode_preference(request: Request) -> ColorMode:
    # Starlette's Request.session asserts when SessionMiddleware is absent;
    # getattr still invokes the property, so gate on scope first (#170).
    if "session" in request.scope:
        session = request.session
        if isinstance(session, dict) and SESSION_KEY in session:
            try:
                return ColorMode(str(session[SESSION_KEY]))
            except ValueError:
                pass
    raw = request.cookies.get(COOKIE_NAME, "system")
    try:
        return ColorMode(raw)
    except ValueError:
        return ColorMode.SYSTEM


def apply_color_mode_cookie(
    response: Response,
    preference: ColorMode | str,
    *,
    max_age: int = 60 * 60 * 24 * 365,
    path: str | None = None,
    request: Request | None = None,
    secure: bool | None = None,
) -> None:
    value = preference.value if isinstance(preference, ColorMode) else str(preference)
    cookie_path = path
    if cookie_path is None and request is not None:
        cookie_path = str(getattr(request.app.state, "hedron_cookie_path", "/") or "/")
    if not cookie_path:
        cookie_path = "/"
    if secure is None:
        force_secure: bool | None = None
        request_is_secure = False
        if request is not None:
            request_is_secure = bool(request.url.is_secure)
            # Match CSRF: STRICT profiles always emit Secure (#249).
            scope = getattr(request, "scope", None)
            app = scope.get("app") if isinstance(scope, dict) else None
            policy = getattr(getattr(app, "state", None), "hedron_security", None)
            profile = getattr(policy, "profile", None)
            if profile is not None and str(getattr(profile, "value", profile)).lower() == "strict":
                force_secure = True
        secure = csrf_cookie_should_be_secure(
            force_secure=force_secure,
            request_is_secure=request_is_secure,
            forwarded_proto_https_trusted=(
                bool(_forwarded_proto_https_trusted(request)) if request is not None else False
            ),
        )
    response.set_cookie(
        COOKIE_NAME,
        value,
        max_age=max_age,
        httponly=False,
        samesite="lax",
        path=cookie_path,
        secure=bool(secure),
    )


def resolved_theme_from_request(
    request: Request,
    *,
    system_dark: bool = False,
) -> Literal["light", "dark"]:
    return resolve_color_mode(read_color_mode_preference(request), system_dark=system_dark)
