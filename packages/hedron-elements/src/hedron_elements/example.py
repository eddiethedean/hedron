"""Reference light-DOM element: hedron-example."""

from __future__ import annotations

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.registry import ElementFieldOwnership
from hedron_elements.markup import render_element_markup

ABI_VERSION = 1
TAG_NAME = "hedron-example"
ELEMENT_ID = "hedron-example"


class ExampleProps(Props):
    status: str = "Ready"
    class_: str | None = None


class Example(Component[ExampleProps]):
    """ABI probe with controlled status text and disposable local UI."""

    props_type = ExampleProps
    logical_name = "Example"
    distribution = "hedron-elements"

    def __init__(
        self,
        status: str = "Ready",
        *,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(ExampleProps(status=status, class_=class_, **kwargs))

    def render(self) -> NodeLike:
        return html.tag(TAG_NAME)(
            html.p(self.props.status, **{"data-hedron-server-region": "content"}),
            html.button("Details", type="button", **{"data-hedron-local": "toggle"}),
            html.div(
                "Local-only panel (disposable).",
                hidden=True,
                **{"data-hedron-local": "panel"},
            ),
            **{
                "data-hedron-abi": str(ABI_VERSION),
                "data-hedron-element": ELEMENT_ID,
                "status": self.props.status,
                "class_": self.props.class_,
            },
        )

    def render_markup(self) -> str:
        return render_element_markup(
            tag_name=TAG_NAME,
            abi_version=ABI_VERSION,
            element_id=ELEMENT_ID,
            attributes={"status": self.props.status},
            server_content=self.props.status,
        )


EXAMPLE_OWNERSHIP: tuple[ElementFieldOwnership, ...] = (
    ElementFieldOwnership(
        name="status",
        mode="controlled",
        reflection="attribute",
        incoming_update="replace",
        persistence="none",
        event="hedron-example-change",
    ),
    ElementFieldOwnership(
        name="expanded",
        mode="local",
        reflection="none",
        incoming_update="preserve",
        persistence="none",
        event="hedron-example-change",
    ),
)
