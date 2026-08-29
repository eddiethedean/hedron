"""Immutable contracts shared by the rendering pipeline.

The public rendering module remains the compatibility façade.  Keeping these
value objects separate prevents normalization and orchestration code from
depending on the façade's implementation details.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from types import MappingProxyType

from hedron_core.alpine import BrowserFeaturePlan
from hedron_core.compat import StrEnum
from hedron_core.diagnostics import Diagnostic
from hedron_core.typing_aliases import RenderTrace


class RenderMode(StrEnum):
    PAGE = "page"
    FRAGMENT = "fragment"


@dataclass(frozen=True, slots=True)
class RenderContext:
    """Per-render locale, theme, budgets, and CSRF token provider fields."""

    locale: str = "en"
    theme: str | None = None
    max_depth: int = 100
    max_nodes: int = 50_000
    csrf_token: str | None = None
    csrf_form_field: str = "csrf_token"
    mount_path: str = ""

    @classmethod
    def standalone(
        cls,
        *,
        locale: str = "en",
        theme: str | None = None,
        csrf_token: str | None = None,
        csrf_form_field: str = "csrf_token",
        mount_path: str = "",
    ) -> RenderContext:
        return cls(
            locale=locale,
            theme=theme,
            csrf_token=csrf_token,
            csrf_form_field=csrf_form_field,
            mount_path=mount_path,
        )


@dataclass(frozen=True, slots=True)
class AssetRef:
    kind: str
    href: str
    attributes: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))


@dataclass(frozen=True, slots=True)
class RenderResult:
    html: str
    mode: RenderMode
    assets: tuple[AssetRef, ...] = ()
    headers: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    identity_map: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: tuple[Diagnostic, ...] = ()
    trace: RenderTrace | Mapping[str, object] | None = None
    htmx_plan: object | None = None
    browser_plan: BrowserFeaturePlan = field(default_factory=BrowserFeaturePlan)


_active_render_context: ContextVar[RenderContext | None] = ContextVar(
    "hedron_active_render_context", default=None
)


def active_render_context() -> RenderContext | None:
    """Return the request-local context for the in-progress render."""
    return _active_render_context.get()


def push_render_context(context: RenderContext) -> Token[RenderContext | None]:
    """Install ``context`` and return the token required to restore it."""
    return _active_render_context.set(context)


def pop_render_context(token: Token[RenderContext | None]) -> None:
    """Restore the render context represented by ``token``."""
    _active_render_context.reset(token)
