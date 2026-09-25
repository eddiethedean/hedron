"""Write-only secret editing controls."""

from __future__ import annotations

from typing_extensions import override

from hedron_core.builtins._base import ElementProps, class_names, dom_id_part
from hedron_core.component import Component, NodeLike
from hedron_core.enhancements import SecretOperation
from hedron_core.html import html


class SecretFieldProps(ElementProps):
    name: str
    label: str
    configured: bool = False
    allow_clear: bool = False
    id: str | None = None


class SecretField(Component[SecretFieldProps]):
    """Password editor that never receives or renders stored plaintext."""

    props_type = SecretFieldProps
    logical_name = "SecretField"

    def __init__(
        self,
        name: str,
        label: str,
        *,
        configured: bool = False,
        allow_clear: bool = False,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            SecretFieldProps(
                name=name,
                label=label,
                configured=configured,
                allow_clear=allow_clear,
                id=id or f"secret-{dom_id_part(name)}",
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    @override
    def render(self) -> NodeLike:
        field_id = self.props.id or f"secret-{dom_id_part(self.props.name)}"
        description_id = f"{field_id}-state"
        state = "Configured" if self.props.configured else "Not configured"
        controls: list[NodeLike] = [
            html.input(
                type="password",
                name=f"{self.props.name}__replacement",
                id=field_id,
                autocomplete="new-password",
                value=None,
                aria={"describedby": description_id},
                data={"hedron-secret-operation": SecretOperation.REPLACE.value},
            ),
            html.input(
                type="hidden",
                name=f"{self.props.name}__operation",
                value=SecretOperation.KEEP.value,
                data={"hedron-secret-operation": "selector"},
            ),
        ]
        if self.props.allow_clear:
            controls.append(
                html.button(
                    "Clear",
                    type="submit",
                    name=f"{self.props.name}__clear",
                    value="1",
                    data={"hedron-secret-operation": SecretOperation.CLEAR.value},
                    aria={"label": f"Clear {self.props.label}"},
                )
            )
        data: dict[str, str | bool | int | float | None] = {
            "hedron-secret-configured": self.props.configured
        }
        if self.props.mark:
            data["hedron-mark"] = self.props.mark
        return html.div(
            html.label(self.props.label, for_=field_id),
            html.span(state, id=description_id, class_="hedron-secret-state"),
            html.div(*controls, class_="hedron-secret-controls"),
            class_=class_names("hedron-secret-field", self.props.class_),
            data=data,
        )
