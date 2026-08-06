"""Experimental specialty extras — TerminalView, joystick, device bridges."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html

# Fail-closed shell metacharacters for allowlisted specialty commands.
_UNSAFE_COMMAND_CHARS = frozenset(
    {
        ";",
        "|",
        "&",
        "`",
        "$",
        "\n",
        "\r",
        "\t",
        "\0",
        ">",
        "<",
        '"',
        "'",
        "\\",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "*",
        "?",
        "~",
        "!",
        "#",
    }
)


def _reject_unsafe_command(cmd: str, *, label: str = "command") -> None:
    if not cmd or not cmd.strip():
        raise ValueError(f"Unsafe {label} rejected: {cmd!r}")
    if any(ch in cmd for ch in _UNSAFE_COMMAND_CHARS):
        raise ValueError(f"Unsafe {label} rejected: {cmd!r}")
    if ".." in cmd:
        raise ValueError(f"Unsafe {label} rejected: {cmd!r}")


@dataclass(frozen=True, slots=True)
class TerminalPolicy:
    """Fail-closed terminal policy — required to enable TerminalView."""

    allowlist: tuple[str, ...]
    authenticated: bool = False
    authorized: bool = False
    audit: bool = False
    output_budget: int = 50_000
    timeout_s: int = 30

    def validated(self) -> TerminalPolicy:
        if not self.allowlist:
            raise ValueError("TerminalPolicy requires a non-empty command allowlist")
        for cmd in self.allowlist:
            _reject_unsafe_command(cmd, label="allowlist entry")
        if not (self.authenticated and self.authorized and self.audit):
            raise ValueError(
                "TerminalView fails closed without authenticated+authorized+audit policy"
            )
        if self.output_budget < 1 or self.output_budget > 1_000_000:
            raise ValueError("output_budget out of bounds")
        if self.timeout_s < 1 or self.timeout_s > 300:
            raise ValueError("timeout_s out of bounds")
        return self


class TerminalViewProps(ElementProps):
    enabled: bool = False
    allowlist: list[str] = []
    output_budget: int = 50_000
    timeout_s: int = 30


class TerminalView(Component[TerminalViewProps]):
    """Experimental PTY/console host — never implies shell access from markup alone."""

    props_type = TerminalViewProps
    logical_name = "TerminalView"
    distribution = "hedron-extras"

    def __init__(self, *, policy: TerminalPolicy | None = None, **kwargs: Any) -> None:
        if policy is None:
            # Fail closed: render disabled surface.
            super().__init__(TerminalViewProps(enabled=False, allowlist=[], **kwargs))
            return
        p = policy.validated()
        super().__init__(
            TerminalViewProps(
                enabled=True,
                allowlist=list(p.allowlist),
                output_budget=p.output_budget,
                timeout_s=p.timeout_s,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        if not self.props.enabled:
            return html.div(
                html.p("Terminal disabled (fail-closed without allowlist/authz/audit)."),
                class_=class_names("hedron-terminal-view is-disabled", self.props.class_),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-specialty": "terminal",
                    "stability": "experimental",
                    "enabled": "0",
                    "allowlist": "0",
                },
            )
        return html.div(
            html.p("Experimental terminal (command allowlist enforced server-side)."),
            html.form(
                html.input(type="text", name="command", autocomplete="off"),
                html.button("Run", type="submit"),
                method="post",
            ),
            class_=class_names("hedron-terminal-view", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-specialty": "terminal",
                "stability": "experimental",
                "enabled": "1",
                "allowlist": "1",
                "output-budget": str(self.props.output_budget),
                "timeout-s": str(self.props.timeout_s),
                "a11y": "limited",
            },
        )


class JoystickProps(ElementProps):
    name: str = "joystick"
    max_rate_hz: int = 30


class Joystick(Component[JoystickProps]):
    props_type = JoystickProps
    logical_name = "Joystick"
    distribution = "hedron-extras"

    def __init__(self, *, name: str = "joystick", max_rate_hz: int = 30, **kwargs: Any) -> None:
        if max_rate_hz < 1 or max_rate_hz > 60:
            raise ValueError("Joystick max_rate_hz out of bounds")
        super().__init__(JoystickProps(name=name, max_rate_hz=max_rate_hz, **kwargs))

    def render(self) -> NodeLike:
        return html.div(
            html.label(
                "X",
                html.input(
                    type="range",
                    name=f"{self.props.name}_x",
                    min="-100",
                    max="100",
                    value="0",
                ),
            ),
            html.label(
                "Y",
                html.input(
                    type="range",
                    name=f"{self.props.name}_y",
                    min="-100",
                    max="100",
                    value="0",
                ),
            ),
            class_=class_names("hedron-joystick", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-specialty": "joystick",
                "stability": "experimental",
                "max-rate-hz": str(self.props.max_rate_hz),
                "pointer-alternative": "range-inputs",
            },
        )


class DeviceBridgeProps(ElementProps):
    device: str
    commands: list[str]
    name: str = "device"


class DeviceBridge(Component[DeviceBridgeProps]):
    props_type = DeviceBridgeProps
    logical_name = "DeviceBridge"
    distribution = "hedron-extras"

    def __init__(
        self,
        device: str,
        commands: Sequence[str],
        *,
        name: str = "device",
        **kwargs: Any,
    ) -> None:
        if not device or ".." in device:
            raise ValueError("Invalid device id")
        cmds = list(commands)
        if not cmds:
            raise ValueError("DeviceBridge requires an explicit command allowlist")
        for cmd in cmds:
            _reject_unsafe_command(cmd, label="device command")
        super().__init__(DeviceBridgeProps(device=device, commands=cmds, name=name, **kwargs))

    def render(self) -> NodeLike:
        options = [html.option(c, value=c) for c in self.props.commands]
        return html.form(
            html.input(type="hidden", name=f"{self.props.name}__device", value=self.props.device),
            html.select(*options, name=f"{self.props.name}__command"),
            html.button("Send", type="submit"),
            class_=class_names("hedron-device-bridge", self.props.class_),
            id=self.props.id,
            method="post",
            data={
                **mark_data(self.props.mark),
                "hedron-specialty": "device-bridge",
                "stability": "experimental",
                # Host must attach CSRF tokens for mutating posts; markup alone is not protection.
                "csrf-required": "host",
            },
        )
