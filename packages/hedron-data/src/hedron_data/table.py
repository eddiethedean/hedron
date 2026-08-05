"""Server-rendered accessible DataTable."""

from __future__ import annotations

import csv
import io
from collections.abc import Mapping, Sequence

from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Model, Props
from hedron_core.security import Secret
from hedron_core.typing_aliases import HtmlAttrMap, JsonValue
from hedron_data.columns import Column, resolve_columns
from hedron_data.normalize import normalize_rows
from hedron_data.sources import DataPage, DataQuery


def _cell_text(value: object) -> str:
    if isinstance(value, Secret):
        return "***"
    if value is None:
        return ""
    return str(value)


class DataTableProps(Props):
    caption: str | None = None
    empty_message: str = "No rows"
    page_size: int = 25
    allow_download: bool = False


class DataTable(Component[DataTableProps]):
    """Read-only accessible table with paging metadata and CSV helper."""

    props_type = DataTableProps
    distribution = "hedron-data"
    logical_name = "DataTable"

    def __init__(
        self,
        rows: object = None,
        *,
        row_model: type[Model] | None = None,
        columns: Sequence[Column] | None = None,
        page: DataPage[dict[str, JsonValue]] | None = None,
        query: DataQuery | None = None,
        caption: str | None = None,
        empty_message: str = "No rows",
        page_size: int = 25,
        allow_download: bool = False,
        **kwargs: object,
    ) -> None:
        super().__init__(
            DataTableProps(
                caption=caption,
                empty_message=empty_message,
                page_size=page_size,
                allow_download=allow_download,
                **kwargs,
            )
        )
        if page is not None:
            raw_rows = list(page.rows)
            self._total = page.total
            self._version = page.version
        else:
            raw_rows = normalize_rows(rows)
            self._total = len(raw_rows)
            self._version = None
        built_rows: list[dict[str, JsonValue]] = []
        for r in raw_rows:
            if isinstance(r, Mapping):
                built_rows.append(dict(r))
            else:
                built_rows.append(dict(r.model_dump()))  # type: ignore[union-attr]
        self._rows = built_rows
        self._columns = resolve_columns(row_model=row_model, columns=columns, rows=self._rows)
        self._query = query

    @property
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def rows(self) -> list[dict[str, JsonValue]]:
        return list(self._rows)

    def to_csv(self) -> str:
        from hedron_data.spreadsheet import _reject_or_sanitize

        visible = [c for c in self._columns if not c.hidden and not c.secret]
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([c.label or c.name for c in visible])
        for row in self._rows:
            writer.writerow(
                [
                    _reject_or_sanitize(_cell_text(row.get(c.name)), formula_policy="sanitize")
                    for c in visible
                ]
            )
        return buf.getvalue()

    def render(self) -> NodeLike:
        visible = [c for c in self._columns if not c.hidden]
        children: list[NodeLike] = []
        if self.props.caption:
            children.append(html.caption(self.props.caption))
        headers = [
            html.th(c.label or c.name, scope="col", **({"aria-sort": "none"} if c.sortable else {}))
            for c in visible
        ]
        children.append(html.thead(html.tr(*headers)))
        if not self._rows:
            children.append(
                html.tbody(html.tr(html.td(self.props.empty_message, colspan=max(len(visible), 1))))
            )
        else:
            body_rows = []
            for row in self._rows:
                cells = []
                for c in visible:
                    val = row.get(c.name)
                    text = "***" if c.secret else _cell_text(val)
                    cells.append(html.td(text))
                body_rows.append(html.tr(*cells))
            children.append(html.tbody(*body_rows))
        attrs: HtmlAttrMap = {"role": "table", "class_": "hedron-data-table"}
        if self._total is not None:
            attrs["data-total"] = str(self._total)
        if self._version is not None:
            attrs["data-version"] = self._version
        return html.table(*children, **attrs)
