"""Connect cookie mode helpers and deployment-aware cookie registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from starlette.responses import Response

from hedron.mount import cookie_path_for_mount, normalize_mount_path
from hedron_core.compat import StrEnum
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic

if TYPE_CHECKING:
    from hedron_posit.app import HedronPosit

ConnectCookieModeName = Literal["native", "authenticated_header_v1"]


class ConnectCookieMode(StrEnum):
    """Supported native cookies; bridge remains an unsupported extension point."""

    NATIVE = "native"
    AUTHENTICATED_HEADER_V1 = "authenticated_header_v1"

    @classmethod
    def parse(cls, value: str | ConnectCookieMode | None) -> ConnectCookieMode:
        raw = cls.NATIVE.value if value is None else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError as exc:
            choices = ", ".join(repr(item.value) for item in cls)
            raise ValueError(f"cookie_mode must be one of: {choices}") from exc


def require_supported_cookie_mode(mode: ConnectCookieMode) -> None:
    """Fail closed when the Experimental bridge extension point is selected."""
    if mode is ConnectCookieMode.AUTHENTICATED_HEADER_V1:
        raise HedronError(
            make_diagnostic(
                "HED-POSIT-0401",
                severity=DiagnosticSeverity.ERROR,
                title="Connect cookie bridge is not Supported",
                explanation=(
                    "ConnectCookieMode.authenticated_header_v1 is retained only as a "
                    "documented extension point. Supported bridge scope remains "
                    "dropped (BRIDGE_DECISION=drop_supported)."
                ),
                remediation=(
                    "Use ConnectCookieMode.native (default). A future Accepted decision is "
                    "required before enabling authenticated_header_v1."
                ),
            )
        )


def resolve_cookie_path(mount: str) -> str:
    """Return a real cookie Path for a deployment mount (never the literal ``auto``)."""
    text = str(mount).strip()
    if text.lower() == "auto" or text == "":
        return cookie_path_for_mount("/")
    return cookie_path_for_mount(normalize_mount_path(text))


@dataclass(frozen=True, slots=True)
class CookieSpec:
    """Registered application cookie owned by HedronPosit lifecycle APIs."""

    name: str
    httponly: bool = True
    secure: bool = True
    samesite: Literal["lax", "strict", "none"] = "lax"
    max_age: int | None = None


class CookieRegistry:
    """Deployment-aware cookie set/delete API (no literal ``Path=auto``)."""

    def __init__(self, app: HedronPosit) -> None:
        self._app = app
        self._specs: dict[str, CookieSpec] = {}
        for name in app._owned_cookie_names():  # pyright: ignore[reportPrivateUsage]  # adapter-owned lifecycle seam
            self._specs[name] = CookieSpec(name=name)

    def register(self, spec: CookieSpec) -> None:
        if not spec.name or any(ord(ch) < 32 for ch in spec.name) or "=" in spec.name:
            raise ValueError("cookie name is invalid")
        if spec.name.lower() == "auto":
            raise ValueError("cookie name cannot be 'auto'")
        self._specs[spec.name] = spec
        refresh = getattr(self._app, "_refresh_owned_cookie_middleware", None)
        if callable(refresh):
            refresh()

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._specs))

    def _path(self) -> str:
        mount = str(getattr(self._app.state, "hedron_mount_path", "") or "/")
        path = resolve_cookie_path(mount)
        if path.lower() == "auto":
            raise HedronError(
                make_diagnostic(
                    "HED-POSIT-0508",
                    severity=DiagnosticSeverity.ERROR,
                    title="Refusing literal cookie Path=auto",
                    explanation=(
                        "Starlette would emit Path=auto as a literal cookie attribute, "
                        "so browsers would not return the cookie."
                    ),
                    remediation="Use HedronPosit cookie registry APIs; never pass path='auto'.",
                )
            )
        return path

    def set(
        self,
        response: Response,
        name: str,
        value: str,
        *,
        max_age: int | None = None,
        httponly: bool | None = None,
        secure: bool | None = None,
        samesite: Literal["lax", "strict", "none"] | None = None,
    ) -> None:
        """Set an owned cookie with the deployment cookie Path."""
        if name not in self._specs:
            raise ValueError(f"cookie {name!r} is not registered with HedronPosit")
        if value and any(ord(ch) < 32 for ch in value):
            raise ValueError("cookie value contains control characters")
        spec = self._specs[name]
        if name.startswith("__Host-") and self._path() != "/":
            raise ValueError("__Host- cookies require Path=/")
        response.set_cookie(
            key=name,
            value=value,
            path=self._path(),
            max_age=spec.max_age if max_age is None else max_age,
            httponly=spec.httponly if httponly is None else httponly,
            secure=spec.secure if secure is None else secure,
            samesite=spec.samesite if samesite is None else samesite,
        )

    def delete(self, response: Response, name: str) -> None:
        """Delete an owned cookie using the same Path used at creation."""
        if name not in self._specs:
            raise ValueError(f"cookie {name!r} is not registered with HedronPosit")
        response.delete_cookie(key=name, path=self._path())


__all__ = [
    "ConnectCookieMode",
    "ConnectCookieModeName",
    "CookieRegistry",
    "CookieSpec",
    "require_supported_cookie_mode",
    "resolve_cookie_path",
]
