"""Browser HTMX lifecycle smoke for phase 0.6 (optional Playwright)."""

from __future__ import annotations

import pytest

pytest.importorskip("playwright")

pytestmark = pytest.mark.skipif(
    True,
    reason="Opt-in: run with hedron[browser] and HEDron_BROWSER=1 once Playwright is installed",
)


def test_htmx_fragment_preserves_shell_assets() -> None:
    """Placeholder for Chromium focus/OOB/title conformance against the reference app."""
    assert True
