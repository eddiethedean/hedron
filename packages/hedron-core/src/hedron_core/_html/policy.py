"""HTML attribute policy used at construction time and serialize time."""

from __future__ import annotations

import re

from hedron_core._html_meta import ALLOWED_ATTRS, ATTR_ALIASES, FORBIDDEN_ATTRS, URL_ATTRS
from hedron_core.diagnostics import error
from hedron_core.htmx_eval import canonical_hx_attribute, hx_attribute_is_url, reject_hx_eval_value
from hedron_core.security import SafeUrl, UrlPurpose, check_url_purpose_for_attribute
from hedron_core.typing_aliases import HtmlAttrValue

# Only layout CSS custom properties — never arbitrary author CSS.
_SAFE_LAYOUT_STYLE = re.compile(r"^--hedron-gap:\s*\d+(\.\d+)?(rem|em|px|%);?$")
# Attribute names must be tokens — never whitespace, quotes, ``=``, or tag breakouts.
_SAFE_ATTR_NAME = re.compile(r"^[A-Za-z_][\w.-]*$")
_SAFE_ALPINE_ATTR_NAME = re.compile(r"^x-[a-z][a-z0-9-]*(?::[A-Za-z0-9_.-]+)?(?:\.[a-z0-9-]+)*$")
_META_REFRESH_URL = re.compile(r"url\s*=", re.IGNORECASE)


class HtmlAttributePolicy:
    """Single source of construction- and serialize-time HTML attribute rules."""

    def is_safe_layout_style(self, value: object) -> bool:
        return isinstance(value, str) and bool(_SAFE_LAYOUT_STYLE.match(value.strip()))

    def require_safe_attr_name(self, name: str) -> str:
        if (
            not name
            or (_SAFE_ATTR_NAME.match(name) is None and _SAFE_ALPINE_ATTR_NAME.match(name) is None)
            or any(ord(ch) < 32 for ch in name)
        ):
            raise error(
                "HED-SEC-0010",
                title="Unsafe attribute name rejected",
                explanation=f"Attribute name {name!r} contains forbidden characters.",
                remediation="Use token attribute names matching [A-Za-z_][\\w.-]*.",
            )
        return name

    def is_event_handler(self, name: str) -> bool:
        return canonical_hx_attribute(name.lower()).startswith("on") or name.lower().startswith(
            "on"
        )

    def is_forbidden_attr(self, name: str) -> bool:
        lower = name.lower()
        return lower in FORBIDDEN_ATTRS or name in FORBIDDEN_ATTRS

    def is_allowed_attr(self, name: str, *, tag: str = "") -> bool:
        lower = name.lower()
        if lower.startswith("data-") or lower.startswith("aria-"):
            return True
        if lower in ALLOWED_ATTRS:
            return True
        # Custom elements may declare observed scalar attributes (phase 0.36 ABI).
        return bool("-" in tag and not lower.startswith("on"))

    def is_url_attr(self, name: str) -> bool:
        lower = name.lower()
        return (
            lower in URL_ATTRS
            or lower.endswith("href")
            or lower.endswith("src")
            or hx_attribute_is_url(lower)
        )

    def normalize_srcset(self, value: object) -> str:
        """Validate srcset candidates; each URL must be SafeUrl or a safe relative path."""
        if isinstance(value, SafeUrl):
            check_url_purpose_for_attribute(value, "srcset")
            return str(value)
        if not isinstance(value, str):
            raise error(
                "HED-SEC-0003",
                title="URL attribute requires SafeUrl",
                explanation="Attribute 'srcset' has unsupported type.",
                remediation=(
                    "Pass SafeUrl.parse(...) or a validated srcset string of SafeUrl paths."
                ),
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

    def reject_meta_refresh_url(self, tag: str, attrs: dict[str, HtmlAttrValue]) -> None:
        if tag != "meta":
            return
        http_equiv = str(attrs.get("http-equiv", "")).lower()
        content = attrs.get("content")
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

    def normalize_attrs(
        self, attrs: dict[str, HtmlAttrValue], *, tag: str
    ) -> dict[str, HtmlAttrValue]:
        out: dict[str, HtmlAttrValue] = {}
        for key, value in attrs.items():
            if value is None:
                continue
            if key == "alpine":
                from hedron_core.alpine import AlpineAttrs

                if not isinstance(value, AlpineAttrs):
                    raise error(
                        "HED-SEC-0012",
                        title="Typed Alpine attributes required",
                        explanation="The alpine= escape hatch accepts only AlpineAttrs.",
                        remediation="Construct AlpineAttrs with typed state/directives.",
                    )
                for alpine_name, alpine_value in value.to_attributes().items():
                    if alpine_name in out:
                        raise error(
                            "HED-SEC-0013",
                            title="Duplicate Alpine attribute",
                            explanation=f"Attribute {alpine_name!r} was provided more than once.",
                            remediation="Declare each Alpine directive once.",
                        )
                    out[alpine_name] = alpine_value
                continue
            if key == "interaction":
                from hedron_core.interaction_067 import Interaction

                if not isinstance(value, Interaction):
                    raise error(
                        "HED-SEC-0015",
                        title="Typed interaction required",
                        explanation="The interaction= escape hatch accepts only Interaction.",
                        remediation="Construct Interaction.local(), .request(), or .combined().",
                    )
                for interaction_name, interaction_value in value.to_attributes(tag=tag).items():
                    if interaction_name in out:
                        raise error(
                            "HED-SEC-0016",
                            title="Duplicate interaction attribute",
                            explanation=(
                                f"Attribute {interaction_name!r} was provided more than once."
                            ),
                            remediation="Declare each interaction once.",
                        )
                    out[interaction_name] = interaction_value
                continue
            if key == "data" and isinstance(value, dict):
                for dk, dv in value.items():
                    safe_key = self.require_safe_attr_name(str(dk))
                    out[f"data-{safe_key}"] = dv
                continue
            if key == "aria" and isinstance(value, dict):
                for ak, av in value.items():
                    safe_key = self.require_safe_attr_name(str(ak))
                    out[f"aria-{safe_key}"] = av
                continue
            name = ATTR_ALIASES.get(key, key)
            self.require_safe_attr_name(str(name))
            lower = name.lower()
            if lower.startswith("x-"):
                raise error(
                    "HED-SEC-0014",
                    title="Raw Alpine attribute rejected",
                    explanation=f"Attribute {name!r} must come from AlpineAttrs.",
                    remediation="Use the typed alpine=AlpineAttrs(...) escape hatch.",
                )
            canonical = canonical_hx_attribute(lower)
            if canonical.startswith("on"):
                raise error(
                    "HED-SEC-0002",
                    title="Inline event handler rejected",
                    explanation=f"Attribute {name!r} is an inline event handler.",
                    remediation="Use HTMX attributes or registered Web Components instead.",
                )
            if lower == "style" or key == "style_":
                if self.is_safe_layout_style(value):
                    out["style"] = str(value).strip().rstrip(";")
                    continue
                raise error(
                    "HED-SEC-0007",
                    title="Forbidden attribute",
                    explanation=f"Attribute {name!r} is not permitted under baseline policy.",
                    remediation=(
                        "Only layout custom properties like '--hedron-gap: 1rem' are allowed."
                    ),
                )
            if self.is_forbidden_attr(lower) or self.is_forbidden_attr(key):
                raise error(
                    "HED-SEC-0007",
                    title="Forbidden attribute",
                    explanation=f"Attribute {name!r} is not permitted under baseline policy.",
                    remediation="Remove style/srcdoc and use typed theme or trusted assets later.",
                )
            if not self.is_allowed_attr(lower, tag=tag):
                raise error(
                    "HED-HTML-0005",
                    title="Unknown HTML attribute",
                    explanation=f"Attribute {name!r} is not in the allowlist.",
                    remediation="Use documented attributes, data={...}, or aria={...}.",
                )
            reject_hx_eval_value(canonical, value)
            url_attr = self.is_url_attr(lower)
            if url_attr:
                if lower == "srcset":
                    out[lower] = self.normalize_srcset(value)
                    continue
                hx_url = canonical if hx_attribute_is_url(lower) else lower
                if hx_url in {"hx-push-url", "hx-replace-url"} and isinstance(value, bool):
                    out[lower] = value
                    continue
                if hx_url in {"hx-push-url", "hx-replace-url"} and isinstance(value, str):
                    lowered_val = value.lower()
                    if lowered_val in {"true", "false"}:
                        out[lower] = lowered_val
                        continue
                if isinstance(value, SafeUrl):
                    check_url_purpose_for_attribute(
                        value, hx_url if hx_url.startswith("hx-") else lower
                    )
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
                    if (
                        hx_url.startswith("hx-")
                        and value.startswith("/")
                        and not value.startswith("//")
                    ):
                        out[lower] = SafeUrl.parse(value, purpose=UrlPurpose.NAVIGATION)
                    elif lower == "ping":
                        raise error(
                            "HED-SEC-0003",
                            title="URL attribute requires SafeUrl",
                            explanation=f"Attribute {lower!r} must be a SafeUrl.",
                            remediation="Pass SafeUrl.parse(...).",
                        )
                    else:
                        attr_name = hx_url if hx_url.startswith("hx-") else lower
                        raise error(
                            "HED-SEC-0003",
                            title="URL attribute requires SafeUrl",
                            explanation=(
                                f"Attribute {attr_name!r} must be a SafeUrl "
                                f"(purpose={purpose.value})."
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

        self.reject_meta_refresh_url(tag, out)
        return out


default_html_policy = HtmlAttributePolicy()


def is_safe_layout_style(value: object) -> bool:
    return default_html_policy.is_safe_layout_style(value)


def require_safe_attr_name(name: str) -> str:
    return default_html_policy.require_safe_attr_name(name)


def normalize_srcset(value: object) -> str:
    return default_html_policy.normalize_srcset(value)


def normalize_attrs(attrs: dict[str, HtmlAttrValue], *, tag: str) -> dict[str, HtmlAttrValue]:
    return default_html_policy.normalize_attrs(attrs, tag=tag)
