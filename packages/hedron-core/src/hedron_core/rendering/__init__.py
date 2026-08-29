"""Framework-neutral rendering API and compatibility façade."""

from __future__ import annotations

from hedron_core._nodes import Node
from hedron_core.component import NodeLike
from hedron_core.rendering.contracts import (
    AssetRef,
    RenderContext,
    RenderMode,
    RenderResult,
    active_render_context,
)
from hedron_core.rendering.normalize import NodeNormalizer, reject_generator
from hedron_core.rendering.session import RenderSession, render, serialize_result
from hedron_core.rendering.state import RenderState

__all__ = [
    "AssetRef",
    "NodeLike",
    "RenderContext",
    "RenderMode",
    "RenderResult",
    "RenderSession",
    "active_render_context",
    "render",
]

# Kept for integrations and benchmarks that used these implementation helpers.
_RenderState = RenderState


def normalize_compat(
    value: NodeLike,
    state: _RenderState,
    *,
    depth: int,
) -> tuple[Node, ...]:
    return NodeNormalizer(state).normalize(value, depth=depth)


def reject_generator_compat(value: object) -> None:
    reject_generator(value)


def serialize_result_compat(
    value: NodeLike,
    nodes: tuple[Node, ...],
    context: RenderContext,
    mode: RenderMode,
) -> str:
    return serialize_result(value, nodes, context, mode)


_normalize = normalize_compat
_reject_generator = reject_generator_compat
_serialize_result = serialize_result_compat


def warn(state: _RenderState, code: str, title: str, explanation: str) -> None:
    state.warn(code, title, explanation)
