"""ExplorerProvider orchestration: timeout, crash, payload, ordering, redaction."""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from typing import Any

from hedron_core.codes import HED_EXPLORER_0002, HED_EXPLORER_0003
from hedron_core.plugins.explorer import (
    ExplorerPanelMeta,
    ExplorerProvider,
    get_explorer_panels,
    get_explorer_providers,
)

_logger = logging.getLogger("hedron.explorer")

DEFAULT_TIMEOUT_MS = 250
DEFAULT_MAX_PAYLOAD = 65_536


def providers_or_defaults() -> list[ExplorerProvider]:
    by_id = {provider.panel_id: provider for provider in get_explorer_providers()}
    out: list[ExplorerProvider] = []
    for panel in get_explorer_panels():
        existing = by_id.get(panel.panel_id)
        if existing is not None:
            out.append(existing)
            continue
        out.append(
            ExplorerProvider(
                panel_id=panel.panel_id,
                title=panel.title,
                plugin=panel.plugin,
                description=panel.description,
                path=panel.path,
                timeout_ms=DEFAULT_TIMEOUT_MS,
                max_payload_bytes=DEFAULT_MAX_PAYLOAD,
            )
        )
    for provider in by_id.values():
        if all(item.panel_id != provider.panel_id for item in out):
            out.append(provider)
    return sorted(out, key=lambda p: (p.ordering, p.panel_id))


def run_isolated(
    provider: ExplorerProvider,
    fn: Callable[[], Any],
) -> dict[str, Any]:
    """Run a provider callback with timeout/crash isolation."""
    timeout_s = max(0.05, provider.timeout_ms / 1000)
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(fn)
            result = future.result(timeout=timeout_s)
    except FuturesTimeout:
        _logger.warning("Explorer provider %s timed out", provider.panel_id)
        return {
            "panel_id": provider.panel_id,
            "ok": False,
            "isolated": True,
            "diagnostic": HED_EXPLORER_0002,
            "error": "timeout",
        }
    except Exception as exc:  # noqa: BLE001
        _logger.warning("Explorer provider %s crashed: %s", provider.panel_id, exc)
        return {
            "panel_id": provider.panel_id,
            "ok": False,
            "isolated": True,
            "diagnostic": HED_EXPLORER_0002,
            "error": "crash",
        }
    encoded = str(result)
    if len(encoded.encode("utf-8")) > provider.max_payload_bytes:
        return {
            "panel_id": provider.panel_id,
            "ok": False,
            "isolated": True,
            "diagnostic": HED_EXPLORER_0003,
            "error": "payload",
        }
    return {"panel_id": provider.panel_id, "ok": True, "result": result}


def as_panel_meta(provider: ExplorerProvider) -> ExplorerPanelMeta:
    return ExplorerPanelMeta(
        panel_id=provider.panel_id,
        title=provider.title,
        plugin=provider.plugin,
        description=provider.description,
        path=provider.path,
    )
