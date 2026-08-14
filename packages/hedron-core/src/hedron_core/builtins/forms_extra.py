"""Typed form controls for phase 0.15 (native-HTML-first)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Literal

from hedron_core.builtins._base import (
    ElementProps,
    class_names,
    collect_children,
    dom_id_part,
    mark_data,
)
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import HtmlAttrValue


def _aria_attrs(
    *,
    describedby: str | None,
    invalid: str | None,
    required: str | None,
) -> dict[str, str | bool | int | float | None]:
    return {
        "describedby": describedby,
        "invalid": invalid,
        "required": required,
    }


class _NamedControlProps(Props):
    name: str
    id: str | None = None
    required: bool = False
    disabled: bool = False
    mark: str | None = None
    aria_describedby: str | None = None
    aria_invalid: str | None = None
    aria_required: str | None = None


class NumberInputProps(_NamedControlProps):
    value: float | int | str | None = None
    min: float | int | str | None = None
    max: float | int | str | None = None
    step: float | int | str | None = None
    placeholder: str | None = None


class NumberInput(Component[NumberInputProps]):
    props_type = NumberInputProps
    logical_name = "NumberInput"

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: float | int | str | None = None,
        min: float | int | str | None = None,
        max: float | int | str | None = None,
        step: float | int | str | None = None,
        placeholder: str | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            NumberInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                min=min,
                max=max,
                step=step,
                placeholder=placeholder,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "number",
            "name": self.props.name,
            "id": self.props.id,
            "class_": "hedron-number-input",
        }
        if self.props.value is not None:
            attrs["value"] = str(self.props.value)
        if self.props.min is not None:
            attrs["min"] = str(self.props.min)
        if self.props.max is not None:
            attrs["max"] = str(self.props.max)
        if self.props.step is not None:
            attrs["step"] = str(self.props.step)
        if self.props.placeholder:
            attrs["placeholder"] = self.props.placeholder
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.input(**attrs)


class RangeInputProps(_NamedControlProps):
    value: float | int | str | None = None
    min: float | int | str = 0
    max: float | int | str = 100
    step: float | int | str | None = 1


class RangeInput(Component[RangeInputProps]):
    props_type = RangeInputProps
    logical_name = "RangeInput"

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: float | int | str | None = None,
        min: float | int | str = 0,
        max: float | int | str = 100,
        step: float | int | str | None = 1,
        markers: Sequence[float | int | str] | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            RangeInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                min=min,
                max=max,
                step=step,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )
        self._markers = tuple(markers) if markers is not None else ()

    def render(self) -> NodeLike:
        field_id = self.props.id or f"field-{dom_id_part(self.props.name)}"
        list_id = f"{field_id}-markers" if self._markers else None
        attrs: dict[str, HtmlAttrValue] = {
            "type": "range",
            "name": self.props.name,
            "id": field_id,
            "min": str(self.props.min),
            "max": str(self.props.max),
            "class_": "hedron-range-input",
        }
        if self.props.value is not None:
            attrs["value"] = str(self.props.value)
        if self.props.step is not None:
            attrs["step"] = str(self.props.step)
        if list_id:
            attrs["list"] = list_id
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        control = html.input(**attrs)
        if not self._markers:
            return control
        options = [html.option(value=str(m), label=str(m)) for m in self._markers]
        return html.div(
            control,
            html.datalist(*options, id=list_id),
            class_="hedron-range-input-wrap",
        )


class DateInputProps(_NamedControlProps):
    value: str = ""
    min: str | None = None
    max: str | None = None


class DateInput(Component[DateInputProps]):
    props_type = DateInputProps
    logical_name = "DateInput"

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: str = "",
        min: str | None = None,
        max: str | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            DateInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                min=min,
                max=max,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "date",
            "name": self.props.name,
            "id": self.props.id,
            "value": self.props.value,
            "class_": "hedron-date-input",
        }
        if self.props.min:
            attrs["min"] = self.props.min
        if self.props.max:
            attrs["max"] = self.props.max
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.input(**attrs)


class TimeInputProps(_NamedControlProps):
    value: str = ""
    min: str | None = None
    max: str | None = None
    step: float | int | str | None = None


class TimeInput(Component[TimeInputProps]):
    props_type = TimeInputProps
    logical_name = "TimeInput"

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: str = "",
        min: str | None = None,
        max: str | None = None,
        step: float | int | str | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            TimeInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                min=min,
                max=max,
                step=step,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "time",
            "name": self.props.name,
            "id": self.props.id,
            "value": self.props.value,
            "class_": "hedron-time-input",
        }
        if self.props.min:
            attrs["min"] = self.props.min
        if self.props.max:
            attrs["max"] = self.props.max
        if self.props.step is not None:
            attrs["step"] = str(self.props.step)
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.input(**attrs)


class DateTimeInputProps(_NamedControlProps):
    value: str = ""
    min: str | None = None
    max: str | None = None
    step: float | int | str | None = None


class DateTimeInput(Component[DateTimeInputProps]):
    props_type = DateTimeInputProps
    logical_name = "DateTimeInput"

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: str = "",
        min: str | None = None,
        max: str | None = None,
        step: float | int | str | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            DateTimeInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                min=min,
                max=max,
                step=step,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "datetime-local",
            "name": self.props.name,
            "id": self.props.id,
            "value": self.props.value,
            "class_": "hedron-datetime-input",
        }
        if self.props.min:
            attrs["min"] = self.props.min
        if self.props.max:
            attrs["max"] = self.props.max
        if self.props.step is not None:
            attrs["step"] = str(self.props.step)
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.input(**attrs)


class MultiSelectProps(_NamedControlProps):
    pass


class MultiSelect(Component[MultiSelectProps]):
    props_type = MultiSelectProps
    logical_name = "MultiSelect"

    def __init__(
        self,
        name: str,
        options: Sequence[tuple[str, str]],
        *,
        id: str | None = None,
        values: Sequence[str] | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            MultiSelectProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )
        self._options = tuple(options)
        self._values = frozenset(values or ())

    def render(self) -> NodeLike:
        opts = []
        for val, label in self._options:
            attrs: dict[str, HtmlAttrValue] = {"value": val}
            if val in self._values:
                attrs["selected"] = True
            opts.append(html.option(label, **attrs))
        attrs: dict[str, HtmlAttrValue] = {
            "name": self.props.name,
            "id": self.props.id,
            "multiple": True,
            "class_": "hedron-multi-select",
        }
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.select(*opts, **attrs)


class ToggleSwitchProps(_NamedControlProps):
    label: str
    checked: bool = False


class ToggleSwitch(Component[ToggleSwitchProps]):
    props_type = ToggleSwitchProps
    logical_name = "ToggleSwitch"

    def __init__(
        self,
        name: str,
        label: str,
        *,
        id: str | None = None,
        checked: bool = False,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            ToggleSwitchProps(
                name=name,
                label=label,
                id=id or f"field-{dom_id_part(name)}",
                checked=checked,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "checkbox",
            "name": self.props.name,
            "id": self.props.id,
            "role": "switch",
            "class_": "hedron-switch",
        }
        if self.props.checked:
            attrs["checked"] = True
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = {
            **_aria_attrs(
                describedby=self.props.aria_describedby,
                invalid=self.props.aria_invalid,
                required=self.props.aria_required,
            ),
            "checked": "true" if self.props.checked else "false",
        }
        wrap: dict[str, HtmlAttrValue] = {"class_": "hedron-toggle-switch"}
        data = mark_data(self.props.mark)
        if data:
            wrap["data"] = data
        return html.div(
            html.input(**attrs),
            html.label(self.props.label, for_=self.props.id),
            **wrap,
        )


class SegmentedControlProps(ElementProps):
    name: str
    legend: str
    required: bool = False
    variant: Literal["segmented", "pills"] = "segmented"


class SegmentedControl(Component[SegmentedControlProps]):
    props_type = SegmentedControlProps
    logical_name = "SegmentedControl"

    def __init__(
        self,
        name: str,
        legend: str,
        options: Sequence[tuple[str, str]],
        *,
        id: str | None = None,
        value: str | None = None,
        required: bool = False,
        variant: Literal["segmented", "pills"] = "segmented",
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            SegmentedControlProps(
                name=name,
                legend=legend,
                id=id,
                required=required,
                variant=variant,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._options = tuple(options)
        self._value = value

    def render(self) -> NodeLike:
        group_id = self.props.id or (
            f"field-{dom_id_part(self.props.name)}-{self.render_instance_id()[2:10]}"
        )
        base = "hedron-pills" if self.props.variant == "pills" else "hedron-segmented-control"
        inputs: list[NodeLike] = []
        for index, (val, label) in enumerate(self._options):
            fid = f"{group_id}-{index}"
            attrs: dict[str, HtmlAttrValue] = {
                "type": "radio",
                "name": self.props.name,
                "id": fid,
                "value": val,
            }
            if self._value == val:
                attrs["checked"] = True
            if self.props.required:
                attrs["required"] = True
            inputs.append(
                html.div(
                    html.input(**attrs),
                    html.label(label, for_=fid),
                    class_="hedron-segment",
                )
            )
        attrs: dict[str, HtmlAttrValue] = {
            "id": group_id,
            "class_": class_names(base, self.props.class_),
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.fieldset(html.legend(self.props.legend), *inputs, **attrs)


class Pills(SegmentedControl):
    """Radio group styled as pill selection (fieldset + radios)."""

    logical_name = "Pills"

    def __init__(
        self,
        name: str,
        legend: str,
        options: Sequence[tuple[str, str]],
        *,
        id: str | None = None,
        value: str | None = None,
        required: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            name,
            legend,
            options,
            id=id,
            value=value,
            required=required,
            variant="pills",
            class_=class_,
            mark=mark,
            **kwargs,
        )


class ColorInputProps(_NamedControlProps):
    value: str = "#000000"


class ColorInput(Component[ColorInputProps]):
    props_type = ColorInputProps
    logical_name = "ColorInput"

    def __init__(
        self,
        name: str,
        *,
        id: str | None = None,
        value: str = "#000000",
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            ColorInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                value=value,
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "color",
            "name": self.props.name,
            "id": self.props.id,
            "value": self.props.value,
            "class_": "hedron-color-input",
        }
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        attrs["aria"] = _aria_attrs(
            describedby=self.props.aria_describedby,
            invalid=self.props.aria_invalid,
            required=self.props.aria_required,
        )
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.input(**attrs)


class RatingInputProps(ElementProps):
    name: str
    legend: str
    maximum: int = 5
    required: bool = False


class RatingInput(Component[RatingInputProps]):
    props_type = RatingInputProps
    logical_name = "RatingInput"

    def __init__(
        self,
        name: str,
        legend: str,
        *,
        maximum: int = 5,
        value: int | None = None,
        id: str | None = None,
        required: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        if maximum < 1:
            raise ValueError("RatingInput maximum must be >= 1")
        super().__init__(
            RatingInputProps(
                name=name,
                legend=legend,
                maximum=maximum,
                id=id,
                required=required,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._value = value

    def render(self) -> NodeLike:
        group_id = self.props.id or (
            f"field-{dom_id_part(self.props.name)}-{self.render_instance_id()[2:10]}"
        )
        inputs: list[NodeLike] = []
        for score in range(1, self.props.maximum + 1):
            fid = f"{group_id}-{score}"
            label = f"{score} of {self.props.maximum}"
            attrs: dict[str, HtmlAttrValue] = {
                "type": "radio",
                "name": self.props.name,
                "id": fid,
                "value": str(score),
            }
            if self._value == score:
                attrs["checked"] = True
            if self.props.required:
                attrs["required"] = True
            inputs.append(
                html.div(
                    html.input(**attrs),
                    html.label(label, for_=fid),
                    class_="hedron-rating-option",
                )
            )
        attrs: dict[str, HtmlAttrValue] = {
            "id": group_id,
            "class_": class_names("hedron-rating-input", self.props.class_),
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.fieldset(html.legend(self.props.legend), *inputs, **attrs)


class ChipInputProps(ElementProps):
    name: str
    placeholder: str | None = None
    disabled: bool = False


class ChipInput(Component[ChipInputProps]):
    """Text entry plus multivalue hidden/list chips submitted under ``name``."""

    props_type = ChipInputProps
    logical_name = "ChipInput"

    def __init__(
        self,
        name: str,
        *,
        values: Sequence[str] | None = None,
        id: str | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            ChipInputProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                placeholder=placeholder,
                disabled=disabled,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._values = tuple(values or ())

    def render(self) -> NodeLike:
        chips: list[NodeLike] = []
        for index, value in enumerate(self._values):
            chips.append(
                html.li(
                    html.input(
                        type="hidden",
                        name=self.props.name,
                        value=value,
                        id=f"{self.props.id}-chip-{index}",
                    ),
                    html.span(value, class_="hedron-chip-label"),
                    class_="hedron-chip",
                )
            )
        entry_attrs: dict[str, HtmlAttrValue] = {
            "type": "text",
            "name": f"{self.props.name}__entry",
            "id": self.props.id,
            "class_": "hedron-chip-entry",
            "aria": {"label": "Add chip"},
        }
        if self.props.placeholder:
            entry_attrs["placeholder"] = self.props.placeholder
        if self.props.disabled:
            entry_attrs["disabled"] = True
        parts: list[NodeLike] = []
        if chips:
            parts.append(html.ul(*chips, class_="hedron-chip-list"))
        parts.append(html.input(**entry_attrs))
        attrs: dict[str, HtmlAttrValue] = {
            "id": f"{self.props.id}-wrap",
            "class_": class_names("hedron-chip-input", self.props.class_),
            "data": {"hedron-chip-name": self.props.name, **mark_data(self.props.mark)},
        }
        return html.div(*parts, **attrs)


class MenuButtonProps(ElementProps):
    label: str


class MenuButton(Component[MenuButtonProps]):
    """Button that reveals a popover/menu of link or action children."""

    props_type = MenuButtonProps
    logical_name = "MenuButton"

    def __init__(
        self,
        label: str,
        *nodes: NodeLike,
        children: NodeLike = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(MenuButtonProps(label=label, id=id, class_=class_, mark=mark, **kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        menu_id = self.props.id or f"menu-{self.render_instance_id()[2:10]}"
        panel_id = f"{menu_id}-panel"
        data = mark_data(self.props.mark)
        wrap_attrs: dict[str, HtmlAttrValue] = {
            "id": menu_id,
            "class_": class_names("hedron-menu-button", self.props.class_),
        }
        if data:
            wrap_attrs["data"] = data
        return html.div(
            html.button(
                self.props.label,
                type="button",
                popovertarget=panel_id,
                popovertargetaction="toggle",
                class_="hedron-menu-button-trigger",
                aria={"haspopup": "menu", "controls": panel_id},
            ),
            html.menu(
                *self._children,
                id=panel_id,
                popover="auto",
                class_="hedron-menu-button-panel",
            ),
            **wrap_attrs,
        )


class SelectSliderProps(_NamedControlProps):
    pass


class SelectSlider(Component[SelectSliderProps]):
    """Discrete range control with datalist markers (select-slider semantics)."""

    props_type = SelectSliderProps
    logical_name = "SelectSlider"

    def __init__(
        self,
        name: str,
        options: Sequence[str | tuple[str, str]],
        *,
        id: str | None = None,
        value: str | None = None,
        required: bool = False,
        disabled: bool = False,
        mark: str | None = None,
        aria_describedby: str | None = None,
        aria_invalid: str | None = None,
        aria_required: str | None = None,
        **kwargs: object,
    ) -> None:
        if not options:
            raise ValueError("SelectSlider requires at least one option")
        super().__init__(
            SelectSliderProps(
                name=name,
                id=id or f"field-{dom_id_part(name)}",
                required=required,
                disabled=disabled,
                mark=mark,
                aria_describedby=aria_describedby,
                aria_invalid=aria_invalid,
                aria_required=aria_required,
                **kwargs,
            )
        )
        normalized: list[tuple[str, str]] = []
        for item in options:
            if isinstance(item, tuple):
                normalized.append((str(item[0]), str(item[1])))
            else:
                normalized.append((str(item), str(item)))
        self._options = tuple(normalized)
        self._value = value

    def render(self) -> NodeLike:
        values = [v for v, _ in self._options]
        index = 0
        if self._value is not None and self._value in values:
            index = values.index(self._value)
        # Reuse RangeInput markers pattern with discrete indices mapped via datalist labels.
        field_id = self.props.id or f"field-{dom_id_part(self.props.name)}"
        list_id = f"{field_id}-markers"
        selected_value = values[index] if values else ""
        attrs: dict[str, HtmlAttrValue] = {
            "type": "range",
            "id": field_id,
            "min": "0",
            "max": str(max(len(self._options) - 1, 0)),
            "step": "1",
            "value": str(index),
            "list": list_id,
            "class_": "hedron-select-slider",
            "aria": _aria_attrs(
                describedby=self.props.aria_describedby,
                invalid=self.props.aria_invalid,
                required=self.props.aria_required,
            ),
        }
        if self.props.required:
            attrs["required"] = True
        if self.props.disabled:
            attrs["disabled"] = True
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        options = [html.option(label, value=str(i)) for i, (_v, label) in enumerate(self._options)]
        return html.div(
            html.input(**attrs),
            html.input(
                type="hidden",
                name=self.props.name,
                value=selected_value,
                id=f"{field_id}-value",
            ),
            html.datalist(*options, id=list_id),
            class_="hedron-select-slider-wrap",
            data={"hedron-select-slider": "true"},
        )


class DirectoryUploadProps(ElementProps):
    name: str = "files"
    label: str = "Upload directory"
    accept: str | None = None
    disabled: bool = False


class DirectoryUpload(Component[DirectoryUploadProps]):
    """File input with ``webkitdirectory`` for directory selection."""

    props_type = DirectoryUploadProps
    logical_name = "DirectoryUpload"

    def __init__(
        self,
        *,
        name: str = "files",
        label: str = "Upload directory",
        accept: str | None = None,
        id: str | None = None,
        disabled: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            DirectoryUploadProps(
                name=name,
                label=label,
                accept=accept,
                id=id or f"field-{dom_id_part(name)}",
                disabled=disabled,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "type": "file",
            "name": self.props.name,
            "id": self.props.id,
            "webkitdirectory": True,
            "multiple": True,
            "aria": {"label": self.props.label},
            "data": {"hedron-directory-upload": "true", **mark_data(self.props.mark)},
        }
        if self.props.accept:
            attrs["accept"] = self.props.accept
        if self.props.disabled:
            attrs["disabled"] = True
        return html.label(
            self.props.label,
            html.input(**attrs),
            class_=class_names("hedron-directory-upload", self.props.class_),
            for_=self.props.id,
        )


@dataclass(frozen=True, slots=True)
class DirectoryUploadFile:
    """Normalized directory-upload entry for server-side validation."""

    name: str
    size: int


def _as_upload_file(
    item: DirectoryUploadFile | tuple[str, int] | Mapping[str, object],
) -> DirectoryUploadFile:
    if isinstance(item, DirectoryUploadFile):
        return item
    if isinstance(item, tuple) and len(item) == 2:
        return DirectoryUploadFile(name=str(item[0]), size=int(item[1]))
    if isinstance(item, Mapping):
        return DirectoryUploadFile(name=str(item["name"]), size=int(item["size"]))  # type: ignore[index]
    raise TypeError(f"Unsupported directory upload entry: {type(item)!r}")


def _reject_traversal(path: str) -> None:
    from urllib.parse import unquote

    if "\x00" in path:
        raise ValueError(f"Unsafe directory upload path: {path!r}")
    raw = path.replace("\\", "/")
    if "\x00" in raw:
        raise ValueError(f"Unsafe directory upload path: {path!r}")
    if not raw or raw.strip() != raw:
        raise ValueError(f"Unsafe directory upload path: {path!r}")
    if raw.startswith("/") or (len(raw) > 1 and raw[1] == ":"):
        raise ValueError(f"Absolute directory upload paths are not allowed: {path!r}")

    decoded = raw
    for _ in range(3):
        next_decoded = unquote(decoded)
        if next_decoded == decoded:
            break
        decoded = next_decoded
        if "\\" in decoded or any(ord(ch) < 32 for ch in decoded):
            raise ValueError(f"Unsafe directory upload path: {path!r}")
        if decoded.startswith("/") or (len(decoded) > 1 and decoded[1] == ":"):
            raise ValueError(f"Absolute directory upload paths are not allowed: {path!r}")

    for candidate in (raw, decoded):
        lowered = candidate.lower()
        if "%2e%2e" in lowered or "%2e." in lowered or ".%2e" in lowered:
            raise ValueError(f"Directory upload path traversal rejected: {path!r}")
        normalized = candidate.replace(";", "/")
        parts = [p for p in normalized.split("/") if p not in {"", "."}]
        if any(part == ".." or part.startswith("..") for part in parts):
            raise ValueError(f"Directory upload path traversal rejected: {path!r}")
        if any(part == "" for part in PurePosixPath(candidate.replace(";", "/")).parts):
            raise ValueError(f"Unsafe directory upload path: {path!r}")


def validate_directory_upload(
    files: Sequence[DirectoryUploadFile | tuple[str, int] | Mapping[str, object]],
    *,
    max_files: int,
    max_total_size: int,
) -> tuple[DirectoryUploadFile, ...]:
    """Validate directory upload names, counts, and total size (server-side)."""
    if max_files < 0:
        raise ValueError("max_files must be >= 0")
    if max_total_size < 0:
        raise ValueError("max_total_size must be >= 0")
    if len(files) > max_files:
        raise ValueError(f"Directory upload exceeds max_files={max_files}")
    validated: list[DirectoryUploadFile] = []
    total = 0
    for item in files:
        entry = _as_upload_file(item)
        _reject_traversal(entry.name)
        if entry.size < 0:
            raise ValueError(f"Negative file size for {entry.name!r}")
        total += entry.size
        if total > max_total_size:
            raise ValueError(f"Directory upload exceeds max_total_size={max_total_size}")
        validated.append(entry)
    return tuple(validated)
