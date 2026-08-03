"""Optional browser testing hooks (requires hedron[browser])."""

from __future__ import annotations

from typing import Any

__all__ = ["axe_scan", "playwright_page"]


def playwright_page(*args: Any, **kwargs: Any) -> Any:
    try:
        import importlib

        sync_api = importlib.import_module("playwright.sync_api")
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install browser extras: pip install 'hedron[browser]'") from exc
    return sync_api.sync_playwright()


def axe_scan(page: Any) -> list[dict[str, Any]]:
    """Run an axe-core scan when playwright + axe are available.

    Returns an empty list when axe is not installed; callers should treat results
    as advisory rather than full accessibility proof.
    """
    try:
        import importlib

        axe_mod = importlib.import_module("axe_playwright_python.sync_playwright")
        axe_cls = axe_mod.Axe
    except ImportError:
        return []
    axe = axe_cls()
    results = axe.run(page)
    violations = results.response.get("violations", []) if hasattr(results, "response") else []
    return list(violations)
