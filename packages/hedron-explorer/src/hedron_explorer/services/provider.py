"""ExplorerProvider orchestration: timeout, crash, payload, ordering, redaction."""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeout
from typing import Final

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
_PROVIDER_EXECUTOR: Final = ThreadPoolExecutor(
    max_workers=4,
    thread_name_prefix="hedron-explorer-provider",
)


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
    fn: Callable[[], object],
) -> dict[str, object]:
    """Run a provider callback behind a bounded latency and worker limit.

    Timed-out callbacks cannot be killed safely by Python threads, so the
    request stops waiting and the bounded shared executor lets an already
    running callback finish without creating one unbounded thread per request.
    """
    timeout_s = max(0.05, provider.timeout_ms / 1000)
    future: Future[object] | None = None
    try:
        future = _PROVIDER_EXECUTOR.submit(fn)
        result = future.result(timeout=timeout_s)
    except FuturesTimeout:
        if future is not None:
            future.cancel()
        _logger.warning("Explorer provider %s timed out", provider.panel_id)
        return {
            "panel_id": provider.panel_id,
            "ok": False,
            "isolated": True,
            "diagnostic": HED_EXPLORER_0002,
            "error": "timeout",
        }
    except Exception as exc:  # noqa: BLE001 - third-party callback isolation boundary
        _logger.warning(
            "Explorer provider %s crashed (%s)",
            provider.panel_id,
            type(exc).__name__,
        )
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
