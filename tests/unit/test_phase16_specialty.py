"""Phase 0.16 Experimental specialty extras."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_extras.specialty import DeviceBridge, Joystick, TerminalPolicy, TerminalView


def test_terminal_fail_closed_without_policy() -> None:
    html = assert_renders(TerminalView(), contains="Terminal disabled")
    assert 'data-enabled="0"' in html
    assert 'data-stability="experimental"' in html


def test_terminal_requires_full_policy() -> None:
    with pytest.raises(ValueError):
        TerminalPolicy(
            allowlist=("ls",),
            authenticated=True,
            authorized=True,
            audit=False,
        ).validated()
    with pytest.raises(ValueError):
        TerminalPolicy(
            allowlist=("ls; rm -rf /",),
            authenticated=True,
            authorized=True,
            audit=True,
        ).validated()
    for bad in ("ls > out", "echo `id`", "ping\nreboot", "cat 'x'"):
        with pytest.raises(ValueError):
            TerminalPolicy(
                allowlist=(bad,),
                authenticated=True,
                authorized=True,
                audit=True,
            ).validated()
    policy = TerminalPolicy(
        allowlist=("status", "logs"),
        authenticated=True,
        authorized=True,
        audit=True,
        output_budget=1000,
        timeout_s=10,
    )
    html = assert_renders(TerminalView(policy=policy), contains="hedron-terminal-view")
    assert 'data-allowlist="1"' in html


def test_joystick_and_device_bridge() -> None:
    assert_renders(Joystick(max_rate_hz=20), contains="hedron-joystick")
    html = assert_renders(
        DeviceBridge("serial-1", ["ping", "reset"]),
        contains="hedron-device-bridge",
    )
    assert 'data-csrf-required="host"' in html
    with pytest.raises(ValueError):
        DeviceBridge("dev", ["reboot; wipe"])
    with pytest.raises(ValueError):
        DeviceBridge("dev", ["ping\nreboot"])
    with pytest.raises(ValueError):
        DeviceBridge("dev", ["ls > /tmp/x"])
