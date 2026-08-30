"""Stable diagnostic records for Hedron."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from pathlib import PurePath
from typing import TYPE_CHECKING, cast

from packaging.version import InvalidVersion, Version

from hedron_core.compat import StrEnum

if TYPE_CHECKING:
    from hedron_core.typing_aliases import DiagnosticDict, JsonObject, JsonValue, SourceSpanDict


class DiagnosticSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFORMATION = "information"


_SEVERITY_RANK = {
    DiagnosticSeverity.INFORMATION: 0,
    DiagnosticSeverity.WARNING: 1,
    DiagnosticSeverity.ERROR: 2,
}

_SEVERITY_ALIASES: Mapping[str, DiagnosticSeverity] = {
    "error": DiagnosticSeverity.ERROR,
    "err": DiagnosticSeverity.ERROR,
    "warning": DiagnosticSeverity.WARNING,
    "warn": DiagnosticSeverity.WARNING,
    "information": DiagnosticSeverity.INFORMATION,
    "info": DiagnosticSeverity.INFORMATION,
    "note": DiagnosticSeverity.INFORMATION,
}

# Security diagnostics cannot be suppressed. Documented in diagnostics contract.
_UNSUPPRESSIBLE_PREFIXES = ("HED-SEC-",)


def _scope_matches_path(scope: str, path: str) -> bool:
    """Exact path match or PurePath prefix; bare suffixes like ``.css`` do not match."""
    if scope in {"*", "all"}:
        return True
    if path == scope:
        return True
    try:
        PurePath(path).relative_to(PurePath(scope))
        return True
    except ValueError:
        return False


@dataclass(frozen=True, slots=True)
class SourceSpan:
    """1-based source location for diagnostics."""

    path: str
    start_line: int
    start_column: int = 1
    end_line: int | None = None
    end_column: int | None = None

    def to_dict(self) -> SourceSpanDict:
        return {
            "path": self.path,
            "start_line": self.start_line,
            "start_column": self.start_column,
            "end_line": self.end_line or self.start_line,
            "end_column": self.end_column or self.start_column,
        }


@dataclass(frozen=True, slots=True)
class ApplicabilityInterval:
    """Inclusive version window where a diagnostic applies."""

    min_version: str | None = None
    max_version: str | None = None

    def applies(self, version: str) -> bool:
        try:
            current = Version(version)
        except InvalidVersion:
            return False
        if self.min_version is not None:
            try:
                if current < Version(self.min_version):
                    return False
            except InvalidVersion:
                return False
        if self.max_version is not None:
            try:
                if current > Version(self.max_version):
                    return False
            except InvalidVersion:
                return False
        return True

    def to_dict(self) -> dict[str, str | None]:
        return {"min_version": self.min_version, "max_version": self.max_version}


@dataclass(frozen=True, slots=True)
class RemediationAction:
    """Machine-actionable remediation hint (kind + optional target/message)."""

    kind: str
    target: str = ""
    message: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "target": self.target, "message": self.message}


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
    context: Mapping[str, object] = field(default_factory=dict[str, object])
    docs_url: str | None = None
    span: SourceSpan | None = None
    applicability: ApplicabilityInterval | None = None
    actions: tuple[RemediationAction, ...] = ()

    def __post_init__(self) -> None:
        if not self.code.startswith("HED-"):
            raise ValueError(f"diagnostic code must start with HED-: {self.code!r}")

    def as_text(self) -> str:
        parts = [f"{self.code} {self.severity.value}: {self.title}", self.explanation]
        if self.remediation:
            parts.append(f"Remediation: {self.remediation}")
        if self.component_id:
            parts.append(f"Component: {self.component_id}")
        if self.span is not None:
            parts.append(
                f"Source: {self.span.path}:{self.span.start_line}:{self.span.start_column}"
            )
        return "\n".join(parts)

    def as_json(self) -> DiagnosticDict:
        payload: DiagnosticDict = {
            "code": self.code,
            "severity": self.severity.value,
            "title": self.title,
            "explanation": self.explanation,
            "remediation": self.remediation,
            "owner": self.owner,
            "component_id": self.component_id,
            "context": dict(self.context),
            "docs_url": self.docs_url,
        }
        if self.span is not None:
            payload["span"] = self.span.to_dict()
        if self.applicability is not None:
            payload["applicability"] = self.applicability.to_dict()
        if self.actions:
            payload["actions"] = [action.to_dict() for action in self.actions]
        return payload


def normalize_severity_alias(value: str) -> DiagnosticSeverity:
    """Map conventional aliases (``err``/``warn``/``info``/``note``) to severity."""
    key = value.strip().lower()
    try:
        return _SEVERITY_ALIASES[key]
    except KeyError as exc:
        raise ValueError(
            f"unknown severity {value!r}; expected one of {sorted(set(_SEVERITY_ALIASES))}."
        ) from exc


class HedronError(Exception):
    """Base exception carrying one or more diagnostics."""

    def __init__(self, diagnostic: Diagnostic, *extra: Diagnostic) -> None:
        self.diagnostics: tuple[Diagnostic, ...] = (diagnostic, *extra)
        super().__init__(diagnostic.as_text())

    @property
    def diagnostic(self) -> Diagnostic:
        return self.diagnostics[0]


@dataclass(frozen=True, slots=True)
class Suppression:
    code: str
    scope: str
    justification: str

    def __post_init__(self) -> None:
        if not self.justification.strip():
            raise ValueError("suppression justification is required")
        if any(self.code.startswith(prefix) for prefix in _UNSUPPRESSIBLE_PREFIXES):
            raise ValueError(f"diagnostic {self.code!r} cannot be suppressed")


def make_diagnostic(
    code: str,
    *,
    severity: DiagnosticSeverity,
    title: str,
    explanation: str,
    remediation: str = "",
    owner: str | None = None,
    component_id: str | None = None,
    context: Mapping[str, object] | None = None,
    span: SourceSpan | None = None,
    applicability: ApplicabilityInterval | None = None,
    actions: Sequence[RemediationAction] | None = None,
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
        span=span,
        applicability=applicability,
        actions=tuple(actions or ()),
    )


def error(
    code: str,
    *,
    title: str,
    explanation: str,
    remediation: str = "",
    owner: str | None = None,
    component_id: str | None = None,
    context: Mapping[str, object] | None = None,
    span: SourceSpan | None = None,
    applicability: ApplicabilityInterval | None = None,
    actions: Sequence[RemediationAction] | None = None,
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
            span=span,
            applicability=applicability,
            actions=actions,
        )
    )


def filter_by_applicability(
    diagnostics: Sequence[Diagnostic],
    version: str,
) -> tuple[Diagnostic, ...]:
    """Keep diagnostics that lack an interval or whose interval applies to ``version``."""
    kept: list[Diagnostic] = []
    for diag in diagnostics:
        if diag.applicability is None or diag.applicability.applies(version):
            kept.append(diag)
    return tuple(kept)


def diagnostics_to_json(diagnostics: Sequence[Diagnostic]) -> list[DiagnosticDict]:
    return [d.as_json() for d in diagnostics]


def diagnostics_to_text(diagnostics: Sequence[Diagnostic]) -> str:
    return "\n\n".join(d.as_text() for d in diagnostics)


def diagnostics_to_sarif(
    diagnostics: Sequence[Diagnostic],
    *,
    tool_name: str = "hedron",
    tool_version: str | None = None,
) -> JsonObject:
    """Emit SARIF 2.1.0 for a diagnostic collection."""
    if tool_version is None:
        from hedron_core import __version__ as package_version

        tool_version = package_version
    results: list[JsonObject] = []
    rules: dict[str, JsonObject] = {}
    for diag in diagnostics:
        rules.setdefault(
            diag.code,
            {
                "id": diag.code,
                "name": diag.code,
                "shortDescription": {"text": diag.title},
                "fullDescription": {"text": diag.explanation},
                "help": {"text": diag.remediation or diag.explanation},
                "defaultConfiguration": {
                    "level": _sarif_level(diag.severity),
                },
            },
        )
        result: JsonObject = {
            "ruleId": diag.code,
            "level": _sarif_level(diag.severity),
            "message": {"text": f"{diag.title}: {diag.explanation}"},
        }
        if diag.span is not None:
            result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": diag.span.path},
                        "region": {
                            "startLine": diag.span.start_line,
                            "startColumn": diag.span.start_column,
                            "endLine": diag.span.end_line or diag.span.start_line,
                            "endColumn": diag.span.end_column or diag.span.start_column,
                        },
                    }
                }
            ]
        properties: JsonObject = {}
        if diag.applicability is not None:
            properties["applicability"] = cast("JsonValue", diag.applicability.to_dict())
        if diag.actions:
            properties["actions"] = cast(
                "JsonValue",
                [action.to_dict() for action in diag.actions],
            )
        if properties:
            result["properties"] = properties
        results.append(result)
    return cast(
        "JsonObject",
        {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": tool_name,
                            "version": tool_version,
                            "informationUri": "https://github.com/eddiethedean/hedron",
                            "rules": list(rules.values()),
                        }
                    },
                    "results": results,
                }
            ],
        },
    )


def apply_suppressions(
    diagnostics: Sequence[Diagnostic],
    suppressions: Sequence[Suppression],
) -> tuple[Diagnostic, ...]:
    """Filter suppressible diagnostics by code and optional path scope.

    Path scopes match exactly or as a PurePath prefix of the diagnostic path.
    Suffix matches such as ``scope=".css"`` are intentionally rejected.
    ``HED-SEC-*`` codes are never suppressible.
    """
    kept: list[Diagnostic] = []
    for diag in diagnostics:
        if any(diag.code.startswith(prefix) for prefix in _UNSUPPRESSIBLE_PREFIXES):
            kept.append(diag)
            continue
        suppressed = False
        for item in suppressions:
            if item.code != diag.code:
                continue
            if item.scope in {"*", "all"}:
                suppressed = True
                break
            if diag.span is not None and _scope_matches_path(item.scope, diag.span.path):
                suppressed = True
                break
            if diag.component_id and diag.component_id == item.scope:
                suppressed = True
                break
        if not suppressed:
            kept.append(diag)
    return tuple(kept)


def meets_severity_threshold(
    diagnostics: Iterable[Diagnostic],
    threshold: DiagnosticSeverity = DiagnosticSeverity.ERROR,
) -> bool:
    rank = _SEVERITY_RANK[threshold]
    return any(_SEVERITY_RANK[d.severity] >= rank for d in diagnostics)


def with_span(diagnostic: Diagnostic, span: SourceSpan) -> Diagnostic:
    return replace(diagnostic, span=span)


def _sarif_level(severity: DiagnosticSeverity) -> str:
    if severity is DiagnosticSeverity.ERROR:
        return "error"
    if severity is DiagnosticSeverity.WARNING:
        return "warning"
    return "note"
