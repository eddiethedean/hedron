"""Document shell built-ins."""

from __future__ import annotations

from typing import Any

from hedron_core.builtins._base import collect_children
from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props


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
        *body: Any,
        lang: str = "en",
        title: str | None = None,
        head: Any = None,
        children: Any = None,
        data_theme: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(PageProps(lang=lang, title=title, data_theme=data_theme, **kwargs))
        self._children = collect_children(*body, children=children)
        if head is not None:
            self._slot_values["head"] = head

    def render(self) -> Any:
        head_nodes: list[Any] = [
            html.meta(charset="utf-8"),
            html.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ]
        if self.props.title:
            head_nodes.append(html.title(self.props.title))
        if "head" in self._slot_values:
            head_nodes.append(self._slot_values["head"])
        html_attrs: dict[str, Any] = {"lang": self.props.lang}
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

    def __init__(self, *nodes: Any, children: Any = None, **kwargs: Any) -> None:
        super().__init__(FragmentProps(**kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> Any:
        return list(self._children)


class HeadProps(Props):
    pass


class Head(Component[HeadProps]):
    props_type = HeadProps

    def __init__(self, *nodes: Any, children: Any = None, **kwargs: Any) -> None:
        super().__init__(HeadProps(**kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> Any:
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
        **kwargs: Any,
    ) -> None:
        value = text if text is not None else (children or "")
        super().__init__(TitleProps(text=value, **kwargs))

    def render(self) -> Any:
        return html.title(self.props.text)
