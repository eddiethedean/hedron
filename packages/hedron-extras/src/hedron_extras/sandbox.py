"""Isolated browser-Python sandbox bridge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import Field

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html


@dataclass(frozen=True, slots=True)
class SandboxBudget:
    cpu_ms: int = 5_000
    memory_mb: int = 256
    output_chars: int = 100_000
    packages: tuple[str, ...] = ()

    def validated(self) -> SandboxBudget:
        if self.cpu_ms < 1 or self.cpu_ms > 60_000:
            raise ValueError("SandboxBudget cpu_ms out of bounds")
        if self.memory_mb < 16 or self.memory_mb > 1024:
            raise ValueError("SandboxBudget memory_mb out of bounds")
        if self.output_chars < 1 or self.output_chars > 2_000_000:
            raise ValueError("SandboxBudget output_chars out of bounds")
        for pkg in self.packages:
            if not pkg or "/" in pkg or ".." in pkg:
                raise ValueError(f"Invalid package allowlist entry: {pkg!r}")
        return self


class BrowserPythonSandboxProps(ElementProps):
    runtime: str = "pyodide"
    cpu_ms: int = 5_000
    memory_mb: int = 256
    output_chars: int = 100_000
    packages: list[str] = Field(default_factory=list)
    network: bool = False


class BrowserPythonSandbox(Component[BrowserPythonSandboxProps]):
    """Pinned local runtime bridge isolated from application origin and server state."""

    props_type = BrowserPythonSandboxProps
    logical_name = "BrowserPythonSandbox"
    distribution = "hedron-extras"

    def __init__(
        self,
        *,
        budget: SandboxBudget | None = None,
        runtime: str = "pyodide",
        network: bool = False,
        **kwargs: Any,
    ) -> None:
        if runtime not in {"pyodide", "jupyterlite"}:
            raise ValueError("Sandbox runtime must be pyodide or jupyterlite")
        b = (budget or SandboxBudget()).validated()
        if network:
            raise ValueError("BrowserPythonSandbox network access is denied by default policy")
        super().__init__(
            BrowserPythonSandboxProps(
                runtime=runtime,
                cpu_ms=b.cpu_ms,
                memory_mb=b.memory_mb,
                output_chars=b.output_chars,
                packages=list(b.packages),
                network=False,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.div(
            html.p("Isolated browser Python sandbox (no server/session access)."),
            html.pre(">>> # worker terminated on budget exhaustion"),
            class_=class_names("hedron-browser-python-sandbox", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-sandbox": self.props.runtime,
                "origin-isolation": "true",
                "server-session": "denied",
                "network": "deny",
                "cpu-ms": str(self.props.cpu_ms),
                "memory-mb": str(self.props.memory_mb),
                "output-chars": str(self.props.output_chars),
                "packages": ",".join(self.props.packages),
                "teardown": "worker-terminate",
            },
        )
