"""Document shell built-ins."""

from __future__ import annotations

from hedron_core.builtins._base import collect_children
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue


class PageProps(Props):
    lang: str = "en"
    title: str | None = None
    data_theme: str | None = None


class Page(Component[PageProps]):
    """Full HTML document shell."""

    props_type = PageProps
    slots = {"head": "optional", "body": "required"}

    def __init__(
        self,
        *body: NodeLike,
        lang: str = "en",
        title: str | None = None,
        head: NodeLike = None,
        children: NodeLike = None,
        data_theme: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(PageProps(lang=lang, title=title, data_theme=data_theme, **kwargs))
        self._children = collect_children(*body, children=children)
        if head is not None:
            self._slot_values["head"] = head

    def render(self) -> NodeLike:
        head_nodes: list[NodeLike] = [
            html.meta(charset="utf-8"),
            html.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ]
        if self.props.title:
            head_nodes.append(html.title(self.props.title))
        if "head" in self._slot_values:
            head_nodes.append(self._slot_values["head"])
        html_attrs: dict[str, HtmlAttrValue] = {"lang": self.props.lang}
        if self.props.data_theme:
            html_attrs["data"] = {"theme": self.props.data_theme}
        return html.html(
            html.head(*head_nodes),
            html.body(*self._children),
            **html_attrs,
        )


class FragmentProps(Props):
    pass


class Fragment(Component[FragmentProps]):
    props_type = FragmentProps

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(FragmentProps(**kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return list(self._children)


class HeadProps(Props):
    pass


class Head(Component[HeadProps]):
    props_type = HeadProps

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(HeadProps(**kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.head(*self._children)


class TitleProps(Props):
    text: str


class Title(Component[TitleProps]):
    props_type = TitleProps

    def __init__(
        self,
        text: str | None = None,
        *,
        children: str | None = None,
        **kwargs: object,
    ) -> None:
        value = text if text is not None else (children or "")
        super().__init__(TitleProps(text=value, **kwargs))

    def render(self) -> NodeLike:
        return html.title(self.props.text)
