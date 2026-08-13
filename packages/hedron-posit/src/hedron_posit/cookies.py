"""Connect cookie mode helpers and bridge extension-point fail-closed checks."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic

ConnectCookieModeName = Literal["native", "authenticated_header_v1"]


class ConnectCookieMode(StrEnum):
    """Supported native cookies; bridge enum is an extension point only in 0.33."""

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
                title="Connect cookie bridge is not Supported in 0.33",
                explanation=(
                    "ConnectCookieMode.authenticated_header_v1 is retained only as a "
                    "documented extension point. Stage 0 evidence dropped Supported bridge "
                    "scope (BRIDGE_DECISION=drop_supported)."
                ),
                remediation=(
                    "Use ConnectCookieMode.native (default). A future Accepted decision is "
                    "required before enabling authenticated_header_v1."
                ),
            )
        )


__all__ = [
    "ConnectCookieMode",
    "ConnectCookieModeName",
    "require_supported_cookie_mode",
]
