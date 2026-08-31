"""Proactive HedronPosit diagnostics (never log cookie values)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from hedron_posit.cookies import resolve_cookie_path


@dataclass(frozen=True, slots=True)
class PositDiagnostic:
    code: str
    title: str
    explanation: str
    remediation: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "title": self.title,
            "explanation": self.explanation,
            "remediation": self.remediation,
        }


def scan_set_cookie_headers(headers: Sequence[str], *, mount: str) -> list[PositDiagnostic]:
    """Scan Set-Cookie headers for Path=auto and path mismatches (values redacted)."""
    expected = resolve_cookie_path(mount)
    found: list[PositDiagnostic] = []
    for header in headers:
        lower = header.lower()
        if "path=auto" in lower.replace(" ", ""):
            found.append(
                PositDiagnostic(
                    code="HED-POSIT-0512",
                    title="Literal cookie Path=auto",
                    explanation=(
                        "A Set-Cookie header uses Path=auto, which browsers treat literally."
                    ),
                    remediation=(
                        "Use HedronPosit.cookies.set/delete so Path matches the deployment mount."
                    ),
                )
            )
            continue
        path_value = None
        for part in header.split(";"):
            piece = part.strip()
            if piece.lower().startswith("path="):
                path_value = piece.split("=", 1)[1].strip()
                break
        if path_value is not None and path_value != expected:
            found.append(
                PositDiagnostic(
                    code="HED-POSIT-0513",
                    title="Cookie Path does not match deployment mount",
                    explanation=(
                        f"Observed Path={path_value!r}; expected {expected!r} for this mount."
                    ),
                    remediation=(
                        "Register cookies with HedronPosit and set/delete through the registry."
                    ),
                )
            )
        elif path_value is None:
            found.append(
                PositDiagnostic(
                    code="HED-POSIT-0513",
                    title="Cookie Path is missing",
                    explanation=(
                        "A cookie emitted without Path is scoped by the browser to the "
                        "current directory rather than the deployment mount."
                    ),
                    remediation="Set an explicit Path through HedronPosit cookie APIs.",
                )
            )
    return found


def scan_location_header(location: str | None, *, mount: str) -> list[PositDiagnostic]:
    """Flag unmounted local Location values during mounted requests."""
    if not location or not mount or mount in {"", "/"}:
        return []
    if (
        location.startswith("/")
        and not location.startswith("//")
        and location != mount
        and not location.startswith(mount + "/")
    ):
        return [
            PositDiagnostic(
                code="HED-POSIT-0514",
                title="Unmounted local Location header",
                explanation="A local redirect Location is missing the deployment mount prefix.",
                remediation="Use HedronPosit.redirect / redirect_for or enable hands_off mode.",
            )
        ]
    if mount != "/" and location.startswith(mount + mount):
        return [
            PositDiagnostic(
                code="HED-POSIT-0515",
                title="Double-prefixed local Location",
                explanation="A Location appears to include the mount prefix twice.",
                remediation="Pass root-relative paths; let HedronPosit adapt once.",
            )
        ]
    return []


def scan_unregistered_cookies(
    names: Iterable[str],
    *,
    registered: Sequence[str],
) -> list[PositDiagnostic]:
    allowed = set(registered)
    out: list[PositDiagnostic] = []
    for name in names:
        if name not in allowed:
            out.append(
                PositDiagnostic(
                    code="HED-POSIT-0516",
                    title="Unregistered application cookie",
                    explanation=f"Cookie {name!r} is not in the HedronPosit registry.",
                    remediation="Call register_cookie(...) or ConnectConfig.owned_cookie_names.",
                )
            )
    return out


__all__ = [
    "PositDiagnostic",
    "scan_location_header",
    "scan_set_cookie_headers",
    "scan_unregistered_cookies",
]
