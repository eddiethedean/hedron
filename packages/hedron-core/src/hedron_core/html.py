"""Public ``html.*`` native element primitives."""

from __future__ import annotations

from typing import Any

from hedron_core._html_meta import (
    ALLOWED_ATTRS,
    ATTR_ALIASES,
    FORBIDDEN_ATTRS,
    FORBIDDEN_TAGS,
    KNOWN_TAGS,
    URL_ATTRS,
    VOID_TAGS,
)
from hedron_core._nodes import ElementNode, TrustedHtmlNode
from hedron_core.diagnostics import error
from hedron_core.security import SafeUrl, TrustedHtml, UrlPurpose, check_url_purpose_for_attribute


def _is_allowed_attr(name: str) -> bool:
    lower = name.lower()
    if lower.startswith("data-") or lower.startswith("aria-"):
        return True
    return lower in ALLOWED_ATTRS


def _normalize_attrs(attrs: dict[str, Any], *, tag: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in attrs.items():
        if value is None:
            continue
        if key == "data" and isinstance(value, dict):
            for dk, dv in value.items():
                out[f"data-{dk}"] = dv
            continue
        if key == "aria" and isinstance(value, dict):
            for ak, av in value.items():
                out[f"aria-{ak}"] = av
            continue
        name = ATTR_ALIASES.get(key, key)
        lower = name.lower()
        if lower.startswith("on"):
            raise error(
                "HED-SEC-0002",
                title="Inline event handler rejected",
                explanation=f"Attribute {name!r} is an inline event handler.",
                remediation="Use HTMX attributes or registered Web Components instead.",
            )
        if lower in FORBIDDEN_ATTRS or key in FORBIDDEN_ATTRS:
            raise error(
                "HED-SEC-0007",
                title="Forbidden attribute",
                explanation=f"Attribute {name!r} is not permitted under baseline policy.",
                remediation="Remove style/srcdoc and use typed theme or trusted assets later.",
            )
        if not _is_allowed_attr(lower):
            raise error(
                "HED-HTML-0005",
                title="Unknown HTML attribute",
                explanation=f"Attribute {name!r} is not in the allowlist.",
                remediation="Use documented attributes, data={...}, or aria={...}.",
            )
        if lower in URL_ATTRS or lower.endswith("href") or lower.endswith("src"):
            if isinstance(value, SafeUrl):
                check_url_purpose_for_attribute(value, lower)
                out[lower] = value
            elif isinstance(value, str):
                purpose = (
                    UrlPurpose.FORM_ACTION
                    if lower in {"action", "formaction"}
                    else UrlPurpose.ASSET
                    if lower in {"src", "poster"} or lower.endswith("src")
                    else UrlPurpose.NAVIGATION
                )
                raise error(
                    "HED-SEC-0003",
                    title="URL attribute requires SafeUrl",
                    explanation=(
                        f"Attribute {lower!r} must be a SafeUrl (purpose={purpose.value})."
                    ),
                    remediation="Pass SafeUrl.parse(...).",
                )
            else:
                raise error(
                    "HED-SEC-0003",
                    title="URL attribute requires SafeUrl",
                    explanation=f"Attribute {lower!r} has unsupported type {type(value)!r}.",
                    remediation="Pass a SafeUrl instance.",
                )
        else:
            out[lower] = value

    # meta refresh with URL-bearing content
    if tag == "meta":
        http_equiv = str(out.get("http-equiv", "")).lower()
        content = out.get("content")
        if http_equiv == "refresh" and isinstance(content, str) and "url=" in content.lower():
            raise error(
                "HED-SEC-0008",
                title="meta refresh URL rejected",
                explanation="http-equiv=refresh with a URL is not allowed in baseline policy.",
                remediation="Use application navigation or SafeUrl-backed links instead.",
            )
    return out


class _HtmlTag:
    __slots__ = ("_tag",)

    def __init__(self, tag: str) -> None:
        self._tag = tag

    def __call__(self, *children: Any, **attrs: Any) -> _NativeElement:
        return _NativeElement(self._tag, children, attrs)


class _NativeElement:
    """Public native HTML node implementing ComponentNode."""

    __slots__ = ("tag", "children", "attributes")

    def __init__(self, tag: str, children: tuple[Any, ...], attrs: dict[str, Any]) -> None:
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
        if tag_l not in KNOWN_TAGS:
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
        self.attributes = _normalize_attrs(attrs, tag=tag_l)

    def __hedron_node__(self) -> _NativeElement:
        return self

    def to_element_node(self, child_nodes: tuple[Any, ...]) -> ElementNode:
        return ElementNode(
            tag=self.tag,
            attributes=self.attributes,
            children=child_nodes,
            void=self.tag in VOID_TAGS,
        )


class _HtmlNamespace:
    def __getattr__(self, name: str) -> _HtmlTag:
        if name.startswith("_"):
            raise AttributeError(name)
        return _HtmlTag(name)

    def raw(self, value: TrustedHtml) -> _TrustedRaw:
        if not isinstance(value, TrustedHtml):
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


html = _HtmlNamespace()
