"""Color mode preference persistence helpers for FastAPI apps."""

from __future__ import annotations

from typing import Literal

from starlette.requests import Request
from starlette.responses import Response

from hedron_core.color_mode import ColorMode, resolve_color_mode

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
    session = getattr(request, "session", None)
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
) -> None:
    value = preference.value if isinstance(preference, ColorMode) else str(preference)
    response.set_cookie(
        COOKIE_NAME,
        value,
        max_age=max_age,
        httponly=False,
        samesite="lax",
        path="/",
    )


def resolved_theme_from_request(
    request: Request,
    *,
    system_dark: bool = False,
) -> Literal["light", "dark"]:
    return resolve_color_mode(read_color_mode_preference(request), system_dark=system_dark)
