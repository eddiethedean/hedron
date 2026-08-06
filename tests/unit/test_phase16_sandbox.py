"""Phase 0.16 browser-Python sandbox."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders, sandbox_budget_fixture
from hedron_extras.sandbox import BrowserPythonSandbox, SandboxBudget


def test_sandbox_isolation_contract() -> None:
    budget = SandboxBudget(cpu_ms=2000, memory_mb=128, packages=("micropip",)).validated()
    html = assert_renders(
        BrowserPythonSandbox(budget=budget),
        contains="hedron-browser-python-sandbox",
    )
    assert 'data-server-session="denied"' in html
    assert 'data-network="deny"' in html
    assert 'data-origin-isolation="true"' in html
    with pytest.raises(ValueError):
        BrowserPythonSandbox(network=True)
    with pytest.raises(ValueError):
        SandboxBudget(cpu_ms=0).validated()
    fixture = sandbox_budget_fixture(cpu_ms=1000)
    assert fixture.cpu_ms == 1000
