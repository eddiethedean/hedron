"""Side-effect-free Workbench configuration resolution (Hedron specialization)."""

from __future__ import annotations

import os
from collections.abc import Mapping

from fastapi_workbench.config import ResolvedDeployment, WorkbenchConfig
from fastapi_workbench.diagnostics import WorkbenchError
from fastapi_workbench.resolve import explicit_mount_hint as _explicit_mount_hint
from fastapi_workbench.resolve import parse_rserver_url_output as _parse_rserver_url_output
from fastapi_workbench.resolve import resolve_deployment as _resolve_deployment
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic

# Hedron launcher handoff (backward compatible with 0.29).
RESOLVED_MOUNT_ENV = "HEDRON_WORKBENCH_RESOLVED_MOUNT"
RESOLVED_PUBLIC_BASE_ENV = "HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE"
RESOLVED_MODE_ENV = "HEDRON_WORKBENCH_RESOLVED_MODE"
RESOLVED_SOURCE_ENV = "HEDRON_WORKBENCH_RESOLVED_SOURCE"

_FWB_TO_HED = {
    "FWB-0001": "HED-WB-0001",
    "FWB-0002": "HED-WB-0002",
    "FWB-0003": "HED-WB-0003",
    "FWB-0004": "HED-WB-0004",
    "FWB-0005": "HED-WB-0005",
    "FWB-0006": "HED-WB-0006",
    "FWB-0007": "HED-WB-0007",
    "FWB-0008": "HED-WB-0008",
    "FWB-0009": "HED-WB-0009",
}

_HEDRON_TO_GENERIC = (
    ("HEDRON_WORKBENCH_MODE", "FASTAPI_WORKBENCH_MODE"),
    ("HEDRON_WORKBENCH_HOST", "FASTAPI_WORKBENCH_HOST"),
    ("HEDRON_WORKBENCH_PORT", "FASTAPI_WORKBENCH_PORT"),
    ("HEDRON_WORKBENCH_MOUNT", "FASTAPI_WORKBENCH_MOUNT"),
    ("HEDRON_WORKBENCH_PUBLIC_BASE_URL", "FASTAPI_WORKBENCH_PUBLIC_BASE_URL"),
    ("HEDRON_WORKBENCH_RSERVER_URL", "FASTAPI_WORKBENCH_RSERVER_URL"),
    ("HEDRON_WORKBENCH_DEBUG", "FASTAPI_WORKBENCH_DEBUG"),
    ("HEDRON_WORKBENCH_RELOAD", "FASTAPI_WORKBENCH_RELOAD"),
    ("HEDRON_WORKBENCH_WORKERS", "FASTAPI_WORKBENCH_WORKERS"),
    ("HEDRON_WORKBENCH_OPEN_BROWSER", "FASTAPI_WORKBENCH_OPEN_BROWSER"),
    ("HEDRON_WORKBENCH_FORWARDED_ALLOW_IPS", "FASTAPI_WORKBENCH_FORWARDED_ALLOW_IPS"),
    ("HEDRON_WORKBENCH_ALLOW_EXTERNAL_BIND", "FASTAPI_WORKBENCH_ALLOW_EXTERNAL_BIND"),
    ("HEDRON_WORKBENCH_TOPOLOGY", "FASTAPI_WORKBENCH_TOPOLOGY"),
    ("HEDRON_WORKBENCH_FORCE", "FASTAPI_WORKBENCH_FORCE"),
    ("HEDRON_WORKBENCH_JOB", "FASTAPI_WORKBENCH_JOB"),
    ("HEDRON_WORKBENCH_RESOLVED_MOUNT", "FASTAPI_WORKBENCH_RESOLVED_MOUNT"),
    ("HEDRON_WORKBENCH_RESOLVED_PUBLIC_BASE", "FASTAPI_WORKBENCH_RESOLVED_PUBLIC_BASE"),
    ("HEDRON_WORKBENCH_RESOLVED_MODE", "FASTAPI_WORKBENCH_RESOLVED_MODE"),
    ("HEDRON_WORKBENCH_RESOLVED_SOURCE", "FASTAPI_WORKBENCH_RESOLVED_SOURCE"),
    ("HEDRON_ROOT_PATH", "FASTAPI_WORKBENCH_ROOT_PATH"),
    ("HEDRON_TRUSTED_PROXIES", "FASTAPI_WORKBENCH_FORWARDED_ALLOW_IPS"),
)


def _merge_environ(environ: Mapping[str, str] | None) -> dict[str, str]:
    base = dict(os.environ if environ is None else environ)
    for hedron_key, generic_key in _HEDRON_TO_GENERIC:
        if hedron_key in base and generic_key not in base:
            base[generic_key] = base[hedron_key]
    return base


def _translate_error(exc: WorkbenchError) -> HedronError:
    diag = exc.diagnostic
    code = _FWB_TO_HED.get(diag.code, diag.code.replace("FWB", "HED-WB", 1))
    return HedronError(
        make_diagnostic(
            code,
            severity=DiagnosticSeverity.ERROR,
            title=diag.title,
            explanation=diag.explanation,
            remediation=diag.remediation,
        )
    )


def parse_rserver_url_output(raw: str, *, port: int) -> tuple[str, str, str]:
    try:
        return _parse_rserver_url_output(raw, port=port)
    except WorkbenchError as exc:
        raise _translate_error(exc) from exc


def explicit_mount_hint(
    config: WorkbenchConfig,
    env: Mapping[str, str] | None = None,
    *,
    compatibility_aliases: bool = True,
    warnings: list[str] | None = None,
    bound_port: int | None = None,
) -> str | None:
    """Return a non-empty mount when ``discover_rserver_url`` can be skipped.

    Applies Hedron→generic env merging, then delegates to
    the internal Workbench resolver so launcher paths skip
    discovery when ``UVICORN_ROOT_PATH`` / resolved-mount env already supply a
    mount (parity with fastapi-workbench #144 / hedron #159).
    """
    return _explicit_mount_hint(
        config,
        _merge_environ(env),
        compatibility_aliases=compatibility_aliases,
        warnings=warnings,
        bound_port=bound_port,
    )


def resolve_deployment(
    config: WorkbenchConfig | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    bound_port: int | None = None,
    discovered_raw: str | None = None,
    compatibility_aliases: bool = True,
) -> ResolvedDeployment:
    try:
        return _resolve_deployment(
            config,
            environ=_merge_environ(environ),
            bound_port=bound_port,
            discovered_raw=discovered_raw,
            compatibility_aliases=compatibility_aliases,
        )
    except WorkbenchError as exc:
        raise _translate_error(exc) from exc
