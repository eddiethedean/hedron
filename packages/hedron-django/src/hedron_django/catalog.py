"""Django portable catalog facts (EC-HOST-002). No FastAPI DI / TypeSchema production."""

from __future__ import annotations

from hedron_core.catalog import compile_interaction_catalog
from hedron_core.codes import HED_PROJECTION_0005
from hedron_core.diagnostics import error
from hedron_core.typing_aliases import JsonObject
from hedron_django.type_authoring import refuse_fastapi_type_authoring

PORTABLE_FACT_KEYS = (
    "logical_id",
    "kind",
    "descriptor_version",
    "descriptor_fingerprint",
    "type_schema_version",
    "type_schema_fingerprint",
    "effect_state",
    "declared_target_ids",
    "outcome_variant_ids",
    "redacted_limitations",
)

HOST_EXCEPTIONS: JsonObject = {
    "fastapi_di": "bounded_exception",
    "type_schema_production": "bounded_exception",
    "mount_path": "live_host_authoritative",
    "external_url": "live_host_authoritative",
    "session": "live_host_authoritative",
    "csrf": "live_host_authoritative",
    "reversal": "live_host_authoritative",
}

__all__ = [
    "HOST_EXCEPTIONS",
    "PORTABLE_FACT_KEYS",
    "project_catalog_facts",
    "refuse_live_host_authority",
]


def project_catalog_facts(logical_id: str, *, app_id: str | None = None) -> JsonObject:
    catalog = compile_interaction_catalog(app_id=app_id)
    entry = catalog.require(logical_id)
    mapping = entry.as_mapping(profile="production")
    facts: JsonObject = {
        key: mapping.get(key) for key in PORTABLE_FACT_KEYS if key != "redacted_limitations"
    }
    facts["redacted_limitations"] = list(entry.limitations)
    facts["disposition"] = "projection_adapter"
    facts["host_exceptions"] = dict(HOST_EXCEPTIONS)
    return facts


def refuse_live_host_authority(*, field: str) -> None:
    if field in {"fastapi_di", "type_schema_production", "ViewParams", "FormBody"}:
        refuse_fastapi_type_authoring(feature=field)
    raise error(
        HED_PROJECTION_0005,
        title="Django host fact is not portable",
        explanation=f"{field} remains live-host-authoritative on Django.",
        remediation="Read mount/session/CSRF/reversal from the Django request, not the catalog.",
        context={"field": field, "disposition": "projection_adapter"},
    )
