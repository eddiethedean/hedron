from __future__ import annotations

from typing import Any


class EdronError(Exception):
    """Base class for errors raised by the Edron facade."""

    code = "EDRON_ERROR"

    def __init__(self, message: str, *, code: str | None = None, **details: Any) -> None:
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.details = details


class RegistrationError(EdronError):
    code = "EDRON_REGISTRATION_ERROR"


class PhaseError(EdronError):
    code = "EDRON_PHASE_ERROR"


class BindingError(EdronError):
    code = "EDRON_BINDING_ERROR"
