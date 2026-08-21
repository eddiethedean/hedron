"""Layout built-ins."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, ClassVar, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.builtins.appearance import (
    Density,
    normalize_responsive_int,
    require_choice,
    responsive_data,
)
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error as raise_error
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue

_GAP_RE = re.compile(r"^\d+(\.\d+)?(rem|em|px|%)$")

# Split ratios are a closed set so the default stylesheet owns the grid math.
SPLIT_RATIOS: tuple[str, ...] = ("1:1", "1:2", "2:1", "1:3", "3:1", "2:3", "3:2")
ACTION_ALIGNMENTS: tuple[str, ...] = ("start", "center", "end", "between")
COLLAPSE_BREAKPOINTS: tuple[str, ...] = ("never", "sm", "md", "lg")


def _validated_gap(gap: str) -> str:
    if not _GAP_RE.match(gap):
        raise raise_error(
            "HED-HTML-0006",
            title="Invalid layout gap",
            explanation=f"Gap {gap!r} is not a safe length token.",
            remediation="Use values like '1rem', '8px', or '50%'.",
        )
    return gap


class ContainerProps(ElementProps):
    pass


class Container(Component[ContainerProps]):
    props_type = ContainerProps

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ContainerProps(id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        attrs = {
            "class_": class_names("hedron-container", self.props.class_),
            "id": self.props.id,
        }
        return html.div(*self._children, **attrs)


class StackProps(ElementProps):
    gap: str = "1rem"


class Stack(Component[StackProps]):
    props_type = StackProps

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        gap: str = "1rem",
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(StackProps(gap=_validated_gap(gap), id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-stack", self.props.class_),
            style=f"--hedron-gap: {self.props.gap}",
            data={"hedron-layout": "stack", "hedron-gap": self.props.gap},
        )


class InlineProps(ElementProps):
    gap: str = "0.5rem"


class Inline(Component[InlineProps]):
    props_type = InlineProps

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        gap: str = "0.5rem",
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(InlineProps(gap=_validated_gap(gap), id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-inline", self.props.class_),
            style=f"--hedron-gap: {self.props.gap}",
            data={"hedron-layout": "inline", "hedron-gap": self.props.gap},
        )


class GridProps(ElementProps):
    columns: int = 2
    gap: str = "1rem"


class Grid(Component[GridProps]):
    """Explicit composition grid; does not return mutable column handles."""

    props_type = GridProps

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        columns: int = 2,
        gap: str = "1rem",
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        if columns < 1:
            raise raise_error(
                "HED-HTML-0006",
                title="Invalid grid columns",
                explanation="columns must be >= 1.",
            )
        super().__init__(
            GridProps(
                columns=columns,
                gap=_validated_gap(gap),
                id=id,
                class_=class_,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-grid", self.props.class_),
            style=f"--hedron-gap: {self.props.gap}",
            data={
                "hedron-layout": "grid",
                "hedron-gap": self.props.gap,
                "hedron-columns": str(self.props.columns),
            },
        )


class DividerProps(Props):
    orientation: Literal["horizontal", "vertical"] = "horizontal"


class Divider(Component[DividerProps]):
    props_type = DividerProps

    def __init__(
        self, orientation: Literal["horizontal", "vertical"] = "horizontal", **kwargs: Any
    ) -> None:
        super().__init__(DividerProps(orientation=orientation, **kwargs))

    def render(self) -> NodeLike:
        if self.props.orientation == "vertical":
            return html.div(role="separator", aria={"orientation": "vertical"})
        return html.hr()


class SpacerProps(ElementProps):
    size: str = "1rem"
    axis: Literal["block", "inline", "both"] = "block"


class Spacer(Component[SpacerProps]):
    """Semantic spacing primitive (gap via layout custom property)."""

    props_type = SpacerProps
    logical_name = "Spacer"

    def __init__(
        self,
        *,
        size: str = "1rem",
        axis: Literal["block", "inline", "both"] = "block",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            SpacerProps(
                size=_validated_gap(size),
                axis=axis,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        data: dict[str, str | bool | int | float | None] = {
            "hedron-layout": "spacer",
            "hedron-gap": self.props.size,
            "hedron-spacer-axis": self.props.axis,
            **mark_data(self.props.mark),
        }
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-spacer", self.props.class_),
            "style": f"--hedron-gap: {self.props.size}",
            "aria": {"hidden": "true"},
            "data": data,
        }
        return html.div(**attrs)


class PageHeaderProps(ElementProps):
    title: str
    eyebrow: str | None = None
    description: str | None = None
    level: Literal[1, 2, 3, 4, 5, 6] = 1
    density: Density | None = None


class PageHeader(Component[PageHeaderProps]):
    """Workspace page title block with optional eyebrow, description, and actions."""

    props_type = PageHeaderProps
    logical_name = "PageHeader"
    slots: ClassVar[dict[str, str]] = {"actions": "optional", "meta": "optional"}

    def __init__(
        self,
        title: str,
        *,
        eyebrow: str | None = None,
        description: str | None = None,
        level: Literal[1, 2, 3, 4, 5, 6] = 1,
        density: Density | None = None,
        actions: NodeLike = None,
        meta: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            PageHeaderProps(
                title=title,
                eyebrow=eyebrow,
                description=description,
                level=level,
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
        text: list[NodeLike] = []
        if self.props.eyebrow:
            text.append(
                html.p(
                    self.props.eyebrow,
                    class_="hedron-page-header-eyebrow hedron-type-eyebrow",
                    data={"hedron-type-role": "eyebrow"},
                )
            )
        heading = getattr(html, f"h{self.props.level}")
        text.append(heading(self.props.title, class_="hedron-page-header-title"))
        if self.props.description:
            text.append(html.p(self.props.description, class_="hedron-page-header-description"))
        if "meta" in self._slot_values:
            text.append(html.div(self._slot_values["meta"], class_="hedron-page-header-meta"))
        parts: list[NodeLike] = [html.div(*text, class_="hedron-page-header-text")]
        if "actions" in self._slot_values:
            parts.append(
                html.div(self._slot_values["actions"], class_="hedron-page-header-actions")
            )
        data: dict[str, str | bool | int | float | None] = {
            "hedron-page-header": "true",
            **mark_data(self.props.mark),
        }
        if self.props.density:
            data["hedron-density"] = self.props.density
        return html.header(
            *parts,
            id=self.props.id,
            class_=class_names("hedron-page-header", self.props.class_),
            data=data,
        )


class SplitViewProps(ElementProps):
    ratio: str = "1:1"
    gap: str = "1.5rem"
    collapse: str = "md"
    reverse: bool = False


class SplitView(Component[SplitViewProps]):
    """Two-pane workspace split with a closed ratio vocabulary."""

    props_type = SplitViewProps
    logical_name = "SplitView"

    def __init__(
        self,
        primary: NodeLike = None,
        secondary: NodeLike = None,
        *,
        ratio: str = "1:1",
        gap: str = "1.5rem",
        collapse: str = "md",
        reverse: bool = False,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(ratio, SPLIT_RATIOS, label="ratio")
        require_choice(collapse, COLLAPSE_BREAKPOINTS, label="collapse")
        super().__init__(
            SplitViewProps(
                ratio=ratio,
                gap=_validated_gap(gap),
                collapse=collapse,
                reverse=reverse,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._primary = primary
        self._secondary = secondary

    def render(self) -> NodeLike:
        panes: list[NodeLike] = [
            html.div(self._primary, class_="hedron-split-primary"),
            html.div(self._secondary, class_="hedron-split-secondary"),
        ]
        data: dict[str, str | bool | int | float | None] = {
            "hedron-layout": "split",
            "hedron-gap": self.props.gap,
            "hedron-split-ratio": self.props.ratio.replace(":", "-"),
            "hedron-split-collapse": self.props.collapse,
            **mark_data(self.props.mark),
        }
        if self.props.reverse:
            data["hedron-split-reverse"] = "true"
        return html.div(
            *panes,
            id=self.props.id,
            class_=class_names("hedron-split", self.props.class_),
            style=f"--hedron-gap: {self.props.gap}",
            data=data,
        )


class MasterDetailProps(ElementProps):
    ratio: str = "1:2"
    gap: str = "1.5rem"
    collapse: str = "md"
    master_id: str = "master"
    detail_id: str = "detail"
    selection: str | None = None
    empty_message: str = "Select an item"
    state: str = "ready"


class MasterDetail(Component[MasterDetailProps]):
    """Responsive master-detail layout with named fragment regions (LAYOUT-055).

    Beta for the first 0.55 release. Selection is application-resolved; missing or
    denied selections must converge to empty/not-found/permission without leaking
    whether an inaccessible record exists.
    """

    props_type = MasterDetailProps
    logical_name = "MasterDetail"
    slots: ClassVar[dict[str, str]] = {
        "master": "optional",
        "detail": "optional",
        "empty": "optional",
        "loading": "optional",
        "error": "optional",
        "permission": "optional",
    }

    def __init__(
        self,
        master: NodeLike = None,
        detail: NodeLike = None,
        *,
        empty: NodeLike = None,
        loading: NodeLike = None,
        error: NodeLike = None,
        permission: NodeLike = None,
        ratio: str = "1:2",
        gap: str = "1.5rem",
        collapse: str = "md",
        master_id: str = "master",
        detail_id: str = "detail",
        selection: str | None = None,
        empty_message: str = "Select an item",
        state: Literal["ready", "loading", "empty", "error", "permission"] = "ready",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(ratio, SPLIT_RATIOS, label="ratio")
        require_choice(collapse, COLLAPSE_BREAKPOINTS, label="collapse")
        if state not in {"ready", "loading", "empty", "error", "permission"}:
            raise raise_error(
                "HED-HTML-0006",
                title="Invalid MasterDetail state",
                explanation=f"State {state!r} is not supported.",
                remediation="Use ready, loading, empty, error, or permission.",
            )
        super().__init__(
            MasterDetailProps(
                ratio=ratio,
                gap=_validated_gap(gap),
                collapse=collapse,
                master_id=master_id.removeprefix("#"),
                detail_id=detail_id.removeprefix("#"),
                selection=selection,
                empty_message=empty_message,
                state=state,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._master = master
        self._detail = detail
        self._empty = empty
        self._loading = loading
        self._error = error
        self._permission = permission

    def fragment_regions(self) -> tuple[str, str]:
        return (self.props.master_id, self.props.detail_id)

    def render(self) -> NodeLike:
        state = self.props.state
        if state == "loading":
            detail_body: NodeLike = self._loading or html.p("Loading…")
        elif state == "error":
            detail_body = self._error or html.p("Unable to load detail")
        elif state == "permission":
            # Never fall through to detail — denied records must not leak content.
            detail_body = self._permission or html.p("Not permitted")
        elif state == "empty" or self._detail is None:
            detail_body = self._empty or html.p(self.props.empty_message)
        else:
            detail_body = self._detail
        data: dict[str, str | bool | int | float | None] = {
            "hedron-layout": "master-detail",
            "hedron-gap": self.props.gap,
            "hedron-split-ratio": self.props.ratio.replace(":", "-"),
            "hedron-split-collapse": self.props.collapse,
            "hedron-master-id": self.props.master_id,
            "hedron-detail-id": self.props.detail_id,
            "hedron-md-state": state,
            **mark_data(self.props.mark),
        }
        if self.props.selection is not None:
            data["hedron-selection"] = self.props.selection
        return html.div(
            html.div(
                self._master,
                id=self.props.master_id,
                class_="hedron-master-pane",
                role="navigation",
                aria={"label": "Master list"},
            ),
            html.div(
                detail_body,
                id=self.props.detail_id,
                class_="hedron-detail-pane",
                role="region",
                aria={"label": "Detail panel", "live": "polite"},
                tabindex="0",
            ),
            id=self.props.id,
            class_=class_names("hedron-master-detail hedron-split", self.props.class_),
            style=f"--hedron-gap: {self.props.gap}",
            data=data,
        )


class FormGridProps(ElementProps):
    columns: dict[str, int]
    gap: str = "1rem"
    density: Density | None = None


class FormGrid(Component[FormGridProps]):
    """Responsive form field grid driven by a breakpoint column map."""

    props_type = FormGridProps
    logical_name = "FormGrid"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        columns: int | Mapping[str, int] = 2,
        gap: str = "1rem",
        density: Density | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        resolved = normalize_responsive_int(columns, label="columns", maximum=4)
        super().__init__(
            FormGridProps(
                columns=resolved,
                gap=_validated_gap(gap),
                density=density,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        data: dict[str, str | bool | int | float | None] = {
            "hedron-layout": "form-grid",
            "hedron-gap": self.props.gap,
            **responsive_data(self.props.columns, prefix="hedron-columns"),
            **mark_data(self.props.mark),
        }
        if self.props.density:
            data["hedron-density"] = self.props.density
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-form-grid", self.props.class_),
            style=f"--hedron-gap: {self.props.gap}",
            data=data,
        )


class ActionGroupProps(ElementProps):
    label: str | None = None
    align: str = "start"
    gap: str = "0.5rem"
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    collapse: str = "sm"


class ActionGroup(Component[ActionGroupProps]):
    """Grouped page or form actions with alignment and collapse behavior."""

    props_type = ActionGroupProps
    logical_name = "ActionGroup"

    def __init__(
        self,
        *nodes: NodeLike,
        children: NodeLike = None,
        label: str | None = None,
        align: str = "start",
        gap: str = "0.5rem",
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        collapse: str = "sm",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(align, ACTION_ALIGNMENTS, label="align")
        require_choice(collapse, COLLAPSE_BREAKPOINTS, label="collapse")
        super().__init__(
            ActionGroupProps(
                label=label,
                align=align,
                gap=_validated_gap(gap),
                orientation=orientation,
                collapse=collapse,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-action-group", self.props.class_),
            "style": f"--hedron-gap: {self.props.gap}",
            "role": "group",
            "data": {
                "hedron-layout": "action-group",
                "hedron-gap": self.props.gap,
                "hedron-align": self.props.align,
                "hedron-orientation": self.props.orientation,
                "hedron-action-collapse": self.props.collapse,
                **mark_data(self.props.mark),
            },
        }
        if self.props.label:
            attrs["aria"] = {"label": self.props.label}
        return html.div(*self._children, **attrs)
