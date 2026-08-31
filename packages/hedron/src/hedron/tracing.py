"""Optional distributed tracing integration (phase 0.13)."""

from __future__ import annotations

import logging
import math
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Protocol, cast

from hedron_core.csrf import redact_secret_like

__all__ = [
    "TraceConfig",
    "TracingDisabled",
    "configure_tracing",
    "get_trace_config",
    "reset_tracing_for_tests",
    "use_trace_config",
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

    def __post_init__(self) -> None:
        sample_rate = cast(object, self.sample_rate)
        if (
            isinstance(sample_rate, bool)
            or not isinstance(sample_rate, (int, float))
            or not math.isfinite(float(sample_rate))
            or not 0.0 <= sample_rate <= 1.0
        ):
            raise ValueError("sample_rate must be finite and between 0.0 and 1.0")

    @property
    def forced_sample(self) -> bool | None:
        """Return the deterministic sampling override used by tests, if configured."""
        return self._force_sample


class _OpenTelemetrySpan(Protocol):
    def set_attribute(self, key: str, value: object) -> object: ...


class _OpenTelemetrySpanContext(Protocol):
    def __enter__(self) -> _OpenTelemetrySpan: ...

    def __exit__(self, *args: object) -> object: ...


class _OpenTelemetryTracer(Protocol):
    def start_as_current_span(self, name: str) -> _OpenTelemetrySpanContext: ...


class _OpenTelemetryApi(Protocol):
    def get_tracer(self, name: str) -> _OpenTelemetryTracer: ...


class TracingDisabled:
    """No-op span context when tracing is off or exporter fails."""

    def __enter__(self) -> TracingDisabled:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def set_attribute(self, key: str, value: object) -> None:
        del key, value


class _RecordingSpan:
    def __init__(self, name: str, attributes: Mapping[str, object]) -> None:
        self.name = name
        self.attributes = redact_secret_like(dict(attributes))
        self._otel_span: _OpenTelemetrySpanContext | None = None
        self._otel_entered: _OpenTelemetrySpan | None = None

    def __enter__(self) -> _RecordingSpan:
        try:
            from opentelemetry import trace  # type: ignore[import-not-found]

            tracer = cast(_OpenTelemetryApi, trace).get_tracer("hedron")
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
            # HED-TRACE-0001 marks exporter failure for catalog honesty.
            self._otel_span = None
            self._otel_entered = None
            logger.debug(
                "HED-TRACE-0001 OpenTelemetry unavailable; continuing without spans",
                exc_info=True,
            )
        return self

    def __exit__(self, *args: object) -> None:
        if self._otel_span is not None:
            try:
                self._otel_span.__exit__(*args)
            except Exception:
                logger.debug("span end failed", exc_info=True)
        return

    def set_attribute(self, key: str, value: object) -> None:
        safe = redact_secret_like({key: value})
        self.attributes.update(safe)
        target = self._otel_entered
        if target is not None:
            try:
                for name, safe_value in safe.items():
                    target.set_attribute(name, safe_value)
            except Exception:
                logger.debug("set_attribute failed", exc_info=True)


def get_trace_config() -> TraceConfig:
    current = _config.get()
    if current is not None:
        return current
    return _global_config or TraceConfig(enabled=False)


@contextmanager
def use_trace_config(config: TraceConfig) -> Generator[None, None, None]:
    """Bind tracing configuration to the current application context."""
    token = _config.set(config)
    try:
        yield
    finally:
        _config.reset(token)


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
    if cfg.forced_sample is not None:
        return cfg.forced_sample
    if cfg.sample_rate >= 1.0:
        return True
    if cfg.sample_rate <= 0.0:
        return False
    import random

    return random.random() < cfg.sample_rate


@contextmanager
def span(
    name: str, /, **attributes: object
) -> Generator[TracingDisabled | _RecordingSpan, None, None]:
    """Open a redacted span; no-op when tracing is disabled."""
    cfg = get_trace_config()
    if not _should_sample(cfg):
        yield TracingDisabled()
        return
    with _RecordingSpan(name, attributes) as opened:
        yield opened


def start_span(name: str, /, **attributes: object) -> TracingDisabled | _RecordingSpan:
    """Non-contextmanager entry for prepare/job hooks."""
    cfg = get_trace_config()
    if not _should_sample(cfg):
        return TracingDisabled()
    return _RecordingSpan(name, attributes)
