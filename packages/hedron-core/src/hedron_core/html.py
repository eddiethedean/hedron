"""Public ``html.*`` native element primitives."""

from __future__ import annotations

import re

from hedron_core._html_meta import (
    ALLOWED_ATTRS,
    ATTR_ALIASES,
    FORBIDDEN_ATTRS,
    FORBIDDEN_TAGS,
    KNOWN_TAGS,
    URL_ATTRS,
    VOID_TAGS,
)
from hedron_core._nodes import ElementNode, Node, TrustedHtmlNode
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.htmx_eval import reject_hx_eval_value
from hedron_core.security import SafeUrl, TrustedHtml, UrlPurpose, check_url_purpose_for_attribute
from hedron_core.typing_aliases import HtmlAttrValue

# Only layout CSS custom properties — never arbitrary author CSS.
_SAFE_LAYOUT_STYLE = re.compile(r"^--hedron-gap:\s*\d+(\.\d+)?(rem|em|px|%);?$")
# Attribute names must be tokens — never whitespace, quotes, ``=``, or tag breakouts.
_SAFE_ATTR_NAME = re.compile(r"^[A-Za-z_][\w.-]*$")
_META_REFRESH_URL = re.compile(r"url\s*=", re.IGNORECASE)


def _is_safe_layout_style(value: object) -> bool:
    return isinstance(value, str) and bool(_SAFE_LAYOUT_STYLE.match(value.strip()))


def _require_safe_attr_name(name: str) -> str:
    if not name or not _SAFE_ATTR_NAME.match(name) or any(ord(ch) < 32 for ch in name):
        raise error(
            "HED-SEC-0010",
            title="Unsafe attribute name rejected",
            explanation=f"Attribute name {name!r} contains forbidden characters.",
            remediation="Use token attribute names matching [A-Za-z_][\\w.-]*.",
        )
    return name


def _is_allowed_attr(name: str) -> bool:
    lower = name.lower()
    if lower.startswith("data-") or lower.startswith("aria-"):
        return True
    return lower in ALLOWED_ATTRS


def _normalize_srcset(value: object) -> str:
    """Validate srcset candidates; each URL must be SafeUrl or a safe relative path."""
    if isinstance(value, SafeUrl):
        check_url_purpose_for_attribute(value, "srcset")
        return str(value)
    if not isinstance(value, str):
        raise error(
            "HED-SEC-0003",
            title="URL attribute requires SafeUrl",
            explanation="Attribute 'srcset' has unsupported type.",
            remediation="Pass SafeUrl.parse(...) or a validated srcset string of SafeUrl paths.",
        )
    parts: list[str] = []
    for candidate in value.split(","):
        piece = candidate.strip()
        if not piece:
            continue
        tokens = piece.split()
        url_token = tokens[0]
        rest = " ".join(tokens[1:])
        # All candidates go through SafeUrl (fail closed on dangerous schemes).
        SafeUrl.parse(url_token, purpose=UrlPurpose.ASSET)
        parts.append(f"{url_token} {rest}".strip())
    return ", ".join(parts)


def _normalize_attrs(attrs: dict[str, HtmlAttrValue], *, tag: str) -> dict[str, HtmlAttrValue]:
    out: dict[str, HtmlAttrValue] = {}
    for key, value in attrs.items():
        if value is None:
            continue
        if key == "data" and isinstance(value, dict):
            for dk, dv in value.items():
                safe_key = _require_safe_attr_name(str(dk))
                out[f"data-{safe_key}"] = dv
            continue
        if key == "aria" and isinstance(value, dict):
            for ak, av in value.items():
                safe_key = _require_safe_attr_name(str(ak))
                out[f"aria-{safe_key}"] = av
            continue
        name = ATTR_ALIASES.get(key, key)
        _require_safe_attr_name(str(name))
        lower = name.lower()
        if lower.startswith("on"):
            raise error(
                "HED-SEC-0002",
                title="Inline event handler rejected",
                explanation=f"Attribute {name!r} is an inline event handler.",
                remediation="Use HTMX attributes or registered Web Components instead.",
            )
        if lower == "style" or key == "style_":
            if _is_safe_layout_style(value):
                out["style"] = str(value).strip().rstrip(";")
                continue
            raise error(
                "HED-SEC-0007",
                title="Forbidden attribute",
                explanation=f"Attribute {name!r} is not permitted under baseline policy.",
                remediation="Only layout custom properties like '--hedron-gap: 1rem' are allowed.",
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
        reject_hx_eval_value(lower, value)
        if lower in URL_ATTRS or lower.endswith("href") or lower.endswith("src"):
            if lower == "srcset":
                out[lower] = _normalize_srcset(value)
                continue
            if lower in {"hx-push-url", "hx-replace-url"} and isinstance(value, bool):
                out[lower] = value
                continue
            if lower in {"hx-push-url", "hx-replace-url"} and isinstance(value, str):
                lowered = value.lower()
                if lowered in {"true", "false"}:
                    out[lower] = lowered
                    continue
            if isinstance(value, SafeUrl):
                check_url_purpose_for_attribute(value, lower)
                out[lower] = value
            elif isinstance(value, str):
                purpose = (
                    UrlPurpose.FORM_ACTION
                    if lower in {"action", "formaction"}
                    else UrlPurpose.ASSET
                    if lower in {"src", "poster", "ping"} or lower.endswith("src")
                    else UrlPurpose.NAVIGATION
                )
                # Local HTMX/resource paths may be provided as strings and are coerced.
                if lower.startswith("hx-") and value.startswith("/") and not value.startswith("//"):
                    out[lower] = SafeUrl.parse(value, purpose=UrlPurpose.NAVIGATION)
                elif lower == "ping":
                    # ping may contain space-separated URLs; require SafeUrl for single URL,
                    # or reject raw strings with javascript:.
                    raise error(
                        "HED-SEC-0003",
                        title="URL attribute requires SafeUrl",
                        explanation=f"Attribute {lower!r} must be a SafeUrl.",
                        remediation="Pass SafeUrl.parse(...).",
                    )
                else:
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
        if (
            http_equiv == "refresh"
            and isinstance(content, str)
            and _META_REFRESH_URL.search(content) is not None
        ):
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

    def __call__(self, *children: NodeLike, **attrs: HtmlAttrValue) -> _NativeElement:
        return _NativeElement(self._tag, children, attrs)


class _NativeElement:
    """Public native HTML node implementing ComponentNode."""

    __slots__ = ("tag", "children", "attributes")

    def __init__(
        self, tag: str, children: tuple[NodeLike, ...], attrs: dict[str, HtmlAttrValue]
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
        self.attributes = _normalize_attrs(attrs, tag=tag_l)

    def __hedron_node__(self) -> _NativeElement:
        return self

    def to_element_node(self, child_nodes: tuple[Node, ...]) -> ElementNode:
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
