"""Color mode preference persistence helpers for FastAPI apps."""

from __future__ import annotations

from typing import Literal

from starlette.requests import Request
from starlette.responses import Response

from hedron.security.csrf import forwarded_proto_https_trusted
from hedron_core.app_state import request_state, state_value
from hedron_core.color_mode import ColorMode, resolve_color_mode
from hedron_core.csrf_secure import csrf_cookie_should_be_secure
from hedron_core.typing_support import dynamic_attribute, object_contains, object_get

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
        session = dynamic_attribute(request, "session")
        if object_contains(session, SESSION_KEY):
            try:
                return ColorMode(str(object_get(session, SESSION_KEY)))
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
        cookie_path = str(state_value(request_state(request), "hedron_cookie_path", "/") or "/")
    if not cookie_path:
        cookie_path = "/"
    if secure is None:
        force_secure: bool | None = None
        request_is_secure = False
        if request is not None:
            request_is_secure = bool(request.url.is_secure)
            # Match CSRF: STRICT profiles always emit Secure (#249).
            app: object | None = request.scope.get("app")
            policy = dynamic_attribute(dynamic_attribute(app, "state"), "hedron_security")
            profile = dynamic_attribute(policy, "profile")
            if (
                profile is not None
                and str(dynamic_attribute(profile, "value", profile)).lower() == "strict"
            ):
                force_secure = True
        secure = csrf_cookie_should_be_secure(
            force_secure=force_secure,
            request_is_secure=request_is_secure,
            forwarded_proto_https_trusted=(
                bool(forwarded_proto_https_trusted(request)) if request is not None else False
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
