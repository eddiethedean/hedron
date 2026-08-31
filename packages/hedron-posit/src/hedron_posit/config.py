"""Immutable Workbench / Posit configuration and resolved deployment records."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field, replace

from fastapi_workbench.config import (
    DEFAULT_FORWARDED_ALLOW_IPS,
    DEFAULT_HOST,
    DEFAULT_RSERVER_URL,
    DeploymentCapabilities,
    ResolvedDeployment,
    WorkbenchConfig,
    WorkbenchMode,
    WorkbenchModeName,
    WorkbenchTopology,
    WorkbenchTopologyName,
)
from hedron_core.diagnostics import DiagnosticSeverity, HedronError, make_diagnostic
from hedron_posit.cookies import ConnectCookieMode, require_supported_cookie_mode
from hedron_posit.detect import truthy
from hedron_posit.products import EvidenceKind, PositProduct, resolve_product

__all__ = [
    "DEFAULT_FORWARDED_ALLOW_IPS",
    "DEFAULT_HOST",
    "DEFAULT_RSERVER_URL",
    "ConnectConfig",
    "ConnectCookieMode",
    "DeploymentCapabilities",
    "PositConfig",
    "PositStatus",
    "ResolvedDeployment",
    "ResolvedPositDeployment",
    "WorkbenchConfig",
    "WorkbenchMode",
    "WorkbenchModeName",
    "WorkbenchTopology",
    "WorkbenchTopologyName",
    "resolve_posit_deployment",
    "resolve_posit_config",
]


@dataclass(frozen=True, slots=True)
class ConnectConfig:
    """Connect-specific operator configuration (never auto-detects trust)."""

    cookie_mode: ConnectCookieMode = ConnectCookieMode.NATIVE
    trusted_peers: tuple[str, ...] = ()
    owned_cookie_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "cookie_mode",
            ConnectCookieMode.parse(self.cookie_mode),
        )
        peers = tuple(str(item).strip() for item in self.trusted_peers if str(item).strip())
        object.__setattr__(self, "trusted_peers", peers)
        names = tuple(
            sorted({str(item).strip() for item in self.owned_cookie_names if str(item).strip()})
        )
        object.__setattr__(self, "owned_cookie_names", names)


@dataclass(frozen=True, slots=True)
class PositConfig:
    """Nested Posit product configuration for ``HedronPosit``."""

    product: PositProduct = PositProduct.AUTO
    workbench: WorkbenchConfig = field(default_factory=WorkbenchConfig)
    connect: ConnectConfig = field(default_factory=ConnectConfig)
    hands_off: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "product", PositProduct.parse(self.product))
        if not isinstance(self.workbench, WorkbenchConfig):  # pyright: ignore[reportUnnecessaryIsInstance]  # runtime boundary validation
            raise TypeError("workbench must be a WorkbenchConfig")
        if not isinstance(self.connect, ConnectConfig):  # pyright: ignore[reportUnnecessaryIsInstance]  # runtime boundary validation
            raise TypeError("connect must be a ConnectConfig")
        object.__setattr__(self, "hands_off", bool(self.hands_off))


@dataclass(frozen=True, slots=True)
class ResolvedPositDeployment:
    """Secret-free resolved Posit product + nested Workbench resolution."""

    product: PositProduct
    evidence: EvidenceKind
    workbench: ResolvedDeployment
    cookie_mode: ConnectCookieMode
    bridge_enabled: bool = False
    compatibility_facade: bool = False

    @property
    def active_connect(self) -> bool:
        return self.product is PositProduct.CONNECT

    @property
    def active_workbench(self) -> bool:
        return self.product is PositProduct.WORKBENCH and self.workbench.active

    def as_dict(self) -> dict[str, object]:
        return {
            "product": self.product.value,
            "evidence": self.evidence,
            "cookie_mode": self.cookie_mode.value,
            "bridge_enabled": self.bridge_enabled,
            "compatibility_facade": self.compatibility_facade,
            "workbench": self.workbench.as_dict(),
        }


@dataclass(frozen=True, slots=True)
class PositStatus:
    """Typed diagnostic record returned by ``posit_status()``."""

    product: PositProduct
    evidence: EvidenceKind
    mount_source: str
    browser_mount: str
    cookie_strategy: str
    bridge_enabled: bool
    registered_cookie_count: int
    normalizer_count: int
    compatibility_facade: bool
    capabilities: DeploymentCapabilities

    def as_dict(self) -> dict[str, object]:
        return {
            "product": self.product.value,
            "evidence": self.evidence,
            "mount_source": self.mount_source,
            "browser_mount": self.browser_mount,
            "cookie_strategy": self.cookie_strategy,
            "bridge_enabled": self.bridge_enabled,
            "registered_cookie_count": self.registered_cookie_count,
            "normalizer_count": self.normalizer_count,
            "compatibility_facade": self.compatibility_facade,
            "capabilities": self.capabilities.as_dict(),
        }


def resolve_posit_config(
    config: PositConfig,
    *,
    environ: Mapping[str, str] | None = None,
) -> PositConfig:
    """Apply namespaced environment defaults before deployment resolution.

    Explicit non-default object values retain precedence. The unsupported
    bridge secret always fails closed instead of being silently ignored.
    """
    env = os.environ if environ is None else environ
    connect = config.connect
    raw_cookie_mode = str(env.get("HEDRON_POSIT_CONNECT_COOKIE_MODE") or "").strip()
    if raw_cookie_mode and connect.cookie_mode is ConnectCookieMode.NATIVE:
        try:
            connect = replace(connect, cookie_mode=ConnectCookieMode.parse(raw_cookie_mode))
        except ValueError as exc:
            raise HedronError(
                make_diagnostic(
                    "HED-POSIT-0102",
                    severity=DiagnosticSeverity.ERROR,
                    title="Invalid namespaced Posit configuration",
                    explanation=str(exc),
                    remediation=(
                        "Set HEDRON_POSIT_CONNECT_COOKIE_MODE to 'native'; the bridge "
                        "extension point is not Supported."
                    ),
                )
            ) from exc
    if str(env.get("HEDRON_POSIT_BRIDGE_SECRET") or "").strip():
        require_supported_cookie_mode(ConnectCookieMode.AUTHENTICATED_HEADER_V1)
    return replace(
        config,
        connect=connect,
        hands_off=config.hands_off or truthy(env.get("HEDRON_POSIT_HANDS_OFF")),
    )


def resolve_posit_deployment(
    config: PositConfig,
    *,
    environ: Mapping[str, str] | None = None,
    discovered_raw: str | None = None,
    bound_port: int | None = None,
    compatibility_aliases: bool = False,
    compatibility_facade: bool = False,
) -> ResolvedPositDeployment:
    """Resolve product + Workbench deployment; fail closed on bridge enum."""
    config = resolve_posit_config(config, environ=environ)
    require_supported_cookie_mode(config.connect.cookie_mode)
    product, evidence = resolve_product(explicit=config.product, environ=environ)

    workbench_config = config.workbench
    if product is PositProduct.CONNECT:
        # Connect owns mounting via ASGI root_path / base header; do not activate Workbench.
        workbench_config = replace(workbench_config, mode=WorkbenchMode.OFF)

    from hedron_posit.resolve import resolve_deployment

    workbench = resolve_deployment(
        workbench_config,
        environ=environ,
        discovered_raw=discovered_raw,
        bound_port=bound_port,
        compatibility_aliases=compatibility_aliases,
    )
    return ResolvedPositDeployment(
        product=product,
        evidence=evidence,
        workbench=workbench,
        cookie_mode=config.connect.cookie_mode,
        bridge_enabled=False,
        compatibility_facade=compatibility_facade,
    )
