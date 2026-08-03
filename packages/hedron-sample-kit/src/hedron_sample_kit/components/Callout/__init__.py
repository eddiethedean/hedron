"""Callout sample component."""

from __future__ import annotations

from typing import Any

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props

__all__ = ["Callout", "CalloutProps", "EXAMPLES", "default"]


class CalloutProps(Props):
    message: str = "Hello from sample kit"


class Callout(Component[CalloutProps]):
    props_type = CalloutProps
    logical_name = "Callout"
    distribution = "hedron-sample-kit"

    def __init__(self, message: str = "Hello from sample kit", **kwargs: Any) -> None:
        super().__init__(CalloutProps(message=message, **kwargs))

    def render(self) -> Any:
        return html.div(self.props.message, class_="root")


def default() -> Callout:
    """Named example: default callout."""
    return Callout(message="Sample kit callout")


EXAMPLES = {"default": default}
