"""Resource list primitives (phase 0.57 / RFC-0084)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, ClassVar, cast

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import Density, appearance_data
from hedron_core.codes import HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["ResourceList", "ResourceRow"]

_INTERACTIVE_LOGICAL_NAMES = frozenset(
    {
        "Button",
        "ConfirmButton",
        "DownloadButton",
        "HtmxLink",
        "IconButton",
        "Link",
        "LinkButton",
        "MenuButton",
        "NavLink",
        "SubmitButton",
    }
)


def _node_is_interactive(node: object) -> bool:
    if isinstance(node, Component):
        component = cast(Component[Props], node)
        name = component.logical_name or type(component).__name__
        if name in _INTERACTIVE_LOGICAL_NAMES:
            return True
        if any(_node_is_interactive(value) for value in component.slot_values.values()):
            return True
        if any(_node_is_interactive(child) for child in component.child_nodes):
            return True
    if isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
        return any(_node_is_interactive(item) for item in cast(Sequence[object], node))
    return False


class ResourceRowProps(ElementProps):
    title: str
    description: str | None = None
    href: SafeUrl | None = None
    density: Density | None = None


class ResourceRow(Component[ResourceRowProps]):
    """One resource entry with either a primary link or separate actions — not both nested."""

    props_type = ResourceRowProps
    logical_name = "ResourceRow"
    slots: ClassVar[dict[str, str]] = {"actions": "optional", "meta": "optional"}

    def __init__(
        self,
        title: str,
        *,
        description: str | None = None,
        href: SafeUrl | str | None = None,
        actions: NodeLike = None,
        meta: NodeLike = None,
        density: Density | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not title.strip():
            raise error(
                HED_HTML_0006,
                title="ResourceRow title is required",
                explanation="Each resource row needs a discernible title.",
                remediation="Pass a non-empty title.",
            )
        if href is not None and actions is not None:
            raise error(
                HED_HTML_0006,
                title="Invalid ResourceRow composition",
                explanation=(
                    "A linked ResourceRow cannot also embed action controls. "
                    "Use either href= for navigation or actions= for controls."
                ),
                remediation="Pass href= alone, or actions= without href=.",
            )
        if href is not None and meta is not None and _node_is_interactive(meta):
            raise error(
                HED_HTML_0006,
                title="Invalid ResourceRow composition",
                explanation=(
                    "A linked ResourceRow cannot nest interactive controls in meta=. "
                    "Keep meta text-only when href= is set."
                ),
                remediation="Pass text or Badge/Status meta, or use actions= without href=.",
            )
        url = None
        if href is not None:
            url = (
                href
                if isinstance(href, SafeUrl)
                else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION)
            )
        super().__init__(
            ResourceRowProps(
                title=title,
                description=description,
                href=url,
                density=density,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        if actions is not None:
            self._slot_values["actions"] = actions
        if meta is not None:
            self._slot_values["meta"] = meta

    def render(self) -> NodeLike:
        title_node: NodeLike
        if self.props.href is not None:
            title_node = html.a(
                self.props.title,
                href=self.props.href,
                class_="hedron-resource-row-link",
            )
        else:
            title_node = html.span(self.props.title, class_="hedron-resource-row-title")
        body: list[NodeLike] = [html.div(title_node, class_="hedron-resource-row-primary")]
        if self.props.description:
            body.append(html.p(self.props.description, class_="hedron-resource-row-description"))
        if "meta" in self._slot_values:
            body.append(html.div(self._slot_values["meta"], class_="hedron-resource-row-meta"))
        if "actions" in self._slot_values:
            body.append(
                html.div(self._slot_values["actions"], class_="hedron-resource-row-actions")
            )
        data: dict[str, str | bool | int | float | None] = {
            "hedron-resource-row": "true",
            **appearance_data(density=self.props.density),
            **mark_data(self.props.mark),
        }
        if self.props.href is not None:
            data["hedron-resource-linked"] = "true"
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-resource-row", self.props.class_),
            "data": data,
        }
        return html.li(*body, **attrs)


class ResourceListProps(ElementProps):
    label: str
    density: Density | None = None


class ResourceList(Component[ResourceListProps]):
    """Semantic list of resources with valid link/action composition."""

    props_type = ResourceListProps
    logical_name = "ResourceList"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str,
        density: Density | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not label.strip():
            raise error(
                HED_HTML_0006,
                title="ResourceList label is required",
                explanation="The resource list needs an accessible name.",
                remediation="Pass label='Transfers'.",
            )
        super().__init__(
            ResourceListProps(
                label=label,
                density=density,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        data = {
            "hedron-resource-list": "true",
            **appearance_data(density=self.props.density),
            **mark_data(self.props.mark),
        }
        return html.ul(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-resource-list", self.props.class_),
            aria={"label": self.props.label},
            data=data,
        )
