"""Auto renderer registry."""

from __future__ import annotations

from hedron_core.auto.spec import AutoDecision, RendererSpec

_renderers: list[RendererSpec] = []
_last_decision: AutoDecision | None = None


def clear_renderers_for_tests() -> None:
    global _last_decision
    _renderers.clear()
    _last_decision = None
    from hedron_core.auto.factories import register_defaults

    register_defaults()


def register_renderer(spec: RendererSpec) -> None:
    # Deterministic order: priority desc, then name asc — never import order.
    _renderers[:] = sorted(
        (*[r for r in _renderers if r.name != spec.name], spec),
        key=lambda r: (-r.priority, r.name),
    )


def list_renderers() -> tuple[RendererSpec, ...]:
    """Return registered Auto renderers (priority order)."""
    return tuple(_renderers)


def get_last_auto_decision() -> AutoDecision | None:
    return _last_decision


def set_last_auto_decision(decision: AutoDecision | None) -> None:
    global _last_decision
    _last_decision = decision


def registered_renderers() -> list[RendererSpec]:
    return _renderers
