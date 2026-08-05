"""Shared harness for module-scoped browser app fixtures."""

from __future__ import annotations

import socket
import time


def reset_browser_plugin_state() -> None:
    """Clear component registry and Explorer panels, then re-register builtins."""
    from hedron_core import reset_registry_for_tests
    from hedron_core.plugins import reset_explorer_panels_for_tests

    reset_registry_for_tests()
    reset_explorer_panels_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]


def wait_for_port(port: int, *, timeout: float = 10.0) -> None:
    """Block until TCP connect succeeds or raise if uvicorn never becomes ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.05)
    raise RuntimeError("uvicorn failed to start for browser tests")
