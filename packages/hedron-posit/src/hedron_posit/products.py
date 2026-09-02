"""Posit product enums and pure product resolution."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Literal

from hedron_core.compat import StrEnum
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_posit.detect import (
    RESOLVED_ACTIVE_ENV,
    is_workbench_env,
    is_workbench_forced,
    rs_server_url,
    truthy,
)

PositProductName = Literal["auto", "inactive", "workbench", "connect"]
EvidenceKind = Literal[
    "explicit",
    "hedron_posit_product",
    "posit_product",
    "rstudio_product_compat",
    "workbench_env",
    "workbench_handoff",
    "workbench_force",
    "none",
]


class PositProduct(StrEnum):
    AUTO = "auto"
    INACTIVE = "inactive"
    WORKBENCH = "workbench"
    CONNECT = "connect"

    @classmethod
    def parse(cls, value: str | PositProduct | None) -> PositProduct:
        raw = cls.AUTO.value if value is None else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError as exc:
            choices = ", ".join(repr(item.value) for item in cls)
            raise ValueError(f"product must be one of: {choices}") from exc


def _env_map(environ: Mapping[str, str] | None) -> Mapping[str, str]:
    return os.environ if environ is None else environ


def connect_product_marker(environ: Mapping[str, str] | None = None) -> EvidenceKind | None:
    """Return Connect runtime evidence kind, preferring ``POSIT_PRODUCT``."""
    env = _env_map(environ)
    posit = str(env.get("POSIT_PRODUCT") or "").strip().upper()
    if posit == "CONNECT":
        return "posit_product"
    if posit:
        return None
    rstudio = str(env.get("RSTUDIO_PRODUCT") or "").strip().upper()
    if rstudio == "CONNECT":
        return "rstudio_product_compat"
    return None


def workbench_product_evidence(environ: Mapping[str, str] | None = None) -> EvidenceKind | None:
    """Return Workbench evidence kind (independent of Connect markers)."""
    env = _env_map(environ)
    if is_workbench_forced(env):
        return "workbench_force"
    if truthy(str(env.get(RESOLVED_ACTIVE_ENV) or "")):
        return "workbench_handoff"
    if rs_server_url(env) or is_workbench_env(env):
        return "workbench_env"
    return None


def _conflict(title: str, explanation: str) -> HedronError:
    return HedronError(
        make_diagnostic(
            "HED-POSIT-0101",
            severity=DiagnosticSeverity.ERROR,
            title=title,
            explanation=explanation,
            remediation=(
                "Set an explicit PositConfig.product, remove conflicting Connect/Workbench "
                "environment markers, or leave product=auto with a single evidence source"
            ),
        )
    )


def resolve_product(
    *,
    explicit: PositProduct = PositProduct.AUTO,
    environ: Mapping[str, str] | None = None,
) -> tuple[PositProduct, EvidenceKind]:
    """Resolve the Posit product. Fail closed on conflicting evidence."""
    env = _env_map(environ)
    configured_from_env = False
    if explicit is PositProduct.AUTO:
        configured = str(env.get("HEDRON_POSIT_PRODUCT") or "").strip()
        if configured:
            try:
                explicit = PositProduct.parse(configured)
                configured_from_env = True
            except ValueError as exc:
                raise _conflict("Invalid Posit product configuration", str(exc)) from exc
    connect_kind = connect_product_marker(env)
    # Workbench evidence ignores Connect-only hosts; RS_SERVER_URL alongside CONNECT is conflict.
    workbench_kind = workbench_product_evidence(env)

    if explicit is not PositProduct.AUTO:
        if explicit is PositProduct.CONNECT and workbench_kind is not None:
            raise _conflict(
                "Conflicting Posit product evidence",
                "Explicit Connect conflicts with Workbench environment evidence",
            )
        if explicit is PositProduct.WORKBENCH and connect_kind is not None:
            raise _conflict(
                "Conflicting Posit product evidence",
                "Explicit Workbench conflicts with Connect runtime evidence",
            )
        if explicit is PositProduct.INACTIVE and (
            connect_kind is not None or workbench_kind is not None
        ):
            raise _conflict(
                "Conflicting Posit product evidence",
                "Explicit inactive conflicts with Connect or Workbench evidence",
            )
        return explicit, "hedron_posit_product" if configured_from_env else "explicit"

    if connect_kind is not None and workbench_kind is not None:
        raise _conflict(
            "Conflicting Posit product evidence",
            "Both Connect and Workbench evidence are present under product=auto",
        )
    if connect_kind is not None:
        return PositProduct.CONNECT, connect_kind
    if workbench_kind is not None:
        return PositProduct.WORKBENCH, workbench_kind
    return PositProduct.INACTIVE, "none"


__all__ = [
    "EvidenceKind",
    "PositProduct",
    "PositProductName",
    "connect_product_marker",
    "resolve_product",
    "workbench_product_evidence",
]
