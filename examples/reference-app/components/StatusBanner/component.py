"""Python StatusBanner used as the reference twin of the HDN template."""

from __future__ import annotations

from typing import Any

from hedron_core import Component, Field, Props, html


class StatusBannerProps(Props):
    label: str = Field(default="Ready")
    tone: str = Field(default="info")


class StatusBanner(Component[StatusBannerProps]):
    """Representative custom component implemented in Python."""

    props_type = StatusBannerProps
    distribution = "hedron-reference"
    logical_name = "StatusBanner"

    def __init__(self, label: str = "Ready", *, tone: str = "info", **kwargs: Any) -> None:
        super().__init__(StatusBannerProps(label=label, tone=tone, **kwargs))

    def render(self) -> Any:
        return html.div(
            html.strong(self.props.label),
            class_="root",
            data={"tone": self.props.tone, "impl": "python"},
        )
