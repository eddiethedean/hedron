"""Optional distributed tracing integration (phase 0.13)."""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from hedron_core.csrf import redact_secret_like

__all__ = [
    "TraceConfig",
    "TracingDisabled",
    "configure_tracing",
    "get_trace_config",
    "reset_tracing_for_tests",
    "span",
    "start_span",
]

logger = logging.getLogger("hedron.trace")

_config: ContextVar[TraceConfig | None] = ContextVar("hedron_trace_config", default=None)
_global_config: TraceConfig | None = None


@dataclass(slots=True)
class TraceConfig:
    """Opt-in tracing configuration. Disabled by default."""

    enabled: bool = False
    sample_rate: float = 1.0
    service_name: str = "hedron"
    _force_sample: bool | None = field(default=None, repr=False)


class TracingDisabled:
    """No-op span context when tracing is off or exporter fails."""

    def __enter__(self) -> TracingDisabled:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def set_attribute(self, key: str, value: Any) -> None:
        del key, value


class _RecordingSpan:
    def __init__(self, name: str, attributes: Mapping[str, Any]) -> None:
        self.name = name
        self.attributes = dict(redact_secret_like(dict(attributes)) or {})
        self._otel_span: Any | None = None
        self._otel_entered: Any | None = None

    def __enter__(self) -> _RecordingSpan:
        try:
            from opentelemetry import trace  # type: ignore[import-not-found]

            tracer = trace.get_tracer("hedron")
            span_cm = tracer.start_as_current_span(self.name)
            entered = span_cm.__enter__()
            self._otel_span = span_cm
            self._otel_entered = entered
            for key, value in self.attributes.items():
                try:
                    entered.set_attribute(key, value)
                except Exception:
                    logger.debug("trace attribute failed", exc_info=True)
        except Exception:
            # Exporter / SDK absence must not change component semantics.
            self._otel_span = None
            self._otel_entered = None
            logger.debug("OpenTelemetry unavailable; continuing without spans", exc_info=True)
        return self

    def __exit__(self, *args: object) -> None:
        if self._otel_span is not None:
            try:
                self._otel_span.__exit__(*args)
            except Exception:
                logger.debug("span end failed", exc_info=True)
        return None

    def set_attribute(self, key: str, value: Any) -> None:
        safe = redact_secret_like({key: value})
        if isinstance(safe, dict):
            self.attributes.update(safe)
            target = self._otel_entered
            if target is not None:
                try:
                    for k, v in safe.items():
                        target.set_attribute(k, v)
                except Exception:
                    logger.debug("set_attribute failed", exc_info=True)


def get_trace_config() -> TraceConfig:
    current = _config.get()
    if current is not None:
        return current
    return _global_config or TraceConfig(enabled=False)


def configure_tracing(
    *,
    enabled: bool = True,
    sample_rate: float = 1.0,
    service_name: str = "hedron",
) -> TraceConfig:
    global _global_config
    cfg = TraceConfig(enabled=enabled, sample_rate=sample_rate, service_name=service_name)
    _global_config = cfg
    return cfg


def reset_tracing_for_tests() -> None:
    global _global_config
    _global_config = None
    _config.set(None)


def _should_sample(cfg: TraceConfig) -> bool:
    if not cfg.enabled:
        return False
    if cfg._force_sample is not None:
        return cfg._force_sample
    if cfg.sample_rate >= 1.0:
        return True
    if cfg.sample_rate <= 0.0:
        return False
    import random

    return random.random() < cfg.sample_rate


@contextmanager
def span(name: str, /, **attributes: Any) -> Iterator[TracingDisabled | _RecordingSpan]:
    """Open a redacted span; no-op when tracing is disabled."""
    cfg = get_trace_config()
    if not _should_sample(cfg):
        yield TracingDisabled()
        return
    with _RecordingSpan(name, attributes) as opened:
        yield opened


def start_span(name: str, /, **attributes: Any) -> TracingDisabled | _RecordingSpan:
    """Non-contextmanager entry for prepare/job hooks."""
    cfg = get_trace_config()
    if not _should_sample(cfg):
        return TracingDisabled()
    return _RecordingSpan(name, attributes)
