"""DIAG-053 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from hedron_core import (
    ApplicabilityInterval,
    DiagnosticSeverity,
    RemediationAction,
    SourceSpan,
    Suppression,
    apply_suppressions,
    normalize_severity_alias,
)
from hedron_core.diagnostics import make_diagnostic


def test_diag_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["DIAG-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


@pytest.mark.parametrize(
    ("alias", "expected"),
    [
        ("error", DiagnosticSeverity.ERROR),
        ("err", DiagnosticSeverity.ERROR),
        ("warning", DiagnosticSeverity.WARNING),
        ("warn", DiagnosticSeverity.WARNING),
        ("information", DiagnosticSeverity.INFORMATION),
        ("info", DiagnosticSeverity.INFORMATION),
        ("note", DiagnosticSeverity.INFORMATION),
        (" WARN ", DiagnosticSeverity.WARNING),
    ],
)
def test_normalize_severity_alias(alias: str, expected: DiagnosticSeverity) -> None:
    assert normalize_severity_alias(alias) is expected


def test_normalize_severity_alias_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown severity"):
        normalize_severity_alias("critical")


def test_applicability_interval() -> None:
    window = ApplicabilityInterval(min_version="0.52.0", max_version="0.53.9")
    assert window.applies("0.52.0")
    assert window.applies("0.53.0")
    assert not window.applies("0.51.9")
    assert not window.applies("0.54.0")
    open_ended = ApplicabilityInterval(min_version="0.52.0")
    assert open_ended.applies("9.0.0")


def test_diagnostic_json_includes_applicability_and_actions() -> None:
    diag = make_diagnostic(
        "HED-CONFIG-0003",
        severity=DiagnosticSeverity.WARNING,
        title="Empty registry",
        explanation="No components found.",
        remediation="Pass --app.",
        applicability=ApplicabilityInterval(min_version="0.52.0", max_version="0.53.9"),
        actions=(
            RemediationAction(
                kind="pass_flag",
                target="--app",
                message="Provide an application import path.",
            ),
        ),
        span=SourceSpan(path="app.py", start_line=1),
    )
    payload = diag.as_json()
    assert payload["applicability"] == {"min_version": "0.52.0", "max_version": "0.53.9"}
    assert payload["actions"] == [
        {
            "kind": "pass_flag",
            "target": "--app",
            "message": "Provide an application import path.",
        }
    ]


def test_apply_suppressions_still_blocks_security() -> None:
    with pytest.raises(ValueError, match="cannot be suppressed"):
        Suppression(code="HED-SEC-0001", scope="*", justification="nope")
    kept = apply_suppressions(
        (
            make_diagnostic(
                "HED-SEC-0002",
                severity=DiagnosticSeverity.ERROR,
                title="Unsafe",
                explanation="x",
            ),
            make_diagnostic(
                "HED-CSS-0004",
                severity=DiagnosticSeverity.WARNING,
                title="Bare",
                explanation="y",
                span=SourceSpan(path="a.css", start_line=1),
            ),
        ),
        (Suppression(code="HED-CSS-0004", scope="*", justification="legacy"),),
    )
    assert [d.code for d in kept] == ["HED-SEC-0002"]
