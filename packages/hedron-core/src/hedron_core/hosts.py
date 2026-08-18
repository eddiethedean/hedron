"""Stable fragment hosts for refreshable views (phase 0.43 / RFC-0070)."""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import ClassVar

from hedron_core.codes import HED_HOST_0001, HED_VIEW_0002
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error as raise_error
from hedron_core.html import html
from hedron_core.htmx.policy import CacheHint
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrMap, HtmlAttrValue

__all__ = [
    "FRAGMENT_HOST_TAGS",
    "FragmentHost",
    "begin_host_mount_scope",
    "end_host_mount_scope",
]

FRAGMENT_HOST_TAGS = frozenset(
    {"div", "section", "article", "aside", "main", "nav", "header", "footer"}
)

_SAFE_ATTR_PREFIXES = ("data-", "aria-")
_SAFE_ATTR_NAMES = frozenset(
    {
        "class",
        "class_",
        "id",
        "role",
        "title",
        "lang",
        "hidden",
        "tabindex",
        "style",
    }
)

_mounted_ids: ContextVar[set[str] | None] = ContextVar("hedron_mounted_host_ids", default=None)


def begin_host_mount_scope() -> Token[set[str] | None]:
    """Start a render-local mounted-host identity set."""
    return _mounted_ids.set(set())


def end_host_mount_scope(token: Token[set[str] | None]) -> None:
    _mounted_ids.reset(token)


def _note_mounted(dom_id: str) -> None:
    mounted = _mounted_ids.get()
    if mounted is None:
        return
    if dom_id in mounted:
        raise raise_error(
            HED_VIEW_0002,
            title="Duplicate unbound fragment mount",
            explanation=(
                f"Host id {dom_id!r} was mounted more than once in the same page. "
                "Repeated views need bind() or an explicit instance key."
            ),
            remediation="Call handle.bind(...) with distinct parameters or an instance key.",
            component_id=dom_id,
        )
    mounted.add(dom_id)


def _validate_attrs(attrs: HtmlAttrMap) -> HtmlAttrMap:
    out: HtmlAttrMap = {}
    for raw_name, value in attrs.items():
        name = str(raw_name)
        lowered = name.lower()
        if lowered.startswith("on") or lowered.startswith("hx-on"):
            raise raise_error(
                HED_HOST_0001,
                title="Unsafe fragment host attribute",
                explanation=(
                    f"Host attribute {name!r} is not an allowlisted ordinary HTML/ARIA attribute."
                ),
                remediation="Use safe HTML/ARIA attributes; do not attach event handlers on hosts.",
            )
        if lowered in _SAFE_ATTR_NAMES or lowered.startswith(_SAFE_ATTR_PREFIXES):
            out[name] = value
            continue
        raise raise_error(
            HED_HOST_0001,
            title="Unsafe fragment host attribute",
            explanation=f"Host attribute {name!r} is not allowlisted.",
            remediation="Pass ordinary class/role/ARIA/data attributes only.",
        )
    return out


class FragmentHostProps(Props):
    tag: str = "div"
    role: str | None = None
    aria_live: str | None = None


class FragmentHost(Component[FragmentHostProps]):
    """Semantically neutral wrapper that owns identity, swap, and busy state."""

    props_type = FragmentHostProps
    logical_name: ClassVar[str | None] = "FragmentHost"
    distribution: ClassVar[str] = "hedron-core"

    def __init__(
        self,
        content: NodeLike | None = None,
        *,
        tag: str = "div",
        role: str | None = None,
        aria_live: str | None = None,
        attrs: HtmlAttrMap | None = None,
        loading: NodeLike | None = None,
        error: NodeLike | str | None = None,
        empty: NodeLike | None = None,
        cache: CacheHint | None = None,
        dom_id: str | None = None,
        get_url: str | None = None,
        event_name: str | None = None,
        logical_id: str | None = None,
        fallback: str | None = None,
        load_on_mount: bool = False,
    ) -> None:
        tag_name = tag.lower()
        if tag_name not in FRAGMENT_HOST_TAGS:
            raise raise_error(
                HED_HOST_0001,
                title="Unsafe fragment host tag",
                explanation=f"Host tag {tag!r} is not allowlisted.",
                remediation=f"Use one of: {', '.join(sorted(FRAGMENT_HOST_TAGS))}.",
            )
        super().__init__(FragmentHostProps(tag=tag_name, role=role, aria_live=aria_live))
        self._content = content
        self._attrs = _validate_attrs(dict(attrs or {}))
        self._loading = loading
        self._error = error
        self._empty = empty
        self._cache: CacheHint | None = cache
        self._dom_id = dom_id
        self._get_url = get_url
        self._event_name = event_name
        self._logical_id = logical_id
        self._fallback = fallback
        self._load_on_mount = load_on_mount

    def materialize(
        self,
        content: NodeLike,
        *,
        dom_id: str,
        get_url: str,
        event_name: str,
        logical_id: str,
        fallback: str | None = None,
        load_on_mount: bool = False,
    ) -> FragmentHost:
        return FragmentHost(
            content,
            tag=self.props.tag,
            role=self.props.role,
            aria_live=self.props.aria_live,
            attrs=dict(self._attrs),
            loading=self._loading,
            error=self._error,
            empty=self._empty,
            cache=self._cache,
            dom_id=dom_id,
            get_url=get_url,
            event_name=event_name,
            logical_id=logical_id,
            fallback=fallback if fallback is not None else self._fallback,
            load_on_mount=load_on_mount,
        )

    def render(self) -> NodeLike:
        if self._dom_id:
            _note_mounted(self._dom_id)
        inner: NodeLike = self._content
        if inner is None:
            inner = self._loading
        attrs: dict[str, HtmlAttrValue] = dict(self._attrs)
        if self._dom_id:
            attrs["id"] = self._dom_id
        if self.props.role:
            attrs["role"] = self.props.role
        aria: dict[str, str | bool | int | float | None] = {"busy": "false"}
        if self.props.aria_live:
            aria["live"] = self.props.aria_live
        attrs["aria"] = aria
        if self._logical_id:
            attrs["data-hedron-handle"] = self._logical_id
        if self._get_url:
            attrs["hx-get"] = self._get_url
            attrs["hx-target"] = "this"
            attrs["hx-swap"] = "outerHTML"
            attrs["hx-sync"] = "this:drop"
            attrs["hx-indicator"] = "this"
            trigger = f"{self._event_name} from:body" if self._event_name else None
            if self._load_on_mount:
                trigger = f"load, {trigger}" if trigger else "load"
            if trigger:
                attrs["hx-trigger"] = trigger
        if self._fallback:
            attrs["data-hedron-fallback"] = self._fallback
        if self._error is not None:
            attrs["data-hedron-error-slot"] = "true"
        tag = getattr(html, self.props.tag)
        children: list[NodeLike] = []
        if self._error is not None:
            error_node: NodeLike = (
                html.p(self._error) if isinstance(self._error, str) else self._error
            )
            children.append(
                html.template(error_node, **{"data-hedron-error-template": "true"})
            )
        if inner is not None:
            children.append(inner)
        return tag(*children, **attrs)
