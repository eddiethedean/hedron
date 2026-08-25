"""Content built-ins."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal

from hedron_core.builtins._base import ElementProps, class_names
from hedron_core.builtins.appearance import (
    TYPE_EFFECTS,
    TYPE_MEASURES,
    TYPOGRAPHY_ROLES,
    Density,
    OverflowMode,
    ResponsivePolicy,
    TypographyEffect,
    TypographyMeasure,
    TypographyRole,
    appearance_data,
    normalize_responsive_int,
    require_choice,
    responsive_data,
)
from hedron_core.codes import HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Model, Props
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


def _typography_attrs(
    base: str,
    role: str | None,
    class_: str | None,
    *,
    overflow: str | None = None,
    lines: int | None = None,
    measure: str | None = None,
    effect: str | None = None,
) -> dict[str, HtmlAttrValue]:
    """Return class/data attributes for a semantic typography role."""
    attrs: dict[str, HtmlAttrValue] = {}
    data: dict[str, str | bool | int | float | None] = {}
    if role:
        attrs["class_"] = class_names(f"{base} hedron-type-{role}", class_)
        data["hedron-type-role"] = role
    elif class_:
        attrs["class_"] = class_names(base, class_)
    # When both overflow=truncate and lines are set, lines win (multi-line clamp).
    effective_overflow = overflow
    if lines is not None and overflow == "truncate":
        effective_overflow = None
    if effective_overflow:
        data.update(appearance_data(overflow=effective_overflow))
        if "class_" not in attrs:
            attrs["class_"] = base
    if lines is not None:
        data["hedron-lines"] = str(lines)
        if "class_" not in attrs:
            attrs["class_"] = base
    if measure is not None:
        data["hedron-type-measure"] = measure
    if effect is not None:
        data["hedron-type-effect"] = effect
    if data:
        attrs["data"] = data
    return attrs


def _validate_lines(lines: int | None) -> int | None:
    if lines is None:
        return None
    if not isinstance(lines, int) or isinstance(lines, bool) or lines < 1 or lines > 6:
        raise error(
            HED_HTML_0006,
            title="Invalid lines value",
            explanation=f"lines={lines!r} must be an integer from 1 to 6.",
            remediation="Pass lines=1..6 for bounded line clamp.",
        )
    return lines


class TextProps(Props):
    content: str
    as_: Literal["p", "span", "strong", "em", "small"] = "p"
    role: TypographyRole | None = None
    overflow: OverflowMode | None = None
    lines: int | None = None
    measure: TypographyMeasure | None = None
    effect: TypographyEffect | None = None
    class_: str | None = None


class Text(Component[TextProps]):
    props_type = TextProps

    def __init__(
        self,
        content: str = "",
        *,
        as_: Literal["p", "span", "strong", "em", "small"] = "p",
        role: TypographyRole | None = None,
        overflow: OverflowMode | None = None,
        lines: int | None = None,
        measure: TypographyMeasure | None = None,
        effect: TypographyEffect | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        require_choice(role, TYPOGRAPHY_ROLES, label="role")
        require_choice(overflow, ("wrap", "break", "truncate", "clip"), label="overflow")
        require_choice(measure, TYPE_MEASURES, label="measure")
        require_choice(effect, TYPE_EFFECTS, label="effect")
        super().__init__(
            TextProps(
                content=content,
                as_=as_,
                role=role,
                overflow=overflow,
                lines=_validate_lines(lines),
                measure=measure,
                effect=effect,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs = _typography_attrs(
            "hedron-text",
            self.props.role,
            self.props.class_,
            overflow=self.props.overflow,
            lines=self.props.lines,
            measure=self.props.measure,
            effect=self.props.effect,
        )
        return getattr(html, self.props.as_)(self.props.content, **attrs)


class HeadingProps(Props):
    content: str
    level: Literal[1, 2, 3, 4, 5, 6] = 2
    role: TypographyRole | None = None
    overflow: OverflowMode | None = None
    lines: int | None = None
    measure: TypographyMeasure | None = None
    effect: TypographyEffect | None = None
    class_: str | None = None


class Heading(Component[HeadingProps]):
    props_type = HeadingProps

    def __init__(
        self,
        content: str = "",
        *,
        level: Literal[1, 2, 3, 4, 5, 6] = 2,
        role: TypographyRole | None = None,
        overflow: OverflowMode | None = None,
        lines: int | None = None,
        measure: TypographyMeasure | None = None,
        effect: TypographyEffect | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        require_choice(role, TYPOGRAPHY_ROLES, label="role")
        require_choice(overflow, ("wrap", "break", "truncate", "clip"), label="overflow")
        require_choice(measure, TYPE_MEASURES, label="measure")
        require_choice(effect, TYPE_EFFECTS, label="effect")
        super().__init__(
            HeadingProps(
                content=content,
                level=level,
                role=role,
                overflow=overflow,
                lines=_validate_lines(lines),
                measure=measure,
                effect=effect,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs = _typography_attrs(
            "hedron-heading",
            self.props.role,
            self.props.class_,
            overflow=self.props.overflow,
            lines=self.props.lines,
            measure=self.props.measure,
            effect=self.props.effect,
        )
        return getattr(html, f"h{self.props.level}")(self.props.content, **attrs)


class TypographyProps(Props):
    content: str
    role: TypographyRole = "body"
    as_: Literal["p", "span", "div", "strong", "em", "small", "code"] = "p"
    overflow: OverflowMode | None = None
    lines: int | None = None
    measure: TypographyMeasure | None = None
    effect: TypographyEffect | None = None
    class_: str | None = None


class Typography(Component[TypographyProps]):
    """Role-first text helper for authors who think in type scale, not tags."""

    props_type = TypographyProps
    logical_name = "Typography"

    def __init__(
        self,
        content: str = "",
        *,
        role: TypographyRole = "body",
        as_: Literal["p", "span", "div", "strong", "em", "small", "code"] = "p",
        overflow: OverflowMode | None = None,
        lines: int | None = None,
        measure: TypographyMeasure | None = None,
        effect: TypographyEffect | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        require_choice(role, TYPOGRAPHY_ROLES, label="role")
        require_choice(overflow, ("wrap", "break", "truncate", "clip"), label="overflow")
        require_choice(measure, TYPE_MEASURES, label="measure")
        require_choice(effect, TYPE_EFFECTS, label="effect")
        super().__init__(
            TypographyProps(
                content=content,
                role=role,
                as_=as_,
                overflow=overflow,
                lines=_validate_lines(lines),
                measure=measure,
                effect=effect,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs = _typography_attrs(
            "hedron-text",
            self.props.role,
            self.props.class_,
            overflow=self.props.overflow,
            lines=self.props.lines,
            measure=self.props.measure,
            effect=self.props.effect,
        )
        return getattr(html, self.props.as_)(self.props.content, **attrs)


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
    columns: dict[str, int] | None = None
    density: Density | None = None
    layout: Literal["stacked", "inline"] = "stacked"


class DescriptionList(Component[DescriptionListProps]):
    props_type = DescriptionListProps

    def __init__(
        self,
        *pairs: tuple[NodeLike, NodeLike],
        columns: int | Mapping[str, int] | None = None,
        density: Density | None = None,
        layout: Literal["stacked", "inline"] = "stacked",
        **kwargs: object,
    ) -> None:
        resolved = (
            None
            if columns is None
            else normalize_responsive_int(columns, label="columns", maximum=3)
        )
        super().__init__(
            DescriptionListProps(
                columns=resolved,
                density=density,
                layout=layout,
                **kwargs,
            )
        )
        self._pairs = pairs

    def render(self) -> NodeLike:
        nodes: list[NodeLike] = []
        for term, desc in self._pairs:
            nodes.append(html.dt(term))
            nodes.append(html.dd(desc))
        attrs: dict[str, HtmlAttrValue] = {}
        data: dict[str, str | bool | int | float | None] = {}
        if self.props.columns:
            data.update(responsive_data(self.props.columns, prefix="hedron-columns"))
        if self.props.density:
            data["hedron-density"] = self.props.density
        if self.props.layout != "stacked":
            data["hedron-dl-layout"] = self.props.layout
        if data:
            attrs["class_"] = "hedron-description-list"
            attrs["data"] = data
        return html.dl(*nodes, **attrs)


class TableColumn(Model):
    """Presentation metadata for one static table column."""

    header: str
    align: Literal["start", "center", "end"] = "start"
    numeric: bool = False
    size: Literal["auto", "narrow", "wide"] = "auto"
    overflow: OverflowMode | None = None
    priority: int | None = None
    kind: Literal["text", "numeric", "action", "status"] | None = None


class TableProps(Props):
    caption: str | None = None
    density: Density | None = None
    sticky_header: bool = False
    sticky_first_column: bool = False
    zebra: bool = False
    responsive: ResponsivePolicy | None = None


class Table(Component[TableProps]):
    """Static table; not a mutable DataTable.

    ``columns`` supplies per-column presentation metadata. When it is provided
    without ``headers``, the column headers are taken from the metadata.
    """

    props_type = TableProps

    def __init__(
        self,
        headers: Sequence[str] | None = None,
        rows: Sequence[Sequence[NodeLike]] = (),
        *,
        caption: str | None = None,
        columns: Sequence[TableColumn] | None = None,
        density: Density | None = None,
        sticky_header: bool = False,
        sticky_first_column: bool = False,
        zebra: bool = False,
        responsive: ResponsivePolicy | None = None,
        row_states: Sequence[str | None] | None = None,
        **kwargs: object,
    ) -> None:
        column_meta = tuple(columns or ())
        resolved_headers = tuple(headers or ()) or tuple(column.header for column in column_meta)
        if column_meta and len(column_meta) != len(resolved_headers):
            raise ValueError(
                "Table columns metadata must have one entry per header "
                f"({len(column_meta)} columns, {len(resolved_headers)} headers)"
            )
        require_choice(responsive, ("scroll", "stack", "priority"), label="responsive")
        super().__init__(
            TableProps(
                caption=caption,
                density=density,
                sticky_header=sticky_header,
                sticky_first_column=sticky_first_column,
                zebra=zebra,
                responsive=responsive,
                **kwargs,
            )
        )
        self._row_states = tuple(row_states or ())
        self._headers = resolved_headers
        self._rows = tuple(tuple(r) for r in rows)
        self._columns = column_meta
        if not hasattr(self, "_row_states"):
            self._row_states = ()

    def _cell_data(self, index: int) -> dict[str, str | bool | int | float | None]:
        if index >= len(self._columns):
            return {}
        column = self._columns[index]
        data: dict[str, str | bool | int | float | None] = {"hedron-align": column.align}
        if column.numeric:
            data["hedron-numeric"] = "true"
        if column.size != "auto":
            data["hedron-col-size"] = column.size
        if column.overflow:
            data["hedron-overflow"] = column.overflow
        if column.priority is not None:
            data["hedron-priority"] = str(column.priority)
        if column.kind:
            data["hedron-col-kind"] = column.kind
        return data

    def render(self) -> NodeLike:
        children: list[NodeLike] = []
        if self.props.caption:
            children.append(html.caption(self.props.caption))
        header_cells: list[NodeLike] = []
        for index, header in enumerate(self._headers):
            cell_data = self._cell_data(index)
            header_cells.append(
                html.th(header, scope="col", **({"data": cell_data} if cell_data else {}))
            )
        children.append(html.thead(html.tr(*header_cells)))
        body_rows: list[NodeLike] = []
        for row_index, row in enumerate(self._rows):
            cells: list[NodeLike] = []
            for index, cell in enumerate(row):
                cell_data = self._cell_data(index)
                cells.append(html.td(cell, **({"data": cell_data} if cell_data else {})))
            row_attrs: dict[str, HtmlAttrValue] = {}
            if row_index < len(self._row_states) and self._row_states[row_index]:
                row_attrs["data"] = {"hedron-row-state": self._row_states[row_index]}
            body_rows.append(html.tr(*cells, **row_attrs))
        children.append(html.tbody(*body_rows))

        data: dict[str, str | bool | int | float | None] = {}
        if self.props.density:
            data["hedron-density"] = self.props.density
        if self.props.sticky_header:
            data["hedron-sticky-header"] = "true"
        if self.props.sticky_first_column:
            data["hedron-sticky-column"] = "true"
        if self.props.zebra:
            data["hedron-zebra"] = "true"
        if self.props.responsive:
            data["hedron-responsive"] = self.props.responsive
        if not data:
            return html.table(*children)
        table = html.table(*children, class_="hedron-table", data=data)
        if (
            self.props.sticky_header
            or self.props.sticky_first_column
            or self.props.responsive == "scroll"
        ):
            return html.div(table, class_="hedron-table-scroll", data=dict(data))
        return table
