"""Immutable Workbench / Posit configuration and resolved deployment records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace

from hedron_posit._workbench.config import (
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
from hedron_posit.cookies import ConnectCookieMode, require_supported_cookie_mode
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
]


@dataclass(frozen=True, slots=True)
class ConnectConfig:
    """Connect-specific operator configuration (never auto-detects trust)."""

    cookie_mode: ConnectCookieMode = ConnectCookieMode.NATIVE
    trusted_peers: tuple[str, ...] = ("127.0.0.1", "::1")
    owned_cookie_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "cookie_mode",
            ConnectCookieMode.parse(self.cookie_mode),
        )
        peers = tuple(str(item).strip() for item in self.trusted_peers if str(item).strip())
        object.__setattr__(self, "trusted_peers", peers or ("127.0.0.1", "::1"))
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
        if not isinstance(self.workbench, WorkbenchConfig):
            raise TypeError("workbench must be a WorkbenchConfig")
        if not isinstance(self.connect, ConnectConfig):
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
