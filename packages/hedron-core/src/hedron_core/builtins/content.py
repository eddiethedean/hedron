"""Content built-ins."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from hedron_core.builtins._base import ElementProps
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue


def _kids(*children: NodeLike) -> tuple[NodeLike, ...]:
    if (
        len(children) == 1
        and isinstance(children[0], Sequence)
        and not isinstance(children[0], (str, bytes))
    ):
        return tuple(children[0])
    return children


class TextProps(Props):
    content: str
    as_: Literal["p", "span", "strong", "em", "small"] = "p"
    class_: str | None = None


class Text(Component[TextProps]):
    props_type = TextProps

    def __init__(
        self,
        content: str = "",
        *,
        as_: Literal["p", "span", "strong", "em", "small"] = "p",
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(TextProps(content=content, as_=as_, class_=class_, **kwargs))

    def render(self) -> NodeLike:
        from hedron_core.builtins._base import class_names

        attrs: dict[str, HtmlAttrValue] = {}
        if self.props.class_:
            attrs["class_"] = class_names("hedron-text", self.props.class_)
        return getattr(html, self.props.as_)(self.props.content, **attrs)


class HeadingProps(Props):
    content: str
    level: Literal[1, 2, 3, 4, 5, 6] = 2
    class_: str | None = None


class Heading(Component[HeadingProps]):
    props_type = HeadingProps

    def __init__(
        self,
        content: str = "",
        *,
        level: Literal[1, 2, 3, 4, 5, 6] = 2,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(HeadingProps(content=content, level=level, class_=class_, **kwargs))

    def render(self) -> NodeLike:
        from hedron_core.builtins._base import class_names

        attrs: dict[str, HtmlAttrValue] = {}
        if self.props.class_:
            attrs["class_"] = class_names("hedron-heading", self.props.class_)
        return getattr(html, f"h{self.props.level}")(self.props.content, **attrs)


class LinkProps(ElementProps):
    href: SafeUrl
    label: str
    external: bool = False


class Link(Component[LinkProps]):
    props_type = LinkProps

    def __init__(
        self,
        label: str,
        href: SafeUrl | str,
        *,
        external: bool = False,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        url = (
            href
            if isinstance(href, SafeUrl)
            else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION, allow_external=external)
        )
        super().__init__(
            LinkProps(
                href=url,
                label=label,
                external=external,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        from hedron_core.builtins._base import class_names, mark_data

        attrs: dict[str, HtmlAttrValue] = {"href": self.props.href}
        if self.props.external:
            attrs["rel"] = "noopener noreferrer"
            attrs["target"] = "_blank"
        if self.props.id:
            attrs["id"] = self.props.id
        if self.props.class_:
            attrs["class_"] = class_names("hedron-link", self.props.class_)
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.a(self.props.label, **attrs)


class ImageProps(Props):
    src: SafeUrl
    alt: str
    width: int | None = None
    height: int | None = None


class Image(Component[ImageProps]):
    props_type = ImageProps

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        alt: str,
        width: int | None = None,
        height: int | None = None,
        allow_external: bool = False,
        **kwargs: object,
    ) -> None:
        url = (
            src
            if isinstance(src, SafeUrl)
            else SafeUrl.parse(src, purpose=UrlPurpose.ASSET, allow_external=allow_external)
        )
        super().__init__(ImageProps(src=url, alt=alt, width=width, height=height, **kwargs))

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {"src": self.props.src, "alt": self.props.alt}
        if self.props.width is not None:
            attrs["width"] = self.props.width
        if self.props.height is not None:
            attrs["height"] = self.props.height
        return html.img(**attrs)


class CodeBlockProps(Props):
    code: str
    language: str | None = None


class CodeBlock(Component[CodeBlockProps]):
    props_type = CodeBlockProps

    def __init__(self, code: str, *, language: str | None = None, **kwargs: object) -> None:
        super().__init__(CodeBlockProps(code=code, language=language, **kwargs))

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {}
        if self.props.language:
            attrs["class_"] = f"language-{self.props.language}"
        return html.pre(html.code(self.props.code, **attrs))


class ListProps(Props):
    ordered: bool = False


class List(Component[ListProps]):
    props_type = ListProps

    def __init__(self, *items: NodeLike, ordered: bool = False, **kwargs: object) -> None:
        super().__init__(ListProps(ordered=ordered, **kwargs))
        self._items = _kids(*items)

    def render(self) -> NodeLike:
        lis = [html.li(item) for item in self._items]
        return html.ol(*lis) if self.props.ordered else html.ul(*lis)


class DescriptionListProps(Props):
    pass


class DescriptionList(Component[DescriptionListProps]):
    props_type = DescriptionListProps

    def __init__(self, *pairs: tuple[NodeLike, NodeLike], **kwargs: object) -> None:
        super().__init__(DescriptionListProps(**kwargs))
        self._pairs = pairs

    def render(self) -> NodeLike:
        nodes: list[NodeLike] = []
        for term, desc in self._pairs:
            nodes.append(html.dt(term))
            nodes.append(html.dd(desc))
        return html.dl(*nodes)


class TableProps(Props):
    caption: str | None = None


class Table(Component[TableProps]):
    """Static table; not a mutable DataTable."""

    props_type = TableProps

    def __init__(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[NodeLike]],
        *,
        caption: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(TableProps(caption=caption, **kwargs))
        self._headers = tuple(headers)
        self._rows = tuple(tuple(r) for r in rows)

    def render(self) -> NodeLike:
        children: list[NodeLike] = []
        if self.props.caption:
            children.append(html.caption(self.props.caption))
        children.append(html.thead(html.tr(*[html.th(h, scope="col") for h in self._headers])))
        body_rows = [html.tr(*[html.td(cell) for cell in row]) for row in self._rows]
        children.append(html.tbody(*body_rows))
        return html.table(*children)
