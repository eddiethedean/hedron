"""Layout built-ins."""

from __future__ import annotations

import re
from typing import Any, Literal

from hedron_core.builtins._base import ElementProps, class_names, collect_children
from hedron_core.component import Component
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props

_GAP_RE = re.compile(r"^\d+(\.\d+)?(rem|em|px|%)$")


def _validated_gap(gap: str) -> str:
    if not _GAP_RE.match(gap):
        raise error(
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
        *nodes: Any,
        children: Any = None,
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(ContainerProps(id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> Any:
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
        *nodes: Any,
        children: Any = None,
        gap: str = "1rem",
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(StackProps(gap=_validated_gap(gap), id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> Any:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-stack", self.props.class_),
            data={"hedron-layout": "stack", "hedron-gap": self.props.gap},
        )


class InlineProps(ElementProps):
    gap: str = "0.5rem"


class Inline(Component[InlineProps]):
    props_type = InlineProps

    def __init__(
        self,
        *nodes: Any,
        children: Any = None,
        gap: str = "0.5rem",
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(InlineProps(gap=_validated_gap(gap), id=id, class_=class_, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> Any:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-inline", self.props.class_),
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
        *nodes: Any,
        children: Any = None,
        columns: int = 2,
        gap: str = "1rem",
        id: str | None = None,
        class_: str | None = None,
        **kwargs: Any,
    ) -> None:
        if columns < 1:
            raise error(
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

    def render(self) -> Any:
        return html.div(
            *self._children,
            id=self.props.id,
            class_=class_names("hedron-grid", self.props.class_),
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

    def render(self) -> Any:
        if self.props.orientation == "vertical":
            return html.div(role="separator", aria={"orientation": "vertical"})
        return html.hr()
