from __future__ import annotations

from typing import Any

from edron.diagnostics import EdronDiagnostic, SourceLocation

_CODE_MAP = {
    "EDRON_APP_TITLE": "EDR-APP-0001",
    "EDRON_APP_SEALED": "EDR-APP-0002",
    "EDRON_PAGE_PATH": "EDR-PAGE-0003",
    "EDRON_PAGE_TYPE": "EDR-PAGE-0001",
    "EDRON_PAGE_INIT": "EDR-PAGE-0002",
    "EDRON_RENDER_MISSING": "EDR-PAGE-0003",
    "EDRON_DUPLICATE_PATH": "EDR-APP-0003",
    "EDRON_NO_REQUEST": "EDR-PHASE-0001",
    "EDRON_WRONG_PHASE": "EDR-PHASE-0004",
    "EDRON_LATE_OUTPUT": "EDR-PHASE-0004",
    "EDRON_ACTION_CALL": "EDR-PHASE-0002",
    "EDRON_ACTION_BIND": "EDR-BIND-0002",
    "EDRON_ACTION_METHOD": "EDR-APP-0001",
    "EDRON_FRAGMENT_APP": "EDR-BIND-0005",
    "EDRON_FRAGMENT_BIND": "EDR-BIND-0003",
    "EDRON_INPUT_INVALID": "EDR-BIND-0003",
    "EDRON_INPUT_BOUNDS": "EDR-BIND-0003",
    "EDRON_INPUT_OPTION": "EDR-BIND-0003",
    "EDRON_DOWNLOAD_METADATA": "EDR-LOWER-0001",
    "EDRON_DOWNLOAD_VALUE": "EDR-LOWER-0001",
}


class EdronError(Exception):
    """Base class for errors raised by the Edron facade."""

    code = "EDRON_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        source: SourceLocation | None = None,
        title: str | None = None,
        remediation: str = "",
        severity: str = "error",
        native_diagnostic: Any = None,
        **details: Any,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = _CODE_MAP.get(code or self.code, code or self.code)
        self.details = details
        self.diagnostic = EdronDiagnostic(
            code=self.code if self.code.startswith("EDR-") else "EDR-APP-0001",
            severity=severity,  # type: ignore[arg-type]
            title=title or self.__class__.__name__,
            explanation=message,
            remediation=remediation,
            source=source,
            native_diagnostic=native_diagnostic,
            context=details,
        )

    def __str__(self) -> str:
        return self.diagnostic.as_text()


class RegistrationError(EdronError):
    code = "EDRON_REGISTRATION_ERROR"


class PhaseError(EdronError):
    code = "EDRON_PHASE_ERROR"


class BindingError(EdronError):
    code = "EDRON_BINDING_ERROR"
