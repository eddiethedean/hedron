"""HTMX shell primitives (phase 0.17 / RFC-0044)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.landmarks import (
    LandmarkProps,
    Nav,
    _filter_landmark_kwargs,
    _landmark_attrs,
)
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.htmx_contract import safe_css_selector, safe_hx_swap
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue


def _kids(*children: NodeLike) -> tuple[NodeLike, ...]:
    return collect_children(*children)


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
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        url = _coerce_nav_url(href, allow_external=external)
        target = _safe_optional_selector(target, label="target")
        select = _safe_optional_selector(select, label="select")
        select_oob = _safe_optional_selector(select_oob, label="select-oob")
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
        assert self.props.id is not None
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
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
        assert self.props.id is not None
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
            id=self.props.id,
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


class AppShell(Component[AppShellProps]):
    """Document shell with side nav slot and MainPanel body."""

    props_type = AppShellProps
    logical_name = "AppShell"

    def __init__(
        self,
        *,
        nav: NodeLike | Sequence[NodeLike] | None = None,
        body: NodeLike | Sequence[NodeLike] | None = None,
        panel_id: str = "main-panel",
        class_: str | None = None,
        id: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(AppShellProps(panel_id=panel_id, class_=class_, id=id, **kwargs))
        self._nav = () if nav is None else _kids(nav)  # type: ignore[arg-type]
        self._body = () if body is None else _kids(body)  # type: ignore[arg-type]

    def render(self) -> NodeLike:
        panel = MainPanel(*self._body, id=self.props.panel_id)
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
            nav = html.nav(*child._children, **_landmark_attrs(props))
        else:
            nav = html.nav(
                *self._nav,
                class_="hedron-app-shell-nav",
                data={"hedron-app-nav": "true"},
                aria={"label": "Primary"},
            )
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-app-shell", self.props.class_),
            "data": {"hedron-app-shell": "true"},
        }
        if self.props.id:
            attrs["id"] = self.props.id
        return html.div(nav, panel, **attrs)

    def as_fragment(self) -> NodeLike:
        """Return only the main panel subtree for HTMX fragment responses."""
        return MainPanel(*self._body, id=self.props.panel_id)
