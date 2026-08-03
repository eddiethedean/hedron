"""Stable diagnostic records for Hedron."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class DiagnosticSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Immutable diagnostic record with a stable ``HED-<AREA>-<NNNN>`` code."""

    code: str
    severity: DiagnosticSeverity
    title: str
    explanation: str
    remediation: str = ""
    owner: str | None = None
    component_id: str | None = None
    context: Mapping[str, Any] = field(default_factory=dict)
    docs_url: str | None = None

    def __post_init__(self) -> None:
        if not self.code.startswith("HED-"):
            raise ValueError(f"diagnostic code must start with HED-: {self.code!r}")

    def as_text(self) -> str:
        parts = [f"{self.code} {self.severity.value}: {self.title}", self.explanation]
        if self.remediation:
            parts.append(f"Remediation: {self.remediation}")
        if self.component_id:
            parts.append(f"Component: {self.component_id}")
        return "\n".join(parts)


class HedronError(Exception):
    """Base exception carrying one or more diagnostics."""

    def __init__(self, diagnostic: Diagnostic, *extra: Diagnostic) -> None:
        self.diagnostics: tuple[Diagnostic, ...] = (diagnostic, *extra)
        super().__init__(diagnostic.as_text())

    @property
    def diagnostic(self) -> Diagnostic:
        return self.diagnostics[0]


def make_diagnostic(
    code: str,
    *,
    severity: DiagnosticSeverity,
    title: str,
    explanation: str,
    remediation: str = "",
    owner: str | None = None,
    component_id: str | None = None,
    context: Mapping[str, Any] | None = None,
) -> Diagnostic:
    return Diagnostic(
        code=code,
        severity=severity,
        title=title,
        explanation=explanation,
        remediation=remediation,
        owner=owner,
        component_id=component_id,
        context=dict(context or {}),
    )


def error(
    code: str,
    *,
    title: str,
    explanation: str,
    remediation: str = "",
    owner: str | None = None,
    component_id: str | None = None,
    context: Mapping[str, Any] | None = None,
) -> HedronError:
    return HedronError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=remediation,
            owner=owner,
            component_id=component_id,
            context=context,
        )
    )
