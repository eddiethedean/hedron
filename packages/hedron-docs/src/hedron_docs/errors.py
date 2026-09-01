"""Errors raised by the experimental documentation compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str
    source: str | None = None
    line: int | None = None
    column: int | None = None

    def format(self) -> str:
        location = ""
        if self.source:
            location = self.source
            if self.line is not None:
                location += f":{self.line}"
            if self.column is not None:
                location += f":{self.column}"
            location += ": "
        return f"{location}{self.code}: {self.message}"


class DocsError(ValueError):
    """A user-actionable documentation build failure."""

    def __init__(self, diagnostic: Diagnostic | str) -> None:
        self.diagnostic = (
            diagnostic
            if isinstance(diagnostic, Diagnostic)
            else Diagnostic("HED-DOCS-0001", str(diagnostic))
        )
        super().__init__(self.diagnostic.format())


def source_error(
    code: str,
    message: str,
    source: Path | str | None = None,
    *,
    line: int | None = None,
    column: int | None = None,
) -> DocsError:
    return DocsError(Diagnostic(code, message, str(source) if source else None, line, column))
