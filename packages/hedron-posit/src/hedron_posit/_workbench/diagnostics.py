"""Private Workbench diagnostic records for hedron-posit."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkbenchDiagnostic:
    code: str
    title: str
    explanation: str
    remediation: str = ""

    def as_text(self) -> str:
        parts = [f"{self.code}: {self.title}", self.explanation]
        if self.remediation:
            parts.append(f"Remediation: {self.remediation}")
        return "\n".join(parts)


class WorkbenchError(Exception):
    """Exception carrying a single Workbench diagnostic."""

    def __init__(self, diagnostic: WorkbenchDiagnostic) -> None:
        self.diagnostic = diagnostic
        super().__init__(diagnostic.as_text())


def make_diagnostic(
    code: str,
    *,
    title: str,
    explanation: str,
    remediation: str = "",
) -> WorkbenchDiagnostic:
    return WorkbenchDiagnostic(
        code=code,
        title=title,
        explanation=explanation,
        remediation=remediation,
    )
