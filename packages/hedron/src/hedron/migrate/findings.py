"""Diagnostic builders for HED-MIG-ST-* findings."""

from __future__ import annotations

from hedron.migrate.ir import Disposition, StreamlitCall, StreamlitMigrationPlan
from hedron_core.codes import (
    HED_MIG_ST_0001,
    HED_MIG_ST_0002,
    HED_MIG_ST_0003,
    HED_MIG_ST_0004,
    HED_MIG_ST_0005,
    HED_MIG_ST_0006,
    HED_MIG_ST_0007,
    HED_MIG_ST_0008,
    HED_MIG_ST_0009,
    HED_MIG_ST_0010,
    HED_MIG_ST_0011,
    HED_MIG_ST_0012,
    HED_MIG_ST_0013,
    HED_MIG_ST_0014,
)
from hedron_core.diagnostics import (
    Diagnostic,
    DiagnosticSeverity,
    make_diagnostic,
)
from hedron_core.diagnostics import (
    SourceSpan as DiagSpan,
)

_CODE_META: dict[str, tuple[DiagnosticSeverity, str, str]] = {
    HED_MIG_ST_0001: (
        DiagnosticSeverity.ERROR,
        "Unresolved Streamlit symbol",
        "The call site could not be proven to refer to a Streamlit API.",
    ),
    HED_MIG_ST_0002: (
        DiagnosticSeverity.ERROR,
        "Unsupported or unknown Streamlit API",
        "The mapping catalog has no Supported rule for this API at the audited 1.60.x baseline.",
    ),
    HED_MIG_ST_0003: (
        DiagnosticSeverity.WARNING,
        "Ambiguous widget-state owner",
        (
            "Classify session/query/form/database ownership explicitly; "
            "do not copy session_state wholesale."
        ),
    ),
    HED_MIG_ST_0004: (
        DiagnosticSeverity.ERROR,
        "Callback or rerun control flow",
        "Hedron has no Streamlit rerun loop; redesign with explicit routes or actions.",
    ),
    HED_MIG_ST_0005: (
        DiagnosticSeverity.WARNING,
        "Side-effect boundary",
        "Mutations must move to POST actions with CSRF and authorization.",
    ),
    HED_MIG_ST_0006: (
        DiagnosticSeverity.WARNING,
        "Cache or resource lifecycle review",
        "Re-evaluate TTL, scope, keys, and invalidation under Hedron cache_data / lifespan DI.",
    ),
    HED_MIG_ST_0007: (
        DiagnosticSeverity.ERROR,
        "Trust, file, or secret boundary",
        (
            "Raw HTML, uploads, downloads, and secrets require explicit trust "
            "and authorization decisions."
        ),
    ),
    HED_MIG_ST_0008: (
        DiagnosticSeverity.ERROR,
        "Authentication boundary",
        "Hedron is not an identity provider; wire OIDC/session helpers and app-owned authz.",
    ),
    HED_MIG_ST_0009: (
        DiagnosticSeverity.WARNING,
        "Accessibility review required",
        "Provide labels, reading order, and textual/table alternatives for charts and custom UI.",
    ),
    HED_MIG_ST_0010: (
        DiagnosticSeverity.WARNING,
        "Dependency or hosting non-parity",
        "Community Cloud and some Streamlit services have no Hedron equivalent.",
    ),
    HED_MIG_ST_0011: (
        DiagnosticSeverity.ERROR,
        "Analysis failure",
        "Discovery, parse, or analysis limits prevented a complete migration plan.",
    ),
    HED_MIG_ST_0012: (
        DiagnosticSeverity.ERROR,
        "Output write refused",
        "The destination is missing, non-empty, or could not be written atomically.",
    ),
    HED_MIG_ST_0013: (
        DiagnosticSeverity.WARNING,
        "Scaffolded mapping requires review",
        "Safe Hedron structure was generated, but application logic still needs review.",
    ),
    HED_MIG_ST_0014: (
        DiagnosticSeverity.WARNING,
        "Report-only construct",
        "No output code was generated for this construct; redesign manually.",
    ),
}


def _diag_span(call: StreamlitCall) -> DiagSpan:
    return DiagSpan(
        path=call.span.path,
        start_line=call.span.start_line,
        start_column=call.span.start_column,
        end_line=call.span.end_line,
        end_column=call.span.end_column,
    )


def finding_for_code(
    code: str,
    *,
    explanation: str | None = None,
    remediation: str = "",
    span: DiagSpan | None = None,
    context: dict[str, object] | None = None,
) -> Diagnostic:
    severity, title, default_explanation = _CODE_META.get(
        code,
        (
            DiagnosticSeverity.WARNING,
            "Migration finding",
            "Review this Streamlit construct during migration.",
        ),
    )
    return make_diagnostic(
        code,
        severity=severity,
        title=title,
        explanation=explanation or default_explanation,
        remediation=remediation
        or "See docs/guides/streamlit-migration.md and the migration report.",
        span=span,
        context=context,
    )


def plan_to_diagnostics(plan: StreamlitMigrationPlan) -> list[Diagnostic]:
    diags: list[Diagnostic] = []
    for err in plan.tool_errors:
        diags.append(
            finding_for_code(
                HED_MIG_ST_0011,
                explanation=err,
                remediation="Fix the SOURCE path, reduce project size, or raise analysis limits.",
            )
        )
    for call in plan.calls:
        codes = list(call.findings)
        if not codes:
            if call.disposition is Disposition.SCAFFOLDED:
                codes = [HED_MIG_ST_0013]
            elif call.disposition is Disposition.REPORT_ONLY:
                codes = [HED_MIG_ST_0014]
            elif call.disposition is Disposition.UNSUPPORTED:
                codes = [HED_MIG_ST_0002]
            else:
                continue
        for code in codes:
            diags.append(
                finding_for_code(
                    code,
                    explanation=(
                        f"{call.symbol} → {call.disposition.value}"
                        + (f" ({call.hedron_hint})" if call.hedron_hint else "")
                    ),
                    span=_diag_span(call),
                    context={
                        "op_id": call.op_id,
                        "symbol": call.symbol,
                        "disposition": call.disposition.value,
                        "confidence": call.confidence.value,
                    },
                )
            )
    return diags
