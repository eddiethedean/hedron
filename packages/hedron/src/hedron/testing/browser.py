"""Optional browser testing hooks (requires hedron[browser])."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

__all__ = ["axe_scan", "axe_scan_report", "playwright", "playwright_page"]


@contextmanager
def playwright(*args: Any, **kwargs: Any) -> Iterator[Any]:
    """Yield a Playwright sync API instance (requires ``hedron[browser]``)."""
    try:
        import importlib

        sync_api = importlib.import_module("playwright.sync_api")
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install browser extras: pip install 'hedron[browser]'") from exc
    with sync_api.sync_playwright(*args, **kwargs) as pw:
        yield pw


def playwright_page(*args: Any, **kwargs: Any) -> Any:
    """Deprecated alias for :func:`playwright` (returns a context manager, not a page)."""
    return playwright(*args, **kwargs)


def axe_scan(page: Any) -> list[dict[str, Any]]:
    """Run an axe-core scan (requires ``hedron[browser]`` with axe-playwright-python).

    Raises ``ImportError`` when axe is not installed. Prefer :func:`axe_scan_report`
    when callers need incomplete/provenance metadata. An empty violation list is
    **never** proof the page is accessible (TEST-019 / PROFILE-019).
    """
    report = axe_scan_report(page)
    if report.get("incomplete"):
        raise ImportError(
            report.get("message")
            or "axe_playwright_python not installed; install hedron[browser]"
        )
    return list(report.get("violations") or [])


def axe_scan_report(page: Any) -> dict[str, Any]:
    """Return axe violations plus provenance metadata for SARIF export."""
    try:
        import importlib

        axe_mod = importlib.import_module("axe_playwright_python.sync_playwright")
        axe_cls = axe_mod.Axe
    except ImportError:
        return {
            "violations": [],
            "incomplete": True,
            "engine": None,
            "message": "axe_playwright_python not installed; scan incomplete",
            "accessible": False,
        }
    axe = axe_cls()
    results = axe.run(page)
    violations = results.response.get("violations", []) if hasattr(results, "response") else []
    version = getattr(axe_mod, "__version__", "unknown")
    return {
        "violations": list(violations),
        "incomplete": False,
        "engine": f"axe_playwright_python:{version}",
        "accessible": False,
        "gate": "TEST-019",
    }
