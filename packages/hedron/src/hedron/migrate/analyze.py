"""Build a StreamlitMigrationPlan from discovered sources."""

from __future__ import annotations

import ast
import time
from pathlib import Path

from hedron.migrate import SCHEMA_VERSION
from hedron.migrate.discovery import DiscoveredSource, discover_sources
from hedron.migrate.ir import (
    Confidence,
    Disposition,
    SourceSpan,
    StreamlitCall,
    StreamlitMigrationPlan,
)
from hedron.migrate.limits import AnalysisLimits, DEFAULT_LIMITS
from hedron.migrate.parse import parse_file
from hedron.migrate.registry import (
    CATALOG_VERSION,
    STREAMLIT_AUDIT_BASELINE,
    lookup,
)
from hedron.migrate.resolve import resolve_streamlit_calls


def _span_for(path: str, node: ast.AST) -> SourceSpan:
    return SourceSpan(
        path=path,
        start_line=getattr(node, "lineno", 1) or 1,
        start_column=getattr(node, "col_offset", 0) + 1,
        end_line=getattr(node, "end_lineno", None),
        end_column=(getattr(node, "end_col_offset", None) or 0) + 1
        if getattr(node, "end_col_offset", None) is not None
        else None,
    )


def _literal_title(calls: list[StreamlitCall]) -> str | None:
    for call in calls:
        if call.symbol in {"st.title", "st.set_page_config"}:
            title = call.args_summary.get("arg0") or call.args_summary.get("page_title")
            if isinstance(title, str):
                return title
    return None


def _needed_extras(calls: list[StreamlitCall]) -> list[str]:
    extras: list[str] = []
    symbols = {c.symbol for c in calls}
    if symbols & {"st.dataframe", "st.data_editor"}:
        extras.append("data")
    if symbols & {
        "st.line_chart",
        "st.area_chart",
        "st.bar_chart",
        "st.scatter_chart",
        "st.pyplot",
        "st.plotly_chart",
        "st.altair_chart",
    }:
        extras.append("charts")
    return extras


def analyze_source(
    source: Path,
    *,
    project_root: Path | None = None,
    python_version: str = "3.12",
    limits: AnalysisLimits = DEFAULT_LIMITS,
) -> StreamlitMigrationPlan:
    started = time.monotonic()
    tool_errors: list[str] = []
    try:
        discovered = discover_sources(
            source, project_root=project_root, max_files=limits.max_files
        )
    except (OSError, ValueError) as exc:
        return StreamlitMigrationPlan(
            schema_version=SCHEMA_VERSION,
            mapping_catalog_version=CATALOG_VERSION,
            streamlit_audit_baseline=STREAMLIT_AUDIT_BASELINE,
            source_units=[],
            calls=[],
            tool_errors=[str(exc)],
        )

    return analyze_discovered(
        discovered,
        python_version=python_version,
        limits=limits,
        started=started,
        tool_errors=tool_errors,
    )


def analyze_discovered(
    discovered: DiscoveredSource,
    *,
    python_version: str = "3.12",
    limits: AnalysisLimits = DEFAULT_LIMITS,
    started: float | None = None,
    tool_errors: list[str] | None = None,
) -> StreamlitMigrationPlan:
    started = time.monotonic() if started is None else started
    tool_errors = list(tool_errors or [])
    units = []
    calls: list[StreamlitCall] = []
    bytes_so_far = 0
    nodes_so_far = 0
    op_counter = 0

    for path in discovered.files:
        if time.monotonic() - started > limits.max_seconds:
            tool_errors.append("analysis time limit exceeded")
            break
        is_entry = path.resolve() == discovered.entrypoint.resolve()
        is_page = "pages" in path.parts and not is_entry
        try:
            parsed = parse_file(
                path,
                project_root=discovered.project_root,
                python_version=python_version,
                is_entrypoint=is_entry,
                is_page=is_page,
                limits=limits,
                bytes_so_far=bytes_so_far,
                nodes_so_far=nodes_so_far,
            )
        except (OSError, ValueError) as exc:
            tool_errors.append(str(exc))
            continue
        bytes_so_far += len(parsed.source.encode("utf-8"))
        nodes_so_far += parsed.node_count
        units.append(parsed.unit)

        for resolved in resolve_streamlit_calls(parsed.tree):
            op_counter += 1
            rule = lookup(resolved.symbol)
            if rule is None:
                disposition = Disposition.UNSUPPORTED
                confidence = Confidence.AMBIGUOUS
                hint = None
                findings = ["HED-MIG-ST-0002"]
            else:
                disposition = rule.disposition
                confidence = rule.confidence
                hint = rule.hedron_hint
                findings = [rule.finding_code] if rule.finding_code else []
                # unsafe_allow_html is always a blocker
                if (
                    resolved.symbol == "st.markdown"
                    and resolved.args_summary.get("unsafe_allow_html") is True
                ):
                    disposition = Disposition.UNSUPPORTED
                    confidence = Confidence.EXACT
                    findings = ["HED-MIG-ST-0007"]
            calls.append(
                StreamlitCall(
                    op_id=f"op-{op_counter:04d}",
                    symbol=resolved.symbol,
                    span=_span_for(parsed.unit.relative_path, resolved.node),
                    disposition=disposition,
                    confidence=confidence,
                    args_summary=dict(resolved.args_summary),
                    assigned_to=resolved.assigned_to,
                    in_sidebar=resolved.in_sidebar,
                    findings=findings,
                    hedron_hint=hint,
                )
            )

    return StreamlitMigrationPlan(
        schema_version=SCHEMA_VERSION,
        mapping_catalog_version=CATALOG_VERSION,
        streamlit_audit_baseline=STREAMLIT_AUDIT_BASELINE,
        source_units=units,
        calls=calls,
        page_title=_literal_title(calls),
        extras=_needed_extras(calls),
        tool_errors=tool_errors,
    )
