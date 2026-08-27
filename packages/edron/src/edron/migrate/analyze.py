"""Edron target view over the no-execution Streamlit analyzer."""

from __future__ import annotations

from pathlib import Path

from hedron.migrate.analyze import analyze_source as _analyze_source
from hedron.migrate.ir import StreamlitMigrationPlan
from hedron.migrate.limits import AnalysisLimits

SCHEMA_VERSION = "0.7.0-beta"
MAPPING_CATALOG_VERSION = "1.60.0-edron-0.7"
STREAMLIT_AUDIT_BASELINE = "1.60.x"

_HINTS = {
    "Heading": "self.heading(level=1)",
    "Text": "self.text(...)",
    "Markdown": "self.markdown(...)",
    "Metric": "self.metric(...)",
    "Select": "self.selectbox(..., name=...)",
    "MultiSelect": "self.multiselect(..., name=...)",
    "NumberInput": "self.number_input(..., name=...)",
    "Checkbox": "self.checkbox(..., name=...)",
    "Grid": "self.layout('grid')",
    "Stack": "self.layout('stack')",
    "Form": "self.form(...)  # review CSRF and POST semantics",
    "DataTable": "self.dataframe(...)",
    "Table fallback": "self.table(...)",
    "Chart alternative": "self.chart(...)  # provide accessible alternative",
    "cache_data": "@ed.cache_data(...)",
    "lifespan DI": "app.resource(...)",
}


def _edron_hint(value: str | None) -> str | None:
    if not value:
        return None
    for needle, replacement in _HINTS.items():
        if needle in value:
            return replacement
    return value.replace("Hedron", "Edron")


def analyze_source(
    source: Path,
    *,
    project_root: Path | None = None,
    python_version: str = "3.12",
    limits: AnalysisLimits | None = None,
) -> StreamlitMigrationPlan:
    plan = _analyze_source(
        source,
        project_root=project_root,
        python_version=python_version,
        **({"limits": limits} if limits is not None else {}),
    )
    plan.schema_version = SCHEMA_VERSION
    plan.mapping_catalog_version = MAPPING_CATALOG_VERSION
    plan.streamlit_audit_baseline = STREAMLIT_AUDIT_BASELINE
    for call in plan.calls:
        call.hedron_hint = _edron_hint(call.hedron_hint)
    return plan
