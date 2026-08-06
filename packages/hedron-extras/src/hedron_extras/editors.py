"""Calendar, signature, and typeahead extras."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html


class CalendarProps(ElementProps):
    name: str = "date"
    value: str | None = None
    min: str | None = None
    max: str | None = None


class Calendar(Component[CalendarProps]):
    props_type = CalendarProps
    logical_name = "Calendar"
    distribution = "hedron-extras"

    def __init__(
        self,
        *,
        name: str = "date",
        value: str | None = None,
        min: str | None = None,
        max: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(CalendarProps(name=name, value=value, min=min, max=max, **kwargs))

    def render(self) -> NodeLike:
        return html.div(
            html.input(
                type="date",
                name=self.props.name,
                value=self.props.value,
                min=self.props.min,
                max=self.props.max,
            ),
            class_=class_names("hedron-calendar", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-editor": "calendar",
                "http-fallback": "input-date",
            },
        )


class SignaturePadProps(ElementProps):
    name: str = "signature"
    max_bytes: int = 200_000


class SignaturePad(Component[SignaturePadProps]):
    props_type = SignaturePadProps
    logical_name = "SignaturePad"
    distribution = "hedron-extras"

    def __init__(self, *, name: str = "signature", max_bytes: int = 200_000, **kwargs: Any) -> None:
        if max_bytes < 1 or max_bytes > 2_000_000:
            raise ValueError("SignaturePad max_bytes out of bounds")
        super().__init__(SignaturePadProps(name=name, max_bytes=max_bytes, **kwargs))

    def render(self) -> NodeLike:
        return html.div(
            html.label(
                "Upload signature image",
                html.input(type="file", name=self.props.name, accept="image/png,image/jpeg"),
            ),
            html.button("Clear", type="reset"),
            class_=class_names("hedron-signature-pad", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-editor": "signature",
                "max-bytes": str(self.props.max_bytes),
                "pointer-alternative": "file-upload",
            },
        )


class TypeaheadProps(ElementProps):
    name: str
    options: list[str]
    value: str | None = None
    placeholder: str | None = None


class Typeahead(Component[TypeaheadProps]):
    props_type = TypeaheadProps
    logical_name = "Typeahead"
    distribution = "hedron-extras"

    def __init__(
        self,
        name: str,
        options: Sequence[str],
        *,
        value: str | None = None,
        placeholder: str | None = None,
        **kwargs: Any,
    ) -> None:
        if len(options) > 5_000:
            raise ValueError("Typeahead options exceed budget")
        super().__init__(
            TypeaheadProps(
                name=name,
                options=list(options),
                value=value,
                placeholder=placeholder,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        list_id = f"{self.props.name}-list"
        return html.div(
            html.input(
                type="text",
                name=self.props.name,
                value=self.props.value,
                placeholder=self.props.placeholder,
                list=list_id,
                role="combobox",
                aria={"autocomplete": "list", "expanded": "false"},
            ),
            html.datalist(
                *[html.option(o, value=o) for o in self.props.options],
                id=list_id,
            ),
            class_=class_names("hedron-typeahead", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-editor": "typeahead",
                "http-fallback": "datalist",
            },
        )
