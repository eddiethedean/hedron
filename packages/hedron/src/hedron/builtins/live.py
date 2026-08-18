"""Live HTMX interaction widgets (refresh, poll, lazy load)."""

from __future__ import annotations

from typing import ClassVar

from hedron.builtins.hx import safe_target
from hedron.routing.reverse import ComponentRef
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.interaction import FragmentRegion
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrMap

__all__ = [
    "ErrorState",
    "InfiniteScroll",
    "Lazy",
    "Loading",
    "Pagination",
    "Poll",
    "RefreshButton",
]


class RefreshButton(Component[Props]):
    logical_name: ClassVar[str | None] = "RefreshButton"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        label: str = "Refresh",
        *,
        ref: ComponentRef | None = None,
        href: str | None = None,
        target: str | None = None,
        swap: str = "outerHTML",
    ) -> None:
        super().__init__(Props())
        self.label = label
        self.ref = ref
        self.href = href
        self.target = safe_target(target)
        self.swap = swap

    @classmethod
    def for_region(
        cls,
        region: FragmentRegion | str,
        *,
        href: str | None = None,
        label: str = "Refresh",
        ref: ComponentRef | None = None,
        swap: str = "outerHTML",
    ) -> RefreshButton:
        """Wire ``hx-target`` from a :class:`~hedron_core.interaction.FragmentRegion`."""
        target = region.selector if isinstance(region, FragmentRegion) else str(region)
        return cls(label, ref=ref, href=href, target=target, swap=swap)

    def render(self) -> NodeLike:
        attrs: HtmlAttrMap = {"type": "button"}
        if self.ref is not None:
            attrs.update(self.ref.hx_attrs())
            if self.target:
                attrs["hx-target"] = self.target
            attrs["hx-swap"] = self.swap
        elif self.href:
            attrs["hx-get"] = SafeUrl.parse(self.href, purpose=UrlPurpose.NAVIGATION)
            if self.target:
                attrs["hx-target"] = self.target
            attrs["hx-swap"] = self.swap
        return html.button(self.label, **attrs)


class Lazy(Component[Props]):
    logical_name: ClassVar[str | None] = "Lazy"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        ref: ComponentRef,
        placeholder: NodeLike | None = None,
        target_id: str | None = None,
        error: NodeLike | None = None,
    ) -> None:
        super().__init__(Props())
        self.ref = ref
        self.placeholder = placeholder
        self.target_id = target_id
        self.error = error

    def render(self) -> NodeLike:
        target_id = self.target_id or f"lazy-{self.render_instance_id()}"
        attrs: HtmlAttrMap = {
            "id": target_id,
            "hx-trigger": "load",
            "hx-swap": "innerHTML",
            "aria-busy": "true",
            "aria-live": "polite",
        }
        attrs.update(self.ref.hx_attrs())
        # Lazy container loads into itself.
        attrs["hx-target"] = f"#{target_id}"
        children: list[NodeLike] = []
        if self.error is not None:
            attrs["data-hedron-error-slot"] = "true"
            children.append(html.template(self.error, **{"data-hedron-error-template": "true"}))
        body = self.placeholder if self.placeholder is not None else Loading("Loading…")
        children.append(body)
        return html.div(*children, **attrs)


class Poll(Component[Props]):
    """Interval-based HTMX refresh helper."""

    logical_name: ClassVar[str | None] = "Poll"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        ref: ComponentRef,
        interval_ms: int = 5000,
        target_id: str | None = None,
        content: NodeLike | None = None,
    ) -> None:
        super().__init__(Props())
        self.ref = ref
        self.interval_ms = max(250, interval_ms)
        self.target_id = target_id
        self.content = content

    def render(self) -> NodeLike:
        target_id = self.target_id or f"poll-{self.render_instance_id()}"
        attrs: HtmlAttrMap = {
            "id": target_id,
            "hx-trigger": f"every {self.interval_ms}ms",
            "hx-swap": "innerHTML",
        }
        attrs.update(self.ref.hx_attrs())
        attrs["hx-target"] = f"#{target_id}"
        body = self.content if self.content is not None else Loading("Polling…")
        return html.div(body, **attrs)


class InfiniteScroll(Component[Props]):
    """Sentinel that loads the next page when revealed."""

    logical_name: ClassVar[str | None] = "InfiniteScroll"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        ref: ComponentRef,
        target: str,
        swap: str = "beforeend",
    ) -> None:
        super().__init__(Props())
        self.ref = ref
        self.target = safe_target(target)
        self.swap = swap

    def render(self) -> NodeLike:
        attrs: HtmlAttrMap = {
            "hx-trigger": "revealed",
            "hx-swap": self.swap,
        }
        attrs.update(self.ref.hx_attrs())
        if self.target:
            attrs["hx-target"] = self.target
        return html.div("Load more", **attrs, class_="hedron-infinite-scroll")


class Loading(Component[Props]):
    logical_name: ClassVar[str | None] = "Loading"
    distribution: ClassVar[str] = "hedron"

    def __init__(self, message: str = "Loading…") -> None:
        super().__init__(Props())
        self.message = message

    def render(self) -> NodeLike:
        return html.div(
            html.span(self.message),
            role="status",
            aria={"live": "polite", "busy": "true"},
            class_="hedron-loading",
        )


class ErrorState(Component[Props]):
    logical_name: ClassVar[str | None] = "ErrorState"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        message: str,
        *,
        retry_href: str | None = None,
        retry_label: str = "Retry",
        target: str | None = None,
    ) -> None:
        super().__init__(Props())
        self.message = message
        self.retry_href = retry_href
        self.retry_label = retry_label
        self.target = safe_target(target)

    def render(self) -> NodeLike:
        children: list[NodeLike] = [
            html.p(self.message, role="alert"),
        ]
        if self.retry_href:
            attrs: HtmlAttrMap = {
                "type": "button",
                "hx-get": SafeUrl.parse(self.retry_href, purpose=UrlPurpose.NAVIGATION),
                "hx-swap": "outerHTML",
            }
            if self.target:
                attrs["hx-target"] = self.target
            children.append(html.button(self.retry_label, **attrs))
        return html.div(*children, class_="hedron-error", role="group")


class Pagination(Component[Props]):
    logical_name: ClassVar[str | None] = "Pagination"
    distribution: ClassVar[str] = "hedron"

    def __init__(
        self,
        *,
        page: int,
        page_size: int,
        total: int,
        base_path: str,
        target: str | None = None,
    ) -> None:
        super().__init__(Props())
        self.page = page
        self.page_size = page_size
        self.total = total
        self.base_path = base_path
        self.target = safe_target(target)

    def render(self) -> NodeLike:
        pages = max(1, (self.total + self.page_size - 1) // self.page_size)
        links: list[NodeLike] = []
        for number in range(1, pages + 1):
            sep = "&" if "?" in self.base_path else "?"
            href_str = f"{self.base_path}{sep}page={number}"
            href = SafeUrl.parse(href_str, purpose=UrlPurpose.NAVIGATION)
            attrs: HtmlAttrMap = {"href": href}
            if self.target:
                attrs.update(
                    {
                        "hx-get": href,
                        "hx-target": self.target,
                        "hx-swap": "innerHTML",
                    }
                )
            label = f"Page {number}" + (" (current)" if number == self.page else "")
            links.append(html.a(str(number), **attrs, aria={"label": label}))
        return html.nav(*links, aria={"label": "Pagination"}, class_="hedron-pagination")
