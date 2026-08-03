"""Document shell built-ins."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props


class PageProps(Props):
    lang: str = "en"
    title: str | None = None


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
        **kwargs: Any,
    ) -> None:
        super().__init__(PageProps(lang=lang, title=title, **kwargs))
        nodes = list(body)
        if children is not None:
            if isinstance(children, Sequence) and not isinstance(children, (str, bytes)):
                nodes.extend(children)
            else:
                nodes.append(children)
        self._children = tuple(nodes)
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
        return html.html(
            html.head(*head_nodes),
            html.body(*self._children),
            lang=self.props.lang,
        )


class FragmentProps(Props):
    pass


class Fragment(Component[FragmentProps]):
    props_type = FragmentProps

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        super().__init__(FragmentProps(**kwargs))
        self._children = children

    def render(self) -> Any:
        return list(self._children)


class HeadProps(Props):
    pass


class Head(Component[HeadProps]):
    props_type = HeadProps

    def __init__(self, *children: Any, **kwargs: Any) -> None:
        super().__init__(HeadProps(**kwargs))
        self._children = children

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
