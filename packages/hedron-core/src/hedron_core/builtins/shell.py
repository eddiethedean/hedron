"""HTMX shell primitives (phase 0.17 / RFC-0044)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.landmarks import Nav
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


class HtmxLinkProps(ElementProps):
    href: SafeUrl
    label: str
    method: Literal["get", "post", "put", "patch", "delete"] = "get"
    target: str | None = None
    swap: str = "outerHTML"
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
        swap: str = "outerHTML",
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
        **kwargs: object,
    ) -> None:
        if not id or not str(id).strip():
            raise ValueError("OobHost requires a non-empty id")
        super().__init__(OobHostProps(id=id, tag=tag, class_=class_, mark=mark, **kwargs))
        self._kids = _kids(*children)

    def render(self) -> NodeLike:
        assert self.props.id is not None
        data = mark_data(self.props.mark)
        data["hedron-oob-host"] = "true"
        return getattr(html, self.props.tag)(
            *self._kids,
            id=self.props.id,
            class_=class_names("hedron-oob-host", self.props.class_),
            data=data,
        )


class AttrHostProps(ElementProps):
    tag: Literal["div", "span", "section"] = "div"
    attrs: dict[str, str] | None = None


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
        **kwargs: object,
    ) -> None:
        if not id or not str(id).strip():
            raise ValueError("AttrHost requires a non-empty id")
        super().__init__(
            AttrHostProps(id=id, tag=tag, attrs=attrs, class_=class_, mark=mark, **kwargs)
        )
        self._kids = _kids(*children)

    def render(self) -> NodeLike:
        assert self.props.id is not None
        data = mark_data(self.props.mark)
        data["hedron-attr-host"] = "true"
        extra: dict[str, HtmlAttrValue] = dict(self.props.attrs or {})
        return getattr(html, self.props.tag)(
            *self._kids,
            id=self.props.id,
            class_=class_names("hedron-attr-host", self.props.class_),
            data=data,
            **extra,
        )


class MainPanelProps(ElementProps):
    pass


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
        **kwargs: object,
    ) -> None:
        super().__init__(MainPanelProps(id=id, class_=class_, mark=mark, **kwargs))
        self._kids = _kids(*children)

    def render(self) -> NodeLike:
        data = mark_data(self.props.mark)
        data["hedron-main-panel"] = "true"
        return html.main(
            *self._kids,
            id=self.props.id,
            class_=class_names("hedron-main-panel", self.props.class_),
            data=data,
        )


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
        from hedron_core.builtins.landmarks import LandmarkProps, _landmark_attrs

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
                *self._nav, class_="hedron-app-shell-nav", data={"hedron-app-nav": "true"}
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
