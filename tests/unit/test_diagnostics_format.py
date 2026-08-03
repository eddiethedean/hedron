"""Diagnostics JSON/SARIF and suppression tests."""

from __future__ import annotations

import pytest

from hedron_core import (
    DiagnosticSeverity,
    SourceSpan,
    Suppression,
    apply_suppressions,
    diagnostics_to_json,
    diagnostics_to_sarif,
    meets_severity_threshold,
)
from hedron_core.diagnostics import make_diagnostic


def test_diagnostic_json_and_sarif_include_span() -> None:
    diag = make_diagnostic(
        "HED-HDN-0001",
        severity=DiagnosticSeverity.ERROR,
        title="Bad template",
        explanation="Missing close tag",
        remediation="Close the element",
        span=SourceSpan(path="template.hdn", start_line=3, start_column=2),
    )
    payload = diag.as_json()
    assert payload["code"] == "HED-HDN-0001"
    assert payload["span"]["start_line"] == 3
    sarif = diagnostics_to_sarif([diag])
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"][0]["ruleId"] == "HED-HDN-0001"
    assert (
        sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["region"]["startLine"]
        == 3
    )
    assert diagnostics_to_json([diag])[0]["title"] == "Bad template"


def test_security_diagnostics_cannot_be_suppressed() -> None:
    with pytest.raises(ValueError, match="cannot be suppressed"):
        Suppression(code="HED-SEC-0001", scope="*", justification="nope")


def test_apply_suppressions_by_scope() -> None:
    diags = (
        make_diagnostic(
            "HED-CSS-0004",
            severity=DiagnosticSeverity.WARNING,
            title="Bare selector",
            explanation="html {}",
            span=SourceSpan(path="a.css", start_line=1),
        ),
        make_diagnostic(
            "HED-SEC-0002",
            severity=DiagnosticSeverity.ERROR,
            title="Unsafe",
            explanation="x",
        ),
    )
    kept = apply_suppressions(
        diags,
        (Suppression(code="HED-CSS-0004", scope="a.css", justification="legacy"),),
    )
    assert len(kept) == 1
    assert kept[0].code == "HED-SEC-0002"


def test_severity_threshold() -> None:
    warn = make_diagnostic(
        "HED-A11Y-0001",
        severity=DiagnosticSeverity.WARNING,
        title="Warn",
        explanation="x",
    )
    assert not meets_severity_threshold([warn], DiagnosticSeverity.ERROR)
    assert meets_severity_threshold([warn], DiagnosticSeverity.WARNING)
