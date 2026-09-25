"""Optional browser testing hooks (requires hedron[browser])."""

from __future__ import annotations

from collections.abc import Generator, Mapping
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, version
from typing import Protocol, cast

__all__ = ["axe_scan", "axe_scan_report", "playwright", "playwright_page"]


class _PlaywrightManager(Protocol):
    def __enter__(self) -> object: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> object: ...


class _PlaywrightFactory(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> _PlaywrightManager: ...


@contextmanager
def playwright(*args: object, **kwargs: object) -> Generator[object, None, None]:
    """Yield a Playwright sync API instance (requires ``hedron[browser]``)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install browser extras: pip install 'hedron[browser]'") from exc
    factory = cast(_PlaywrightFactory, sync_playwright)
    with factory(*args, **kwargs) as pw:
        yield pw


def playwright_page(*args: object, **kwargs: object) -> object:
    """Deprecated alias for :func:`playwright` (returns a context manager, not a page)."""
    return playwright(*args, **kwargs)


def axe_scan(page: object) -> list[dict[str, object]]:
    """Run an axe-core scan (requires ``hedron[browser]`` with axe-playwright-python).

    Raises ``ImportError`` when axe is not installed. Prefer :func:`axe_scan_report`
    when callers need incomplete/provenance metadata. An empty violation list is
    **never** proof the page is accessible (TEST-019 / PROFILE-019).
    """
    report = axe_scan_report(page)
    if report.get("incomplete"):
        raise ImportError(
            report.get("message") or "axe_playwright_python not installed; install hedron[browser]"
        )
    violations = report.get("violations", [])
    if not isinstance(violations, list):
        return []
    return [
        {str(key): value for key, value in cast(Mapping[object, object], item).items()}
        for item in cast(list[object], violations)
        if isinstance(item, Mapping)
    ]


def axe_scan_report(page: object) -> dict[str, object]:
    """Return axe violations plus provenance metadata for SARIF export."""
    try:
        from axe_playwright_python.sync_playwright import Axe
    except ImportError:
        return {
            "violations": [],
            "incomplete": True,
            "engine": None,
            "message": "axe_playwright_python not installed; scan incomplete",
            "accessible": False,
        }
    axe = Axe()
    results = axe.run(page)
    response_value: object = getattr(results, "response", {})
    response: Mapping[str, object] = (
        cast(Mapping[str, object], response_value) if isinstance(response_value, Mapping) else {}
    )
    violations_value = response.get("violations", [])
    violations = cast(list[object], violations_value) if isinstance(violations_value, list) else []
    try:
        package_version = version("axe-playwright-python")
    except PackageNotFoundError:
        package_version = "unknown"
    return {
        "violations": list(violations),
        "incomplete": False,
        "engine": f"axe_playwright_python:{package_version}",
        "accessible": False,
        "gate": "TEST-019",
    }
