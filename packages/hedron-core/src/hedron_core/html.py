"""Public ``html.*`` native element primitives."""

from __future__ import annotations

from typing import TypeAlias, TypeGuard, cast

from hedron_core._html.policy import (
    is_safe_layout_style,
    normalize_srcset,
    require_safe_attr_name,
)
from hedron_core._html.policy import (
    normalize_attrs as _normalize_attrs,
)
from hedron_core._html_meta import FORBIDDEN_TAGS, KNOWN_TAGS, VOID_TAGS
from hedron_core._nodes import ElementNode, Node, TrustedHtmlNode
from hedron_core.alpine import AlpineAttrs
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.interaction_067 import Interaction
from hedron_core.security import TrustedHtml
from hedron_core.typing_aliases import HtmlAttrValue

# Leaked names used by hedron-elements and tests; keep importable on html.py.
_is_safe_layout_style = is_safe_layout_style
_normalize_srcset = normalize_srcset
_require_safe_attr_name = require_safe_attr_name

__all__ = ["NativeElement", "TrustedRawNode", "html"]

HtmlTagAttrValue: TypeAlias = HtmlAttrValue | AlpineAttrs | Interaction


def _is_trusted_html(value: object) -> TypeGuard[TrustedHtml]:
    return isinstance(value, TrustedHtml)


class _HtmlTag:
    __slots__ = ("_tag",)

    def __init__(self, tag: str) -> None:
        self._tag = tag

    def __call__(self, *children: NodeLike, **attrs: HtmlTagAttrValue) -> _NativeElement:
        return _NativeElement(self._tag, children, attrs)


class _NativeElement:
    """Public native HTML node implementing ComponentNode."""

    __slots__ = ("tag", "children", "attributes", "browser_demands")

    def __init__(
        self, tag: str, children: tuple[NodeLike, ...], attrs: dict[str, HtmlTagAttrValue]
    ) -> None:
        tag_l = tag.lower()
        if tag_l in FORBIDDEN_TAGS:
            raise error(
                "HED-SEC-0009",
                title="Active HTML element rejected",
                explanation=(
                    f"<{tag_l}> is executable or active content and cannot be "
                    "constructed via html.* in phase 0.1."
                ),
                remediation="Use TrustedHtml only through approved asset/sanitizer paths later.",
            )
        # Hyphenated tags are custom elements (Web Components).
        if tag_l not in KNOWN_TAGS and "-" not in tag_l:
            raise error(
                "HED-HTML-0004",
                title="Unknown HTML tag",
                explanation=f"Tag {tag!r} is not in the known HTML element set.",
                remediation="Use a standard HTML tag or a Hedron built-in component.",
            )
        if tag_l in VOID_TAGS and children:
            raise error(
                "HED-HTML-0003",
                title="Void element cannot have children",
                explanation=f"<{tag_l}> is a void element and cannot contain children.",
            )
        self.tag = tag_l
        self.children = children
        demands: tuple[object, ...] = ()
        alpine_value = attrs.get("alpine")
        if alpine_value is not None:
            from hedron_core.alpine import AlpineAttrs

            if isinstance(alpine_value, AlpineAttrs):
                demands += alpine_value.demands()
        interaction_value = attrs.get("interaction")
        if interaction_value is not None:
            from hedron_core.interaction_067 import Interaction

            if isinstance(interaction_value, Interaction):
                demands += interaction_value.demands()
        self.browser_demands = demands
        self.attributes = _normalize_attrs(cast(dict[str, HtmlAttrValue], attrs), tag=tag_l)

    def __hedron_node__(self) -> _NativeElement:
        return self

    def with_attributes(self, attributes: dict[str, HtmlAttrValue]) -> _NativeElement:
        """Clone an already-normalized element for framework-owned merges.

        Render-time helpers sometimes need to add ARIA or identity attributes after
        construction. Re-running the public constructor would mistake normalized
        ``x-*`` attributes for raw author markup; this private clone keeps the
        original typed-policy boundary intact.
        """
        clone = object.__new__(_NativeElement)
        clone.tag = self.tag
        clone.children = self.children
        clone.attributes = attributes
        clone.browser_demands = self.browser_demands
        return clone

    def to_element_node(self, child_nodes: tuple[Node, ...]) -> ElementNode:
        return ElementNode(
            tag=self.tag,
            attributes=self.attributes,
            children=child_nodes,
            void=self.tag in VOID_TAGS,
        )


NativeElement = _NativeElement


class _HtmlNamespace:
    def __getattr__(self, name: str) -> _HtmlTag:
        if name.startswith("_"):
            raise AttributeError(name)
        return _HtmlTag(name)

    def tag(self, name: str) -> _HtmlTag:
        """Return a constructor for ``name`` (including hyphenated custom elements)."""
        return _HtmlTag(name)

    def raw(self, value: TrustedHtml) -> _TrustedRaw:
        if not _is_trusted_html(value):
            raise error(
                "HED-SEC-0004",
                title="raw() requires TrustedHtml",
                explanation="Ordinary strings cannot be passed to html.raw().",
                remediation="Use TrustedHtml.reviewed(...) at an explicit trust boundary.",
            )
        return _TrustedRaw(value)


class _TrustedRaw:
    __slots__ = ("trusted",)

    def __init__(self, trusted: TrustedHtml) -> None:
        self.trusted = trusted

    def __hedron_node__(self) -> _TrustedRaw:
        return self

    def to_node(self) -> TrustedHtmlNode:
        return TrustedHtmlNode(html=self.trusted.value, source=self.trusted.source)


TrustedRawNode = _TrustedRaw


html = _HtmlNamespace()
