"""Layout built-ins."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import Any, Literal

from hedron_core.component import Component
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props

_GAP_RE = re.compile(r"^\d+(\.\d+)?(rem|em|px|%)$")


def _kids(*children: Any) -> tuple[Any, ...]:
    if (
        len(children) == 1
        and isinstance(children[0], Sequence)
        and not isinstance(children[0], (str, bytes))
    ):
        return tuple(children[0])
    return children


def _validated_gap(gap: str) -> str:
    if not _GAP_RE.match(gap):
        raise error(
            "HED-HTML-0006",
            title="Invalid layout gap",
            explanation=f"Gap {gap!r} is not a safe length token.",
            remediation="Use values like '1rem', '8px', or '50%'.",
        )
    return gap


class ContainerProps(Props):
    class_: str | None = None


class Container(Component[ContainerProps]):
    props_type = ContainerProps

    def __init__(self, *children: Any, class_: str | None = None, **kwargs: Any) -> None:
        super().__init__(ContainerProps(class_=class_, **kwargs))
        self._children = _kids(*children)

    def render(self) -> Any:
        attrs = {"class_": self.props.class_ or "hedron-container"}
        return html.div(*self._children, **attrs)


class StackProps(Props):
    gap: str = "1rem"
    class_: str | None = None


class Stack(Component[StackProps]):
    props_type = StackProps

    def __init__(
        self, *children: Any, gap: str = "1rem", class_: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(StackProps(gap=_validated_gap(gap), class_=class_, **kwargs))
        self._children = _kids(*children)

    def render(self) -> Any:
        cls = self.props.class_ or "hedron-stack"
        return html.div(
            *self._children,
            class_=cls,
            data={"hedron-layout": "stack", "hedron-gap": self.props.gap},
        )


class InlineProps(Props):
    gap: str = "0.5rem"
    class_: str | None = None


class Inline(Component[InlineProps]):
    props_type = InlineProps

    def __init__(
        self, *children: Any, gap: str = "0.5rem", class_: str | None = None, **kwargs: Any
    ) -> None:
        super().__init__(InlineProps(gap=_validated_gap(gap), class_=class_, **kwargs))
        self._children = _kids(*children)

    def render(self) -> Any:
        cls = self.props.class_ or "hedron-inline"
        return html.div(
            *self._children,
            class_=cls,
            data={"hedron-layout": "inline", "hedron-gap": self.props.gap},
        )


class GridProps(Props):
    columns: int = 2
    gap: str = "1rem"
    class_: str | None = None


class Grid(Component[GridProps]):
    """Explicit composition grid; does not return mutable column handles."""

    props_type = GridProps

    def __init__(
        self,
        *children: Any,
        columns: int = 2,
        gap: str = "1rem",
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
            GridProps(columns=columns, gap=_validated_gap(gap), class_=class_, **kwargs)
        )
        self._children = _kids(*children)

    def render(self) -> Any:
        cls = self.props.class_ or "hedron-grid"
        return html.div(
            *self._children,
            class_=cls,
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
