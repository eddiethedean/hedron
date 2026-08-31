"""Immutable Workbench configuration and resolved deployment records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from fastapi_workbench._compat import StrEnum

DEFAULT_RSERVER_URL = "/usr/lib/rstudio-server/bin/rserver-url"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_FORWARDED_ALLOW_IPS = "127.0.0.1,::1"

WorkbenchModeName = Literal["auto", "on", "off"]
WorkbenchTopologyName = Literal[
    "auto",
    "local",
    "launcher-local",
    "launcher-kubernetes",
    "launcher-slurm",
    "reverse-proxy",
]


class WorkbenchMode(StrEnum):
    AUTO = "auto"
    ON = "on"
    OFF = "off"

    @classmethod
    def parse(cls, value: str | WorkbenchMode | None) -> WorkbenchMode:
        raw = cls.AUTO.value if value is None else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError as exc:
            raise ValueError("mode must be one of: 'auto', 'on', 'off'") from exc


class WorkbenchTopology(StrEnum):
    """Expected network/process topology for diagnostics and safe defaults."""

    AUTO = "auto"
    LOCAL = "local"
    LAUNCHER_LOCAL = "launcher-local"
    LAUNCHER_KUBERNETES = "launcher-kubernetes"
    LAUNCHER_SLURM = "launcher-slurm"
    REVERSE_PROXY = "reverse-proxy"

    @classmethod
    def parse(cls, value: str | WorkbenchTopology | None) -> WorkbenchTopology:
        raw = cls.AUTO.value if value is None else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError as exc:
            choices = ", ".join(repr(item.value) for item in cls)
            raise ValueError(f"topology must be one of: {choices}") from exc


@dataclass(frozen=True, slots=True)
class WorkbenchConfig:
    """Operator-facing configuration. Resolution is side-effect-free."""

    mode: WorkbenchMode = WorkbenchMode.AUTO
    host: str | None = None
    port: int | None = None
    mount: str | None = None
    public_base_url: str | None = None
    rserver_url_bin: str = DEFAULT_RSERVER_URL
    open_browser: bool = False
    forwarded_allow_ips: str | None = None
    allow_external_bind: bool = False
    reload: bool = False
    # None = unset (env may supply); explicit 1 must beat FASTAPI_WORKBENCH_WORKERS (#147).
    workers: int | None = None
    debug: bool = False
    factory: bool = False
    app_target: str | None = None
    topology: WorkbenchTopology = WorkbenchTopology.AUTO

    def __post_init__(self) -> None:
        # Configuration is a public runtime boundary: callers commonly pass
        # values from TOML/CLI/env as strings. Normalize them once so every
        # resolver can rely on enum identity rather than crashing on `.value`.
        object.__setattr__(self, "mode", WorkbenchMode.parse(self.mode))
        object.__setattr__(self, "topology", WorkbenchTopology.parse(self.topology))


@dataclass(frozen=True, slots=True)
class ResolvedDeployment:
    """Import-independent resolved launch record (redact before logging)."""

    mode: WorkbenchMode
    host: str
    port: int
    bind: str
    external_origin: str
    browser_mount: str
    cookie_mount: str
    source: str
    active: bool = False
    warnings: tuple[str, ...] = field(default_factory=tuple)
    discovered: bool = False
    rserver_url_bin: str = DEFAULT_RSERVER_URL
    forwarded_allow_ips: str = DEFAULT_FORWARDED_ALLOW_IPS
    reload: bool = False
    workers: int = 1
    open_browser: bool = False
    debug: bool = False
    factory: bool = False
    app_target: str | None = None
    topology: WorkbenchTopology = WorkbenchTopology.AUTO

    def as_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode.value,
            "host": self.host,
            "port": self.port,
            "bind": self.bind,
            "external_origin": self.external_origin,
            "browser_mount": self.browser_mount,
            "cookie_mount": self.cookie_mount,
            "source": self.source,
            "active": self.active,
            "warnings": list(self.warnings),
            "discovered": self.discovered,
            "reload": self.reload,
            "workers": self.workers,
            "open_browser": self.open_browser,
            "debug": self.debug,
            "factory": self.factory,
            "app_target": self.app_target,
            "topology": self.topology.value,
        }


@dataclass(frozen=True, slots=True)
class DeploymentCapabilities:
    """Request/deployment capabilities relevant to links and interactive behavior."""

    platform: str
    topology: WorkbenchTopology
    mounted: bool
    browser_links: bool
    durable_links: bool
    background_links: bool
    websockets: bool
    ephemeral_session: bool
    notes: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict[str, object]:
        return {
            "platform": self.platform,
            "topology": self.topology.value,
            "mounted": self.mounted,
            "browser_links": self.browser_links,
            "durable_links": self.durable_links,
            "background_links": self.background_links,
            "websockets": self.websockets,
            "ephemeral_session": self.ephemeral_session,
            "notes": list(self.notes),
        }
