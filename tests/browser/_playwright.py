"""Reuse one Playwright driver and browser per engine for the opt-in suite.

Each ``sync_playwright()`` / ``BrowserType.launch()`` pair used to start a new
driver and Chromium/Firefox/WebKit process. That dominated local and CI runtime.
Patches install when ``HEDRON_BROWSER`` is set; ``browser.close()`` still drops
contexts so tests stay isolated.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

_pw: Any = None
_browsers: dict[str, Any] = {}
_original_sync_playwright: Any = None
_original_launch: Any = None
_patched = False


class IsolatedBrowser:
    """Shared engine process whose ``new_page`` uses a fresh context."""

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    def new_page(self, **kwargs: Any) -> Any:
        context = self._inner.new_context()
        return context.new_page(**kwargs)

    def new_context(self, **kwargs: Any) -> Any:
        return self._inner.new_context(**kwargs)

    def close(self) -> None:
        for context in list(self._inner.contexts):
            context.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def start() -> Any:
    global _pw
    if _pw is None:
        from playwright.sync_api import sync_playwright

        real = _original_sync_playwright or sync_playwright
        _pw = real().start()
    return _pw


def stop() -> None:
    global _pw
    for browser in _browsers.values():
        inner = getattr(browser, "_inner", browser)
        inner.close()
    _browsers.clear()
    if _pw is not None:
        _pw.stop()
        _pw = None


def browser_for(engine: str) -> IsolatedBrowser:
    existing = _browsers.get(engine)
    if existing is not None:
        return existing
    pw = start()
    browser_type = getattr(pw, engine)
    if _original_launch is None:
        inner = browser_type.launch(headless=True)
    else:
        inner = _original_launch(browser_type, headless=True)
    wrapped = IsolatedBrowser(inner)
    _browsers[engine] = wrapped
    return wrapped


@contextmanager
def reused_sync_playwright() -> Iterator[Any]:
    yield start()


def _patched_launch(self: Any, *args: Any, **kwargs: Any) -> IsolatedBrowser:
    del args, kwargs
    return browser_for(str(self.name))


def install_reuse_patches() -> None:
    global _original_sync_playwright, _original_launch, _patched
    if _patched:
        return
    import playwright.sync_api as api
    from playwright.sync_api import BrowserType

    _original_sync_playwright = api.sync_playwright
    _original_launch = BrowserType.launch
    api.sync_playwright = reused_sync_playwright
    BrowserType.launch = _patched_launch  # type: ignore[method-assign]
    _patched = True
    start()


def uninstall_reuse_patches() -> None:
    global _patched
    if not _patched:
        return
    import playwright.sync_api as api
    from playwright.sync_api import BrowserType

    if _original_sync_playwright is not None:
        api.sync_playwright = _original_sync_playwright
    if _original_launch is not None:
        BrowserType.launch = _original_launch  # type: ignore[method-assign]
    _patched = False
    stop()
