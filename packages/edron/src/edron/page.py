from __future__ import annotations

import base64
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Literal

import hedron
from edron._internal import require_frame
from edron.errors import BindingError


@dataclass
class Container:
    """A request-local layout container."""

    page: Page
    kind: str = "stack"
    options: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)
    _entered: bool = field(default=False, init=False)

    def _append(self, value: Any) -> None:
        self.children.append(value)

    def __enter__(self) -> Container:
        if self._entered:
            raise RuntimeError("a container cannot be entered twice")
        self._entered = True
        self.page._container_stack.append(self)
        return self

    def __exit__(self, *_: Any) -> None:
        if not self.page._container_stack or self.page._container_stack[-1] is not self:
            raise RuntimeError("containers must be exited in nesting order")
        self.page._container_stack.pop()

    def text(self, value: str) -> None:
        self.page.text(value, _target=self)

    def selectbox(self, label: str, options: Sequence[Any], **kwargs: Any) -> Any:
        return self.page.selectbox(label, options, _target=self, **kwargs)

    def multiselect(self, label: str, options: Sequence[Any], **kwargs: Any) -> list[Any]:
        return self.page.multiselect(label, options, _target=self, **kwargs)

    def button(self, label: str, **kwargs: Any) -> None:
        return self.page.button(label, _target=self, **kwargs)

    def container(self, **kwargs: Any) -> Container:
        return self.page.container(_target=self, **kwargs)

    def card(self, **kwargs: Any) -> Container:
        return self.page.card(_target=self, **kwargs)

    def __getattr__(self, name: str) -> Any:
        method = getattr(self.page, name)
        if not callable(method):
            raise AttributeError(name)

        def forward(*args: Any, **kwargs: Any) -> Any:
            previous = self.page._explicit_target
            self.page._explicit_target = self
            try:
                return method(*args, **kwargs)
            finally:
                self.page._explicit_target = previous

        return forward


class FilterScope(Container):
    def __init__(self, page: Page, *, name: str | None = None) -> None:
        super().__init__(page, "filters", {"name": name})


class Page:
    """Base class for Edron request-scoped page controllers."""

    def __init__(self) -> None:
        # Action handlers still receive a fresh controller instance so their
        # application method can use the same dependency attributes. Output
        # methods independently remain page/fragment-only via ``require_frame``.
        self._frame = require_frame("page", "fragment", "action")
        self._container_stack: list[Container] = []
        self._explicit_target: Container | None = None
        self._sidebar: Container | None = None

    @property
    def sidebar(self) -> Container:
        if self._sidebar is None:
            self._sidebar = Container(self, "sidebar")
            self._append(self._sidebar)
        return self._sidebar

    def _append(self, value: Any, *, _target: Container | None = None) -> None:
        target = (
            _target
            or self._explicit_target
            or (self._container_stack[-1] if self._container_stack else None)
        )
        if target is None:
            self._frame.buffer.append(value)
        else:
            target._append(value)

    def _native(self, name: str, *args: Any, **kwargs: Any) -> Any:
        return getattr(hedron, name)(*args, **kwargs)

    def include(self, *nodes: Any) -> None:
        for node in nodes:
            self._append(node)

    def __call__(self, *nodes: Any) -> None:
        self.include(*nodes)

    def heading(self, text: str, *, level: int = 2) -> None:
        self._append(self._native("Heading", text, level=level))

    def subheader(self, text: str) -> None:
        self.heading(text, level=3)

    def text(self, text: str, *, _target: Container | None = None) -> None:
        self._append(self._native("Text", str(text)), _target=_target)

    def caption(self, text: str) -> None:
        self._append(self._native("Text", str(text), as_="small"))

    def markdown(self, source: str) -> None:
        self._append(self._native("Markdown", source))

    def code(self, source: str, *, language: str | None = None) -> None:
        self._append(self._native("CodeBlock", source, language=language))

    def divider(self) -> None:
        self._append(self._native("Divider"))

    def _status(self, message: str, tone: str) -> None:
        self._append(self._native("Status", message, tone=tone))

    def success(self, message: str) -> None:
        self._status(message, "success")

    def info(self, message: str) -> None:
        self._status(message, "info")

    def warning(self, message: str) -> None:
        self._status(message, "warning")

    def error(self, message: str) -> None:
        self._status(message, "danger")

    def empty(self, message: str = "") -> None:
        self._status(message, "info")

    def metric(
        self, label: str, value: Any, *, delta: Any = None, delta_tone: str = "neutral"
    ) -> None:
        self._append(self._native("Metric", label, value, delta=delta, delta_tone=delta_tone))

    def table(self, data: Any, *, caption: str | None = None) -> None:
        try:
            from hedron_data import DataTable

            node = DataTable(data, caption=caption)
        except (ImportError, TypeError, ValueError):
            rows = list(data) if data is not None else []
            headers = list(rows[0].keys()) if rows and isinstance(rows[0], Mapping) else None
            values = [tuple(row.get(key) for key in headers) for row in rows] if headers else rows
            node = self._native("Table", headers=headers, rows=values, caption=caption)
        self._append(node)

    dataframe = table

    def data_workspace(
        self,
        workspace: Any,
        *,
        request: Any = None,
        editable: bool = False,
        selection: Any = None,
        caption: str | None = None,
        save_endpoint: str | None = None,
        save_mode: Literal["batch", "row", "cell"] = "batch",
        _target: Container | None = None,
    ) -> Any:
        """Render one bounded Edron workspace page and return its safe page value.

        When ``request`` is omitted, ordinary query parameters are parsed through
        the workspace allowlists.  ``editable=True`` lowers to the native data
        editor; otherwise this lowers to its native accessible table.
        """
        from edron.data import DataWorkspace, PageRequest

        if not isinstance(workspace, DataWorkspace):
            raise TypeError("data_workspace expects edron.DataWorkspace")
        if request is None:
            native_request = self._frame.request
            query = (
                getattr(native_request, "query_params", {}) if native_request is not None else {}
            )
            request = workspace.request_from(query)
        if not isinstance(request, PageRequest):
            raise TypeError("request must be edron.PageRequest")
        page = workspace.page(request, selection=selection)
        if editable:
            node = workspace.editor(
                page,
                caption=caption,
                save_endpoint=save_endpoint,
                save_mode=save_mode,
            )
        else:
            node = workspace.table(page, caption=caption)
        self._append(node, _target=_target)
        return page

    def data_editor(self, workspace: Any, **kwargs: Any) -> Any:
        """Editable spelling of :meth:`data_workspace`."""
        kwargs["editable"] = True
        return self.data_workspace(workspace, **kwargs)

    def chart(
        self,
        spec: Any,
        *,
        alternative: str | None = None,
        _target: Container | None = None,
    ) -> None:
        """Render a reviewed native ``hedron-charts`` specification.

        ``Chart`` owns compilation, payload limits, sanitization, and its
        accessible static/table fallback. Edron only places the native node
        in the request-local output buffer.
        """
        from hedron_charts import Chart

        node = spec if isinstance(spec, Chart) else Chart(spec=spec)
        self._append(node, _target=_target)
        if alternative is not None:
            if not isinstance(alternative, str) or not alternative.strip():
                raise ValueError("chart alternative must be a non-empty string")
            self._append(
                self._native("Text", alternative, as_="small", class_="edron-visual-alternative"),
                _target=_target,
            )

    def _chart(
        self,
        kind: str,
        data: Any,
        *,
        x: str,
        y: str | Sequence[str],
        title: str | None,
        description: str | None,
        color: str | None = None,
    ) -> None:
        from hedron_charts import chart_from_beginner

        ys = [y] if isinstance(y, str) else list(y)
        for field_name in ys:
            self._append(
                chart_from_beginner(
                    kind=kind,
                    data=list(data),
                    x=x,
                    y=field_name,
                    title=title or f"{field_name} by {x}",
                    description=description or f"{field_name} by {x}",
                    color=color,
                )
            )

    def line_chart(
        self,
        data: Any,
        *,
        x: str,
        y: str | Sequence[str],
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        self._chart("line", data, x=x, y=y, title=title, description=description)

    def area_chart(
        self,
        data: Any,
        *,
        x: str,
        y: str | Sequence[str],
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        self._chart("area", data, x=x, y=y, title=title, description=description)

    def bar_chart(
        self,
        data: Any,
        *,
        x: str,
        y: str | Sequence[str],
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        self._chart("bar", data, x=x, y=y, title=title, description=description)

    def scatter_chart(
        self,
        data: Any,
        *,
        x: str,
        y: str,
        color: str | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        self._chart("scatter", data, x=x, y=y, title=title, description=description, color=color)

    def plotly_chart(self, figure: Any, *, description: str | None = None) -> None:
        from hedron_charts import compile_figure

        adapter, output = compile_figure(figure, title="Plotly chart", description=description)
        self._append(adapter.render_node(output))

    def altair_chart(self, chart: Any, *, description: str | None = None) -> None:
        from hedron_charts import compile_figure

        adapter, output = compile_figure(chart, title="Altair chart", description=description)
        self._append(adapter.render_node(output))

    def matplotlib_chart(self, figure: Any, *, description: str | None = None) -> None:
        from hedron_charts import compile_figure

        adapter, output = compile_figure(figure, title="Matplotlib chart", description=description)
        self._append(adapter.render_node(output))

    def map(
        self,
        spec: Any = None,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        zoom: float = 2.0,
        title: str = "Map",
        description: str = "Geographic map",
        alternative: str | None = None,
        _target: Container | None = None,
        **kwargs: Any,
    ) -> None:
        from hedron_maps import Map

        self._append(
            Map(spec, center=center, zoom=zoom, title=title, description=description, **kwargs),
            _target=_target,
        )
        if alternative is not None:
            if not isinstance(alternative, str) or not alternative.strip():
                raise ValueError("map alternative must be a non-empty string")
            self._append(
                self._native("Text", alternative, as_="small", class_="edron-visual-alternative"),
                _target=_target,
            )

    def image(
        self,
        src: Any,
        *,
        alt: str,
        width: int | None = None,
        height: int | None = None,
        allow_external: bool = False,
        _target: Container | None = None,
    ) -> None:
        """Render a native safe image with required alternative text."""
        if not isinstance(alt, str) or not alt.strip():
            raise ValueError("image alt must be a non-empty string")
        self._append(
            self._native(
                "Image",
                src,
                alt=alt,
                width=width,
                height=height,
                allow_external=allow_external,
            ),
            _target=_target,
        )

    def audio(
        self,
        src: Any,
        *,
        tracks: Sequence[Any] = (),
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = False,
        preload: str | None = None,
        allow_external: bool = False,
        _target: Container | None = None,
    ) -> None:
        """Render native audio with validated caption/transcript tracks."""
        self._append(
            self._native(
                "Audio",
                src,
                tracks=tracks,
                controls=controls,
                autoplay=autoplay,
                loop=loop,
                muted=muted,
                preload=preload,
                allow_external=allow_external,
            ),
            _target=_target,
        )

    def video(
        self,
        src: Any,
        *,
        tracks: Sequence[Any] = (),
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = False,
        preload: str | None = None,
        poster: Any = None,
        allow_external: bool = False,
        _target: Container | None = None,
    ) -> None:
        """Render native video with a safe poster and caption tracks."""
        self._append(
            self._native(
                "Video",
                src,
                tracks=tracks,
                controls=controls,
                autoplay=autoplay,
                loop=loop,
                muted=muted,
                preload=preload,
                poster=poster,
                allow_external=allow_external,
            ),
            _target=_target,
        )

    def _request_value(self, name: str, default: Any) -> Any:
        request = self._frame.request
        if request is None:
            return default
        query = getattr(request, "query_params", {})
        return query.get(name, default)

    @staticmethod
    def _options(options: Sequence[Any]) -> list[tuple[str, Any]]:
        result = []
        for item in options:
            if isinstance(item, (tuple, list)) and len(item) == 2:
                result.append((str(item[0]), item[1]))
            else:
                result.append((str(item), item))
        return result

    def _labelled(self, label: str, control: Any, *, target: Container | None) -> None:
        self._append(
            self._native(
                "Stack", self._native("Text", label, as_="strong"), control, gap="0.25rem"
            ),
            _target=target,
        )

    def text_input(
        self,
        label: str,
        *,
        name: str,
        default: str = "",
        placeholder: str | None = None,
        required: bool = False,
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> str:
        value = str(self._request_value(name, default))
        control = self._native(
            "TextInput",
            name,
            value=value,
            placeholder=placeholder,
            required=required,
            disabled=disabled,
        )
        self._labelled(label, control, target=_target)
        return value

    def number_input(
        self,
        label: str,
        *,
        name: str,
        default: int | float | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        step: int | float | None = None,
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> int | float | None:
        raw = self._request_value(name, default)
        value: int | float | None = default
        if raw not in (None, ""):
            try:
                value = (
                    float(raw)
                    if any(
                        isinstance(x, float)
                        for x in (default, min_value, max_value, step)
                        if x is not None
                    )
                    else int(raw)
                )
            except (TypeError, ValueError) as exc:
                raise BindingError(
                    f"invalid number for {name}", code="EDRON_INPUT_INVALID"
                ) from exc
        if (
            value is not None
            and min_value is not None
            and value < min_value
            or value is not None
            and max_value is not None
            and value > max_value
        ):
            raise BindingError(
                f"number for {name} is outside its bounds", code="EDRON_INPUT_BOUNDS"
            )
        control = self._native(
            "NumberInput",
            name,
            value=value,
            min=min_value,
            max=max_value,
            step=step,
            disabled=disabled,
        )
        self._labelled(label, control, target=_target)
        return value

    def selectbox(
        self,
        label: str,
        options: Sequence[Any],
        *,
        name: str,
        default: Any = None,
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> Any:
        pairs = self._options(options)
        default = pairs[0][1] if default is None and pairs else default
        raw = self._request_value(name, default)
        value = next(
            (item for text, item in pairs if str(item) == str(raw) or text == raw), default
        )
        if pairs and value not in [item for _, item in pairs]:
            raise BindingError(f"invalid option for {name}", code="EDRON_INPUT_OPTION")
        control = self._native(
            "Select",
            name,
            [(text, str(item)) for text, item in pairs],
            value=None if value is None else str(value),
        )
        self._labelled(label, control, target=_target)
        return value

    def multiselect(
        self,
        label: str,
        options: Sequence[Any],
        *,
        name: str,
        default: Sequence[Any] = (),
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> list[Any]:
        pairs = self._options(options)
        raw = self._request_value(name, None)
        values = list(default) if raw is None else ([raw] if isinstance(raw, str) else list(raw))
        resolved = [item for _, item in pairs if any(str(item) == str(value) for value in values)]
        control = self._native(
            "MultiSelect",
            name,
            [(text, str(item)) for text, item in pairs],
            values=[str(item) for item in resolved],
            disabled=disabled,
        )
        self._labelled(label, control, target=_target)
        return resolved

    def slider(
        self,
        label: str,
        *,
        name: str,
        min_value: int | float = 0,
        max_value: int | float = 100,
        value: int | float | None = None,
        step: int | float = 1,
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> int | float:
        default = min_value if value is None else value
        number = self.number_input(
            label,
            name=name,
            default=default,
            min_value=min_value,
            max_value=max_value,
            step=step,
            disabled=disabled,
            updates=updates,
            _target=_target,
        )
        return default if number is None else number

    def checkbox(
        self,
        label: str,
        *,
        name: str,
        default: bool = False,
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> bool:
        raw = self._request_value(name, default)
        value = raw if isinstance(raw, bool) else str(raw).lower() in {"1", "true", "yes", "on"}
        self._labelled(
            label,
            self._native("Checkbox", name, label, checked=value, disabled=disabled),
            target=_target,
        )
        return value

    def date_input(
        self,
        label: str,
        *,
        name: str,
        default: date | None = None,
        disabled: bool = False,
        updates: Any = None,
        _target: Container | None = None,
    ) -> date | None:
        raw = self._request_value(name, default.isoformat() if default else None)
        value = default
        if raw not in (None, ""):
            try:
                value = raw if isinstance(raw, date) else date.fromisoformat(str(raw))
            except ValueError as exc:
                raise BindingError(f"invalid date for {name}", code="EDRON_INPUT_INVALID") from exc
        self._labelled(
            label,
            self._native(
                "DateInput", name, value=value.isoformat() if value else "", disabled=disabled
            ),
            target=_target,
        )
        return value

    def filters(self, *, name: str | None = None) -> FilterScope:
        scope = FilterScope(self, name=name)
        self._append(scope)
        return scope

    def card(self, *, _target: Container | None = None, **kwargs: Any) -> Container:
        container = Container(self, "card", kwargs)
        self._append(container, _target=_target)
        return container

    def container(self, *, border: bool = False, _target: Container | None = None) -> Container:
        container = Container(self, "stack", {"class_": "edron-container" if border else None})
        self._append(container, _target=_target)
        return container

    def columns(
        self,
        spec: int | Sequence[int | float] = 2,
        *,
        gap: str = "md",
        vertical_alignment: str = "top",
        _target: Container | None = None,
    ) -> tuple[Container, ...]:
        count = spec if isinstance(spec, int) else len(spec)
        parent = Container(
            self,
            "grid",
            {
                "columns": count,
                "gap": {"sm": "0.5rem", "md": "1rem", "lg": "1.5rem"}.get(gap, gap),
                "vertical_alignment": vertical_alignment,
            },
        )
        self._append(parent, _target=_target)
        children = tuple(Container(self, "stack") for _ in range(count))
        parent.children.extend(children)
        return children

    def tabs(self, labels: Sequence[str]) -> tuple[Container, ...]:
        parent = Container(self, "tabs", {"labels": tuple(labels)})
        self._append(parent)
        children = tuple(Container(self, "stack") for _ in labels)
        parent.children.extend(children)
        return children

    def expander(
        self, title: str, *, expanded: bool = False, open: bool | None = None, **kwargs: Any
    ) -> Container:
        container = Container(
            self, "expander", {"title": title, "open": expanded if open is None else open, **kwargs}
        )
        self._append(container)
        return container

    def style_scope(self, **kwargs: Any) -> Container:
        container = Container(self, "style", kwargs)
        self._append(container)
        return container

    def button(
        self,
        label: str,
        *,
        action: Any = None,
        variant: str = "primary",
        size: Any = None,
        width: Any = None,
        confirm: Any = None,
        disabled: bool = False,
        _target: Container | None = None,
    ) -> None:
        frame = require_frame("page", "fragment")
        node = frame.app._action_button(
            label,
            action,
            variant=variant,
            size=size,
            width=width,
            confirm=confirm,
            disabled=disabled,
        )
        self._append(node, _target=_target)

    def form(
        self, model: Any = None, *, action: Any, submit_label: str = "Submit", **kwargs: Any
    ) -> None:
        frame = require_frame("page", "fragment")
        node = frame.app._action_form(action, model=model, submit_label=submit_label, **kwargs)
        self._append(node)

    def download_button(
        self,
        value: Any = None,
        *,
        label: str = "Download",
        filename: str | None = None,
        media_type: str | None = None,
        download: Any = None,
        **kwargs: Any,
    ) -> None:
        value = value if value is not None else download
        if isinstance(value, bytes):
            if not filename or not media_type:
                raise BindingError(
                    "bytes downloads require filename and media_type",
                    code="EDRON_DOWNLOAD_METADATA",
                )
            payload = base64.b64encode(value).decode("ascii")
            reference = f"data:{media_type};base64,{payload}"
        else:
            reference = getattr(value, "identifier", value)
            filename = filename or str(reference)
        if reference is None or filename is None:
            raise BindingError(
                "download_button requires a Download or bytes value",
                code="EDRON_DOWNLOAD_VALUE",
            )
        self._append(
            self._native(
                "DownloadButton",
                href=str(reference),
                filename=filename,
                label=label,
                **kwargs,
            )
        )

    def job(self, flow: Any, *, submit_label: str = "Submit", show_cancel: bool = False) -> None:
        frame = require_frame("page", "fragment")
        bundle = flow.to_bundle() if hasattr(flow, "to_bundle") else flow
        frame.app.include(bundle)
        if hasattr(bundle, "render"):
            self._append(bundle.render())

    def _resolve(self, value: Any) -> Any:
        if isinstance(value, Container):
            children = [self._resolve(child) for child in value.children]
            kind = value.kind
            if kind == "sidebar":
                return self._native("Sidebar", *children, label="Sidebar")
            if kind == "card":
                options = dict(value.options)
                variant = options.pop("variant", None)
                options.pop("recipe", None)
                if variant is not None:
                    options["appearance"] = {"outlined": "outline"}.get(variant, variant)
                return self._native("Card", *children, **options)
            if kind == "grid":
                options = dict(value.options)
                options.pop("vertical_alignment", None)
                return self._native("Grid", *children, **options)
            if kind == "tabs":
                items = list(zip(value.options["labels"], children, strict=True))
                return self._native("Tabs", items)
            if kind == "expander":
                return self._native(
                    "Expander", value.options.pop("title"), *children, **value.options
                )
            if kind == "style":
                return self._native("StyleScope", *children, **value.options)
            return self._native("Stack", *children, **value.options)
        return value

    def _resolved_output(self) -> list[Any]:
        return [self._resolve(value) for value in self._frame.buffer.entries]
