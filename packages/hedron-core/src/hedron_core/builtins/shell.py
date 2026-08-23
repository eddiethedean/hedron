"""HTMX shell primitives (phase 0.17 / RFC-0044)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import CONTENT_WIDTHS, require_choice
from hedron_core.builtins.landmarks import (
    LandmarkProps,
    Nav,
    _filter_landmark_kwargs,
    _landmark_attrs,
)
from hedron_core.codes import HED_EXT_0006, HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.htmx_contract import safe_css_selector, safe_hx_swap
from hedron_core.htmx_extensions import PRELOAD_INITIATION_MODES, require_htmx_extension
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue


def _kids(*children: NodeLike) -> tuple[NodeLike, ...]:
    return collect_children(*children)


def _normalize_nav_groups(
    groups: Mapping[str, Sequence[NodeLike]] | Sequence[tuple[str, Sequence[NodeLike]]] | None,
) -> tuple[tuple[str, tuple[NodeLike, ...]], ...]:
    """Accept a label→links mapping or an ordered sequence of label/link pairs."""
    if groups is None:
        return ()
    items = groups.items() if isinstance(groups, Mapping) else groups
    normalized: list[tuple[str, tuple[NodeLike, ...]]] = []
    for label, links in items:
        if not str(label).strip():
            raise ValueError("AppShell nav_groups labels must be non-empty")
        normalized.append((str(label), _kids(links)))  # type: ignore[arg-type]
    return tuple(normalized)


def _coerce_nav_url(href: SafeUrl | str, *, allow_external: bool = False) -> SafeUrl:
    if isinstance(href, SafeUrl):
        return href
    return SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION, allow_external=allow_external)


def _safe_optional_selector(value: str | None, *, label: str) -> str | None:
    if value is None or value == "":
        return None
    if not safe_css_selector(value):
        raise ValueError(f"Unsafe HTMX {label} selector: {value!r}")
    return value


def _merge_marker_data(
    mark: str | None,
    caller: Mapping[str, str | bool | int | float | None] | None,
    **markers: str,
) -> dict[str, str | bool | int | float | None]:
    """Merge caller ``data`` with internal ``data-hedron-*`` markers (markers win)."""
    merged: dict[str, str | bool | int | float | None] = {}
    if caller:
        merged.update(caller)
    merged.update(mark_data(mark))
    merged.update(markers)
    return merged


_OOB_HOST_SAFE_KEYS = frozenset(
    {
        "class_",
        "id",
        "tag",
        "mark",
        "lang",
        "dir",
        "title",
        "tabindex",
        "aria",
        "data",
        "hidden",
        "role",
    }
)


def _filter_oob_host_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    unknown = set(kwargs) - _OOB_HOST_SAFE_KEYS
    if unknown:
        raise TypeError(
            f"Unsupported OobHost attribute(s): {sorted(unknown)}. "
            f"Allowlisted: {sorted(k for k in _OOB_HOST_SAFE_KEYS if k != 'role')}."
        )
    role = kwargs.get("role")
    if isinstance(role, str) and role.strip():
        raise TypeError(
            f"role={role!r} is not allowed on OobHost "
            "(prefer native landmark tags via tag=; do not set role=)."
        )
    return {k: v for k, v in kwargs.items() if k in _OOB_HOST_SAFE_KEYS and k != "role"}


class HtmxLinkProps(ElementProps):
    href: SafeUrl
    label: str
    method: Literal["get", "post", "put", "patch", "delete"] = "get"
    target: str | None = None
    swap: str = "innerHTML"
    select: str | None = None
    select_oob: str | None = None
    push_url: bool | str = False
    disabled_elt: str | None = None
    indicator: str | None = None
    active: bool = False
    external: bool = False
    preload: str | None = None
    leading_icon: str | None = None


class HtmxLink(Component[HtmxLinkProps]):
    """Navigation control that emits SafeUrl href plus allowlisted HTMX attrs."""

    props_type = HtmxLinkProps
    logical_name = "HtmxLink"

    def __init__(
        self,
        label: str,
        href: SafeUrl | str,
        *,
        method: Literal["get", "post", "put", "patch", "delete"] = "get",
        target: str | None = None,
        swap: str = "innerHTML",
        select: str | None = None,
        select_oob: str | None = None,
        push_url: bool | str = False,
        disabled_elt: str | None = None,
        indicator: str | None = None,
        active: bool = False,
        external: bool = False,
        preload: str | None = None,
        leading_icon: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        url = _coerce_nav_url(href, allow_external=external)
        target = _safe_optional_selector(target, label="target")
        select = _safe_optional_selector(select, label="select")
        select_oob = select_oob or None
        if select_oob is not None:
            from hedron_core.interaction import unparsed_select_oob_tokens

            unparsed = unparsed_select_oob_tokens(select_oob)
            if unparsed:
                tokens = ", ".join(sorted(unparsed))
                raise ValueError(
                    f"select_oob must use simple #id selectors only; unsupported token(s): {tokens}"
                )
        disabled_elt = _safe_optional_selector(disabled_elt, label="disabled-elt")
        indicator = _safe_optional_selector(indicator, label="indicator")
        if not safe_hx_swap(swap):
            raise ValueError(f"Unsafe HTMX swap value: {swap!r}")
        if preload is not None:
            mode = str(preload).strip().lower()
            if mode not in PRELOAD_INITIATION_MODES:
                raise error(
                    HED_EXT_0006,
                    title="Invalid preload initiation mode",
                    explanation=f"preload={preload!r} is not a closed GET initiation mode.",
                    remediation="Use mousedown, mouseover, or touchstart.",
                )
            if method.lower() != "get":
                raise error(
                    HED_EXT_0006,
                    title="Preload requires a cacheable GET",
                    explanation=f"Cannot preload {method.upper()} requests.",
                    remediation="Attach preload only to GET links and hx-get controls.",
                )
            if external:
                raise error(
                    HED_EXT_0006,
                    title="User-derived or external preload URL rejected",
                    explanation="Preload cannot target external or request-derived URLs.",
                    remediation="Use a same-origin SafeUrl navigation path.",
                )
            preload = mode
        super().__init__(
            HtmxLinkProps(
                href=url,
                label=label,
                method=method,
                target=target,
                swap=swap,
                select=select,
                select_oob=select_oob,
                push_url=push_url,
                disabled_elt=disabled_elt,
                indicator=indicator,
                active=active,
                external=external,
                preload=preload,
                leading_icon=leading_icon,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {"href": self.props.href}
        method = self.props.method.lower()
        path = str(self.props.href)
        # External links are plain navigation; do not emit hx-* absolute URLs
        # (html URL policy rejects absolute schemes on hx-* attributes).
        if not self.props.external:
            attrs[f"hx-{method}"] = path
            if self.props.target:
                attrs["hx-target"] = self.props.target
            if self.props.swap:
                attrs["hx-swap"] = self.props.swap
            if self.props.select:
                attrs["hx-select"] = self.props.select
            if self.props.select_oob:
                attrs["hx-select-oob"] = self.props.select_oob
            if self.props.push_url is True:
                attrs["hx-push-url"] = "true"
            elif isinstance(self.props.push_url, str) and self.props.push_url:
                attrs["hx-push-url"] = self.props.push_url
            if self.props.disabled_elt:
                attrs["hx-disabled-elt"] = self.props.disabled_elt
            if self.props.indicator:
                attrs["hx-indicator"] = self.props.indicator
            if self.props.preload:
                require_htmx_extension("preload")
                attrs["preload"] = self.props.preload
        if self.props.id:
            attrs["id"] = self.props.id
        base = "hedron-nav-link"
        if self.props.active:
            base = class_names(base, "active")
        attrs["class_"] = class_names(base, self.props.class_)
        data = mark_data(self.props.mark)
        data["hedron-nav-link"] = "true"
        if self.props.active:
            data["hedron-nav-active"] = "true"
        attrs["data"] = data
        if self.props.external:
            attrs["rel"] = "noopener noreferrer"
            attrs["target"] = "_blank"
        if self.props.leading_icon:
            from hedron_core.builtins.icon import Icon

            return html.a(
                Icon(self.props.leading_icon, size="sm", decorative=True),
                html.span(self.props.label, class_="hedron-nav-link-label"),
                **attrs,
            )
        return html.a(self.props.label, **attrs)


# Alias preferred by RFC-0044 / issue #28.
NavLink = HtmxLink


class OobHostProps(ElementProps):
    tag: Literal["div", "section", "aside", "main", "nav"] = "div"
    lang: str | None = None
    dir: Literal["ltr", "rtl", "auto"] | None = None
    title: str | None = None
    tabindex: int | None = None
    aria: dict[str, str | bool | int | float | None] | None = None
    data: dict[str, str | bool | int | float | None] | None = None
    hidden: bool | None = None


class OobHost(Component[OobHostProps]):
    """Stable OOB fragment root requiring an explicit element id."""

    props_type = OobHostProps
    logical_name = "OobHost"

    def __init__(
        self,
        *children: NodeLike,
        id: str,
        tag: Literal["div", "section", "aside", "main", "nav"] = "div",
        class_: str | None = None,
        mark: str | None = None,
        lang: str | None = None,
        dir: Literal["ltr", "rtl", "auto"] | None = None,
        title: str | None = None,
        tabindex: int | None = None,
        aria: dict[str, str | bool | int | float | None] | None = None,
        data: dict[str, str | bool | int | float | None] | None = None,
        hidden: bool | None = None,
        **kwargs: object,
    ) -> None:
        if not id or not str(id).strip():
            raise ValueError("OobHost requires a non-empty id")
        filtered = _filter_oob_host_kwargs(
            {
                "id": id,
                "tag": tag,
                "class_": class_,
                "mark": mark,
                "lang": lang,
                "dir": dir,
                "title": title,
                "tabindex": tabindex,
                "aria": aria,
                "data": data,
                "hidden": hidden,
                **kwargs,
            }
        )
        super().__init__(OobHostProps(**filtered))
        self._kids = _kids(*children)

    def render(self) -> NodeLike:
        host_id = self.props.id
        if host_id is None:
            raise ValueError("OobHost requires a non-None id")
        attrs: dict[str, HtmlAttrValue] = {
            "id": host_id,
            "class_": class_names("hedron-oob-host", self.props.class_),
            "data": _merge_marker_data(
                self.props.mark, self.props.data, **{"hedron-oob-host": "true"}
            ),
        }
        if self.props.lang:
            attrs["lang"] = self.props.lang
        if self.props.dir:
            attrs["dir"] = self.props.dir
        if self.props.title:
            attrs["title"] = self.props.title
        if self.props.tabindex is not None:
            attrs["tabindex"] = self.props.tabindex
        if self.props.aria:
            attrs["aria"] = self.props.aria
        if self.props.hidden:
            attrs["hidden"] = True
        return getattr(html, self.props.tag)(*self._kids, **attrs)


class AttrHostProps(ElementProps):
    tag: Literal["div", "span", "section"] = "div"
    attrs: dict[str, str] | None = None
    lang: str | None = None
    dir: Literal["ltr", "rtl", "auto"] | None = None
    title: str | None = None
    tabindex: int | None = None
    aria: dict[str, str | bool | int | float | None] | None = None
    data: dict[str, str | bool | int | float | None] | None = None
    hidden: bool | None = None


_ATTR_HOST_SAFE_KEYS = frozenset(
    {
        "class_",
        "id",
        "tag",
        "mark",
        "attrs",
        "lang",
        "dir",
        "title",
        "tabindex",
        "aria",
        "data",
        "hidden",
    }
)


def _filter_attr_host_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    unknown = set(kwargs) - _ATTR_HOST_SAFE_KEYS
    if unknown:
        raise TypeError(
            f"Unsupported AttrHost attribute(s): {sorted(unknown)}. "
            f"Allowlisted: {sorted(_ATTR_HOST_SAFE_KEYS)}."
        )
    return {k: v for k, v in kwargs.items() if k in _ATTR_HOST_SAFE_KEYS}


class AttrHost(Component[AttrHostProps]):
    """Host element for authorized attribute / OOB attribute swaps."""

    props_type = AttrHostProps
    logical_name = "AttrHost"

    def __init__(
        self,
        *children: NodeLike,
        id: str,
        tag: Literal["div", "span", "section"] = "div",
        attrs: dict[str, str] | None = None,
        class_: str | None = None,
        mark: str | None = None,
        lang: str | None = None,
        dir: Literal["ltr", "rtl", "auto"] | None = None,
        title: str | None = None,
        tabindex: int | None = None,
        aria: dict[str, str | bool | int | float | None] | None = None,
        data: dict[str, str | bool | int | float | None] | None = None,
        hidden: bool | None = None,
        **kwargs: object,
    ) -> None:
        if not id or not str(id).strip():
            raise ValueError("AttrHost requires a non-empty id")
        filtered = _filter_attr_host_kwargs(
            {
                "id": id,
                "tag": tag,
                "attrs": attrs,
                "class_": class_,
                "mark": mark,
                "lang": lang,
                "dir": dir,
                "title": title,
                "tabindex": tabindex,
                "aria": aria,
                "data": data,
                "hidden": hidden,
                **kwargs,
            }
        )
        super().__init__(AttrHostProps(**filtered))
        self._kids = _kids(*children)

    def render(self) -> NodeLike:
        host_id = self.props.id
        if host_id is None:
            raise ValueError("AttrHost requires a non-None id")
        data = _merge_marker_data(self.props.mark, self.props.data, **{"hedron-attr-host": "true"})
        extra: dict[str, HtmlAttrValue] = dict(self.props.attrs or {})
        if self.props.lang:
            extra["lang"] = self.props.lang
        if self.props.dir:
            extra["dir"] = self.props.dir
        if self.props.title:
            extra["title"] = self.props.title
        if self.props.tabindex is not None:
            extra["tabindex"] = self.props.tabindex
        if self.props.aria:
            extra["aria"] = self.props.aria
        if self.props.hidden:
            extra["hidden"] = True
        return getattr(html, self.props.tag)(
            *self._kids,
            id=host_id,
            class_=class_names("hedron-attr-host", self.props.class_),
            data=data,
            **extra,
        )


class MainPanelProps(LandmarkProps):
    mark: str | None = None


class MainPanel(Component[MainPanelProps]):
    """Primary panel region swapped by in-shell HTMX navigation."""

    props_type = MainPanelProps
    logical_name = "MainPanel"

    def __init__(
        self,
        *children: NodeLike,
        id: str = "main-panel",
        class_: str | None = None,
        mark: str | None = None,
        lang: str | None = None,
        dir: Literal["ltr", "rtl", "auto"] | None = None,
        title: str | None = None,
        tabindex: int | None = None,
        aria: dict[str, str | bool | int | float | None] | None = None,
        data: dict[str, str | bool | int | float | None] | None = None,
        hidden: bool | None = None,
        **kwargs: object,
    ) -> None:
        filtered = _filter_landmark_kwargs(
            {
                "id": id,
                "class_": class_,
                "mark": mark,
                "lang": lang,
                "dir": dir,
                "title": title,
                "tabindex": tabindex,
                "aria": aria,
                "data": data,
                "hidden": hidden,
                **kwargs,
            },
            extra_allowed=frozenset({"mark"}),
        )
        super().__init__(MainPanelProps(**filtered))
        self._kids = _kids(*children)

    def render(self) -> NodeLike:
        attrs = _landmark_attrs(self.props)
        attrs["class_"] = class_names("hedron-main-panel", self.props.class_)
        attrs["data"] = _merge_marker_data(
            self.props.mark, self.props.data, **{"hedron-main-panel": "true"}
        )
        return html.main(*self._kids, **attrs)


class AppShellProps(Props):
    panel_id: str = "main-panel"
    class_: str | None = None
    id: str | None = None
    content_width: str = "default"
    mobile_collapse: bool = True


NavGroups = Mapping[str, Sequence[NodeLike]] | Sequence[tuple[str, Sequence[NodeLike]]]


class AppShell(Component[AppShellProps]):
    """Document shell with composed chrome slots, side nav, and MainPanel body.

    Every chrome slot is optional; an ``AppShell(nav=..., body=...)`` call keeps
    the phase 0.17 markup so existing applications are unaffected.
    """

    props_type = AppShellProps
    logical_name = "AppShell"
    slots: ClassVar[dict[str, str]] = {
        "nav": "optional",
        "body": "optional",
        "banner": "optional",
        "brand": "optional",
        "env_badge": "optional",
        "account": "optional",
        "nav_groups": "optional",
        "nav_footer": "optional",
        "app_footer": "optional",
    }

    def __init__(
        self,
        *,
        nav: NodeLike | Sequence[NodeLike] | None = None,
        body: NodeLike | Sequence[NodeLike] | None = None,
        panel_id: str = "main-panel",
        banner: NodeLike = None,
        brand: NodeLike = None,
        env_badge: NodeLike = None,
        account: NodeLike = None,
        nav_groups: NavGroups | None = None,
        nav_footer: NodeLike = None,
        app_footer: NodeLike = None,
        content_width: str = "default",
        mobile_collapse: bool = True,
        class_: str | None = None,
        id: str | None = None,
        **kwargs: object,
    ) -> None:
        require_choice(content_width, CONTENT_WIDTHS, label="content_width")
        super().__init__(
            AppShellProps(
                panel_id=panel_id,
                class_=class_,
                id=id,
                content_width=content_width,
                mobile_collapse=mobile_collapse,
                **kwargs,
            )
        )
        self._nav = () if nav is None else _kids(nav)  # type: ignore[arg-type]
        self._body = () if body is None else _kids(body)  # type: ignore[arg-type]
        self._banner = banner
        self._brand = brand
        self._env_badge = env_badge
        self._account = account
        self._nav_groups = _normalize_nav_groups(nav_groups)
        self._nav_footer = nav_footer
        self._app_footer = app_footer

    def _nav_element(self) -> NodeLike:
        extras: list[NodeLike] = []
        for label, items in self._nav_groups:
            extras.append(
                html.div(
                    html.p(label, class_="hedron-nav-group-label"),
                    html.div(*items, class_="hedron-nav-group-items"),
                    class_="hedron-nav-group",
                    role="group",
                    aria={"label": label},
                    data={"hedron-nav-group": "true"},
                )
            )
        if self._nav_footer is not None:
            extras.append(html.div(self._nav_footer, class_="hedron-app-shell-nav-footer"))
        if len(self._nav) == 1 and isinstance(self._nav[0], Nav):
            # Avoid nested <nav> landmarks when callers pass Nav(...).
            child = self._nav[0]
            data = dict(child.props.data) if isinstance(child.props.data, dict) else {}
            data["hedron-app-nav"] = "true"
            props = LandmarkProps(
                class_=class_names("hedron-app-shell-nav", child.props.class_),
                id=child.props.id,
                lang=child.props.lang,
                dir=child.props.dir,
                title=child.props.title,
                tabindex=child.props.tabindex,
                aria=child.props.aria,
                data=data,
                hidden=child.props.hidden,
            )
            return html.nav(*child._children, *extras, **_landmark_attrs(props))
        return html.nav(
            *self._nav,
            *extras,
            class_="hedron-app-shell-nav",
            data={"hedron-app-nav": "true"},
            aria={"label": "Primary"},
        )

    def _chrome_header(self) -> NodeLike | None:
        parts: list[NodeLike] = []
        if self._brand is not None:
            parts.append(html.div(self._brand, class_="hedron-app-shell-brand"))
        if self._env_badge is not None:
            parts.append(
                html.div(
                    self._env_badge,
                    class_="hedron-app-shell-env",
                    data={"hedron-app-env": "true"},
                )
            )
        if self._account is not None:
            parts.append(html.div(self._account, class_="hedron-app-shell-account"))
        if not parts:
            return None
        return html.header(
            *parts,
            class_="hedron-app-shell-header",
            data={"hedron-app-shell-header": "true"},
        )

    def render(self) -> NodeLike:
        panel = MainPanel(*self._body, id=self.props.panel_id)
        children: list[NodeLike] = []
        if self._banner is not None:
            children.append(
                html.div(
                    self._banner,
                    class_="hedron-app-shell-banner",
                    data={"hedron-app-banner": "true"},
                )
            )
        header = self._chrome_header()
        if header is not None:
            children.append(header)
        children.append(self._nav_element())
        children.append(panel)
        if self._app_footer is not None:
            children.append(
                html.footer(
                    self._app_footer,
                    class_="hedron-app-shell-footer",
                    data={"hedron-app-footer": "true"},
                )
            )
        data: dict[str, str | bool | int | float | None] = {
            "hedron-app-shell": "true",
            "hedron-content-width": self.props.content_width,
        }
        if not self.props.mobile_collapse:
            data["hedron-mobile-collapse"] = "off"
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-app-shell", self.props.class_),
            "data": data,
        }
        if self.props.id:
            attrs["id"] = self.props.id
        return html.div(*children, **attrs)

    def as_fragment(self) -> NodeLike:
        """Return only the main panel subtree for HTMX fragment responses."""
        return MainPanel(*self._body, id=self.props.panel_id)


class BrandProps(ElementProps):
    name: str
    href: SafeUrl | None = None
    mark_text: str | None = None
    subtitle: str | None = None
    subtitle_overflow: Literal["wrap", "break", "truncate", "clip"] = "truncate"
    attrs: dict[str, HtmlAttrValue] | None = None
    aria: dict[str, str | bool | int | float | None] | None = None
    data: dict[str, str | bool | int | float | None] | None = None


class Brand(Component[BrandProps]):
    """Typed AppShell brand mark for zero-application-CSS chrome."""

    props_type = BrandProps
    logical_name = "Brand"

    def __init__(
        self,
        name: str,
        *,
        href: SafeUrl | str | None = None,
        mark_text: str | None = None,
        subtitle: str | None = None,
        subtitle_overflow: Literal["wrap", "break", "truncate", "clip"] = "truncate",
        attrs: dict[str, HtmlAttrValue] | None = None,
        aria: dict[str, str | bool | int | float | None] | None = None,
        data: dict[str, str | bool | int | float | None] | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        if not name.strip():
            raise error(
                HED_HTML_0006,
                title="Brand name is required",
                explanation="Brand chrome needs a discernible product name.",
                remediation="Pass a non-empty name.",
            )
        require_choice(
            subtitle_overflow,
            ("wrap", "break", "truncate", "clip"),
            label="subtitle_overflow",
        )
        url = None
        if href is not None:
            url = href if isinstance(href, SafeUrl) else _coerce_nav_url(href)
        super().__init__(
            BrandProps(
                name=name,
                href=url,
                mark_text=mark_text,
                subtitle=subtitle,
                subtitle_overflow=subtitle_overflow,
                attrs=attrs,
                aria=aria,
                data=data,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        label_parts: list[NodeLike] = [html.strong(self.props.name, class_="hedron-brand-name")]
        if self.props.subtitle:
            label_parts.append(html.small(self.props.subtitle, class_="hedron-brand-subtitle"))
        label = html.span(*label_parts, class_="hedron-brand-copy")
        mark = html.span(
            self.props.mark_text or self.props.name[:1],
            class_="hedron-brand-mark",
            aria={"hidden": "true"},
        )
        data = dict(self.props.data or {})
        data.update(
            {
                "hedron-brand": "true",
                "hedron-brand-subtitle-overflow": self.props.subtitle_overflow,
                **mark_data(self.props.mark),
            }
        )
        extra: dict[str, HtmlAttrValue] = dict(self.props.attrs or {})
        if self.props.aria:
            extra["aria"] = self.props.aria
        inner = (mark, label)
        if self.props.href is not None:
            return html.a(
                *inner,
                href=self.props.href,
                id=self.props.id,
                class_=class_names("hedron-brand", self.props.class_),
                data=data,
                **extra,
            )
        return html.div(
            *inner,
            id=self.props.id,
            class_=class_names("hedron-brand", self.props.class_),
            data=data,
            **extra,
        )


class AccountSummaryProps(ElementProps):
    name: str
    detail: str | None = None
    href: SafeUrl | None = None
    mark_text: str | None = None
    attrs: dict[str, HtmlAttrValue] | None = None
    aria: dict[str, str | bool | int | float | None] | None = None
    data: dict[str, str | bool | int | float | None] | None = None


class AccountSummary(Component[AccountSummaryProps]):
    """Typed account chip for AppShell account slot."""

    props_type = AccountSummaryProps
    logical_name = "AccountSummary"

    def __init__(
        self,
        name: str,
        *nodes: NodeLike,
        detail: str | None = None,
        href: SafeUrl | str | None = None,
        mark_text: str | None = None,
        action: NodeLike = None,
        attrs: dict[str, HtmlAttrValue] | None = None,
        aria: dict[str, str | bool | int | float | None] | None = None,
        data: dict[str, str | bool | int | float | None] | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        if not name.strip():
            raise error(
                HED_HTML_0006,
                title="AccountSummary name is required",
                explanation="Account chrome needs a discernible display name.",
                remediation="Pass a non-empty name.",
            )
        url = None
        if href is not None:
            url = href if isinstance(href, SafeUrl) else _coerce_nav_url(href)
        super().__init__(
            AccountSummaryProps(
                name=name,
                detail=detail,
                href=url,
                mark_text=mark_text,
                attrs=attrs,
                aria=aria,
                data=data,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._actions = collect_children(*nodes, children=action)

    def render(self) -> NodeLike:
        account_copy: list[NodeLike] = [html.span(self.props.name, class_="hedron-account-name")]
        if self.props.detail:
            account_copy.append(html.span(self.props.detail, class_="hedron-account-detail"))
        parts: list[NodeLike] = [
            html.span(
                self.props.mark_text or self.props.name[:1],
                class_="hedron-brand-mark hedron-account-mark",
                aria={"hidden": "true"},
            ),
            html.span(*account_copy, class_="hedron-account-copy"),
        ]
        parts.extend(self._actions)
        data = dict(self.props.data or {})
        data.update({"hedron-account-summary": "true", **mark_data(self.props.mark)})
        extra: dict[str, HtmlAttrValue] = dict(self.props.attrs or {})
        if self.props.aria:
            extra["aria"] = self.props.aria
        if self.props.href is not None:
            return html.a(
                *parts,
                href=self.props.href,
                id=self.props.id,
                class_=class_names("hedron-account-summary", self.props.class_),
                data=data,
                **extra,
            )
        return html.div(
            *parts,
            id=self.props.id,
            class_=class_names("hedron-account-summary", self.props.class_),
            data=data,
            **extra,
        )


class EnvironmentBannerProps(ElementProps):
    label: str
    tone: Literal["info", "success", "warning", "danger"] = "warning"


class EnvironmentBanner(Component[EnvironmentBannerProps]):
    """Environment banner for non-production AppShell chrome."""

    props_type = EnvironmentBannerProps
    logical_name = "EnvironmentBanner"

    def __init__(
        self,
        label: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "warning",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            EnvironmentBannerProps(
                label=label,
                tone=tone,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.div(
            self.props.label,
            id=self.props.id,
            class_=class_names("hedron-environment-banner", self.props.class_),
            role="status",
            data={
                "hedron-environment-banner": "true",
                "hedron-tone": self.props.tone,
                **mark_data(self.props.mark),
            },
        )


class NavStatusProps(ElementProps):
    message: str
    tone: Literal["info", "success", "warning", "danger"] = "info"


class NavStatus(Component[NavStatusProps]):
    """Compact navigation status line for AppShell nav footer/status."""

    props_type = NavStatusProps
    logical_name = "NavStatus"

    def __init__(
        self,
        message: str,
        *,
        tone: Literal["info", "success", "warning", "danger"] = "info",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            NavStatusProps(message=message, tone=tone, id=id, class_=class_, mark=mark, **kwargs)
        )

    def render(self) -> NodeLike:
        return html.p(
            self.props.message,
            id=self.props.id,
            class_=class_names("hedron-nav-status", self.props.class_),
            data={
                "hedron-nav-status": "true",
                "hedron-tone": self.props.tone,
                **mark_data(self.props.mark),
            },
        )


class AppFooterProps(ElementProps):
    text: str


class AppFooter(Component[AppFooterProps]):
    """Typed application footer composition for AppShell footer slot."""

    props_type = AppFooterProps
    logical_name = "AppFooter"

    def __init__(
        self,
        text: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        from hedron_core.builtins._base import collect_children

        super().__init__(AppFooterProps(text=text, id=id, class_=class_, mark=mark, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        parts: list[NodeLike] = [html.span(self.props.text, class_="hedron-app-footer-text")]
        if self._children:
            parts.append(html.div(*self._children, class_="hedron-app-footer-actions"))
        return html.footer(
            *parts,
            id=self.props.id,
            class_=class_names("hedron-app-footer", self.props.class_),
            data={"hedron-app-footer": "true", **mark_data(self.props.mark)},
        )
