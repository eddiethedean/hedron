"""First-class HTMX attribute builder for forms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from hedron_core.htmx_contract import safe_css_selector, safe_hx_swap
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue


def _safe_optional_selector(value: str | None, *, label: str) -> str | None:
    if value is None or value == "":
        return None
    if not safe_css_selector(value):
        raise ValueError(f"Unsafe HTMX {label} selector: {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class Hx:
    """First-class HTMX options for ``Form`` (FORM-022)."""

    target: str | None = None
    swap: str = "outerHTML"
    select: str | None = None
    select_oob: str | None = None
    push_url: bool | str = False
    disabled_elt: str | None = None
    indicator: str | None = None
    method: Literal["get", "post", "put", "patch", "delete"] | None = None
    url: str | None = None

    def as_html_attrs(self) -> dict[str, HtmlAttrValue]:
        target = _safe_optional_selector(self.target, label="target")
        select = _safe_optional_selector(self.select, label="select")
        select_oob = self.select_oob or None
        if select_oob is not None:
            from hedron_core.htmx.oob import unparsed_select_oob_tokens

            unparsed = unparsed_select_oob_tokens(select_oob)
            if unparsed:
                tokens = ", ".join(sorted(unparsed))
                raise ValueError(
                    f"select_oob must use simple #id selectors only; unsupported token(s): {tokens}"
                )
        disabled_elt = _safe_optional_selector(self.disabled_elt, label="disabled-elt")
        indicator = _safe_optional_selector(self.indicator, label="indicator")
        if not safe_hx_swap(self.swap):
            raise ValueError(f"Unsafe HTMX swap value: {self.swap!r}")
        attrs: dict[str, HtmlAttrValue] = {}
        if self.method and self.url:
            safe = SafeUrl.parse(self.url, purpose=UrlPurpose.FORM_ACTION)
            attrs[f"hx-{self.method.lower()}"] = safe
        if target:
            attrs["hx-target"] = target
        if self.swap:
            attrs["hx-swap"] = self.swap
        if select:
            attrs["hx-select"] = select
        if select_oob:
            attrs["hx-select-oob"] = select_oob
        if self.push_url is True:
            attrs["hx-push-url"] = "true"
        elif isinstance(self.push_url, str) and self.push_url:
            safe_push = SafeUrl.parse(self.push_url, purpose=UrlPurpose.NAVIGATION)
            attrs["hx-push-url"] = safe_push
        if disabled_elt:
            attrs["hx-disabled-elt"] = disabled_elt
        if indicator:
            attrs["hx-indicator"] = indicator
        return attrs
