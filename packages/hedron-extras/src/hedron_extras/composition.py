"""Composition UI components for phase 0.16 extras."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Literal

from pydantic import Field, field_validator

from hedron_core.builtins._base import ElementProps, class_names, collect_children, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_extras.host import extras_host

MappingLike = Mapping[str, Any]


class ChoiceOption(Props):
    value: str
    label: str
    description: str | None = None
    disabled: bool = False


class ChoiceCardsProps(ElementProps):
    name: str
    options: list[ChoiceOption]
    selected: list[str] = Field(default_factory=list)
    multiple: bool = False
    required: bool = False


class ChoiceCards(Component[ChoiceCardsProps]):
    props_type = ChoiceCardsProps
    logical_name = "ChoiceCards"
    distribution = "hedron-extras"

    def __init__(
        self,
        name: str,
        options: Sequence[ChoiceOption | MappingLike],
        *,
        selected: Sequence[str] | None = None,
        multiple: bool = False,
        required: bool = False,
        **kwargs: Any,
    ) -> None:
        parsed = [
            opt if isinstance(opt, ChoiceOption) else ChoiceOption.model_validate(opt)
            for opt in options
        ]
        super().__init__(
            ChoiceCardsProps(
                name=name,
                options=parsed,
                selected=list(selected or []),
                multiple=multiple,
                required=required,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        input_type = "checkbox" if self.props.multiple else "radio"
        cards: list[NodeLike] = []
        for opt in self.props.options:
            checked = opt.value in self.props.selected
            input_el = html.input(
                type=input_type,
                name=self.props.name,
                value=opt.value,
                checked=checked or None,
                disabled=opt.disabled or None,
                required=(self.props.required and not self.props.multiple) or None,
            )
            body: list[NodeLike] = [html.span(opt.label, class_="hedron-choice-label")]
            if opt.description:
                body.append(html.span(opt.description, class_="hedron-choice-desc"))
            cards.append(
                html.label(
                    input_el,
                    *body,
                    class_=class_names(
                        "hedron-choice-card" + (" is-disabled" if opt.disabled else "")
                    ),
                )
            )
        return extras_host(
            "hedron-extras-composition",
            html.fieldset(
                html.legend(self.props.name),
                *cards,
                class_=class_names("hedron-choice-cards", self.props.class_),
                id=self.props.id,
                data={**mark_data(self.props.mark), "hedron-choice": "cards"},
                role="group",
            ),
            payload={"kind": "choice-cards"},
        )


class TreeNodeProps(Props):
    id: str
    label: str
    children: list[TreeNodeProps] = Field(default_factory=list)
    selectable: bool = True


class TreeViewProps(ElementProps):
    nodes: list[TreeNodeProps]
    selected: list[str] = Field(default_factory=list)
    name: str = "tree"
    source: str | None = None
    empty_message: str = "No items"
    error_message: str | None = None


class TreeView(Component[TreeViewProps]):
    props_type = TreeViewProps
    logical_name = "TreeView"
    distribution = "hedron-extras"

    def __init__(
        self,
        nodes: Sequence[TreeNodeProps | MappingLike],
        *,
        selected: Sequence[str] | None = None,
        name: str = "tree",
        source: str | None = None,
        empty_message: str = "No items",
        error_message: str | None = None,
        **kwargs: Any,
    ) -> None:
        parsed = [
            n if isinstance(n, TreeNodeProps) else TreeNodeProps.model_validate(n) for n in nodes
        ]
        if len(parsed) > 5_000:
            raise ValueError("TreeView nodes exceed budget")
        ids: list[str] = []

        def walk(items: Sequence[TreeNodeProps]) -> None:
            for item in items:
                ids.append(item.id)
                walk(item.children)

        walk(parsed)
        if len(ids) != len(set(ids)):
            raise ValueError("TreeView node ids must be stable and unique")
        super().__init__(
            TreeViewProps(
                nodes=parsed,
                selected=list(selected or []),
                name=name,
                source=source,
                empty_message=empty_message,
                error_message=error_message,
                **kwargs,
            )
        )

    def _render_node(self, node: TreeNodeProps) -> NodeLike:
        kids = [self._render_node(c) for c in node.children]
        label_parts: list[NodeLike] = []
        if node.selectable:
            label_parts.append(
                html.input(
                    type="checkbox",
                    name=self.props.name,
                    value=node.id,
                    checked=(node.id in self.props.selected) or None,
                )
            )
        label_parts.append(html.span(node.label))
        return html.li(
            html.label(*label_parts),
            *([html.ul(*kids)] if kids else []),
            data={"tree-id": node.id},
        )

    def render(self) -> NodeLike:
        if self.props.error_message:
            body: NodeLike = html.div(
                html.p(self.props.error_message, role="alert"),
                html.button("Retry", type="submit", name=f"{self.props.name}__retry", value="1"),
            )
        elif not self.props.nodes:
            body = html.p(self.props.empty_message)
        else:
            body = html.ul(*[self._render_node(n) for n in self.props.nodes], role="tree")
        return extras_host(
            "hedron-extras-composition",
            html.form(
                body,
                html.select(
                    html.option("(paged fallback)", value=""),
                    *[html.option(n.label, value=n.id) for n in self.props.nodes],
                    name=f"{self.props.name}__fallback",
                    aria={"label": "Tree fallback"},
                ),
                method="post",
                class_=class_names("hedron-tree-view", self.props.class_),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-tree": "true",
                    "fs-authority": "server",
                    "abortable": "true",
                    "http-fallback": "select",
                },
            ),
            payload={"kind": "tree", "source": self.props.source or "", "abortable": True},
        )


class StepsProps(ElementProps):
    steps: list[str]
    current: int = 0
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    name: str = "step"


class Steps(Component[StepsProps]):
    props_type = StepsProps
    logical_name = "Steps"
    distribution = "hedron-extras"

    def __init__(
        self,
        steps: Sequence[str],
        *,
        current: int = 0,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        name: str = "step",
        **kwargs: Any,
    ) -> None:
        if not steps:
            raise ValueError("Steps requires at least one step label")
        idx = max(0, min(int(current), len(steps) - 1))
        super().__init__(
            StepsProps(
                steps=list(steps),
                current=idx,
                orientation=orientation,
                name=name,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        items: list[NodeLike] = []
        for i, label in enumerate(self.props.steps):
            items.append(
                html.li(
                    html.button(
                        label,
                        type="submit",
                        name=self.props.name,
                        value=str(i),
                        aria={"current": "step" if i == self.props.current else None},
                    ),
                    data={"step-index": str(i)},
                )
            )
        return extras_host(
            "hedron-extras-composition",
            html.nav(
                html.form(
                    html.ol(*items),
                    method="post",
                    class_="hedron-steps-form",
                ),
                class_=class_names(
                    f"hedron-steps hedron-steps-{self.props.orientation}",
                    self.props.class_,
                ),
                id=self.props.id,
                aria={"label": "Steps"},
                data={
                    **mark_data(self.props.mark),
                    "hedron-steps": self.props.orientation,
                    "current": str(self.props.current),
                },
            ),
            payload={"kind": "steps", "current": self.props.current},
        )


class SplitPaneProps(ElementProps):
    primary_ratio: float = 0.5
    min_ratio: float = 0.2
    max_ratio: float = 0.8
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    persist_key: str | None = None


class SplitPane(Component[SplitPaneProps]):
    props_type = SplitPaneProps
    logical_name = "SplitPane"
    distribution = "hedron-extras"
    slots: ClassVar[dict[str, str]] = {"primary": "optional", "secondary": "optional"}

    def __init__(
        self,
        *children: NodeLike,
        primary_ratio: float = 0.5,
        min_ratio: float = 0.2,
        max_ratio: float = 0.8,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        persist_key: str | None = None,
        primary: NodeLike = None,
        secondary: NodeLike = None,
        **kwargs: Any,
    ) -> None:
        ratio = max(min_ratio, min(max_ratio, primary_ratio))
        if min_ratio > max_ratio:
            raise ValueError("SplitPane min_ratio must be <= max_ratio")
        if not 0.0 <= min_ratio <= 1.0 or not 0.0 <= max_ratio <= 1.0:
            raise ValueError("SplitPane ratios must be between 0 and 1")
        super().__init__(
            SplitPaneProps(
                primary_ratio=ratio,
                min_ratio=min_ratio,
                max_ratio=max_ratio,
                orientation=orientation,
                persist_key=persist_key,
                **kwargs,
            )
        )
        nodes = collect_children(*children)
        if primary is not None or secondary is not None:
            self._slot_primary = primary
            self._slot_secondary = secondary
        elif len(nodes) >= 2:
            self._slot_primary, self._slot_secondary = nodes[0], nodes[1]
        elif len(nodes) == 1:
            self._slot_primary, self._slot_secondary = nodes[0], None
        else:
            self._slot_primary = self._slot_secondary = None

    def render(self) -> NodeLike:
        return extras_host(
            "hedron-extras-composition",
            html.div(
                html.div(
                    self._slot_primary,
                    class_="hedron-split-primary",
                    data={"pane": "primary"},
                ),
                html.div(
                    role="separator",
                    tabindex=0,
                    aria={
                        "orientation": self.props.orientation,
                        "valuenow": int(self.props.primary_ratio * 100),
                    },
                    class_="hedron-split-handle",
                    data={"keyboard-resize": "true"},
                ),
                html.div(
                    self._slot_secondary,
                    class_="hedron-split-secondary",
                    data={"pane": "secondary"},
                ),
                class_=class_names(
                    f"hedron-split-pane hedron-split-{self.props.orientation}",
                    self.props.class_,
                ),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-split": self.props.orientation,
                    "ratio": f"{self.props.primary_ratio:.3f}",
                    "min-ratio": f"{self.props.min_ratio:.3f}",
                    "max-ratio": f"{self.props.max_ratio:.3f}",
                    "persist-key": self.props.persist_key,
                    "responsive-fallback": "stack",
                },
            ),
            payload={"kind": "split"},
        )


class FloatingActionProps(ElementProps):
    label: str
    href: SafeUrl | None = None
    action: str | None = None
    placement: Literal["bottom-right", "bottom-left", "top-right", "top-left"] = "bottom-right"


class FloatingAction(Component[FloatingActionProps]):
    props_type = FloatingActionProps
    logical_name = "FloatingAction"
    distribution = "hedron-extras"

    def __init__(
        self,
        label: str,
        *,
        href: str | None = None,
        action: str | None = None,
        placement: Literal["bottom-right", "bottom-left", "top-right", "top-left"] = "bottom-right",
        **kwargs: Any,
    ) -> None:
        if href is None and action is None:
            raise ValueError("FloatingAction requires href or action")
        super().__init__(
            FloatingActionProps(
                label=label,
                href=None if href is None else SafeUrl.parse(href, purpose=UrlPurpose.NAVIGATION),
                action=action,
                placement=placement,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        if self.props.href:
            control: NodeLike = html.a(
                self.props.label,
                href=self.props.href,
                class_="hedron-fab-control",
            )
        else:
            control = html.form(
                html.button(
                    self.props.label,
                    type="submit",
                    name="hedron_fab",
                    value=self.props.action or "",
                    class_="hedron-fab-control",
                ),
                method="post",
                class_="hedron-fab-form",
            )
        return extras_host(
            "hedron-extras-composition",
            html.div(
                control,
                class_=class_names("hedron-floating-action", self.props.class_),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-fab": self.props.placement,
                    "safe-area": "true",
                    "collision": "action-dock",
                },
            ),
            payload={"kind": "fab"},
        )


class ShortcutBinding(Props):
    keys: str
    action: str
    href: SafeUrl | None = None
    description: str = ""

    @field_validator("href", mode="before")
    @classmethod
    def _coerce_href(cls, value: Any) -> Any:
        if value is None or isinstance(value, SafeUrl):
            return value
        return SafeUrl.parse(str(value), purpose=UrlPurpose.NAVIGATION)


class KeyboardShortcutsProps(ElementProps):
    bindings: list[ShortcutBinding]
    enabled: bool = True


class KeyboardShortcuts(Component[KeyboardShortcutsProps]):
    props_type = KeyboardShortcutsProps
    logical_name = "KeyboardShortcuts"
    distribution = "hedron-extras"

    def __init__(
        self,
        bindings: Sequence[ShortcutBinding | MappingLike],
        *,
        enabled: bool = True,
        **kwargs: Any,
    ) -> None:
        parsed: list[ShortcutBinding] = []
        for raw in bindings:
            binding = (
                raw if isinstance(raw, ShortcutBinding) else ShortcutBinding.model_validate(raw)
            )
            # Re-parse to apply SafeUrl coercion when constructed with a raw str href.
            if binding.href is not None and not isinstance(binding.href, SafeUrl):
                binding = ShortcutBinding(
                    keys=binding.keys,
                    action=binding.action,
                    href=binding.href,
                    description=binding.description,
                )
            parsed.append(binding)
        # Conflict detection: duplicate key chords rejected.
        seen: set[str] = set()
        for b in parsed:
            key = b.keys.strip().lower()
            if key in seen:
                raise ValueError(f"Duplicate keyboard shortcut: {b.keys}")
            seen.add(key)
        super().__init__(KeyboardShortcutsProps(bindings=parsed, enabled=enabled, **kwargs))

    def render(self) -> NodeLike:
        items = [
            html.li(
                html.kbd(b.keys),
                " ",
                html.span(b.description or b.action),
                data={
                    "keys": b.keys,
                    "action": b.action,
                    "link": None if b.href is None else str(b.href),
                },
            )
            for b in self.props.bindings
        ]
        return extras_host(
            "hedron-extras-composition",
            html.div(
                html.ul(*items),
                class_=class_names("hedron-keyboard-shortcuts", self.props.class_),
                id=self.props.id,
                hidden=True if not self.props.enabled else None,
                data={
                    **mark_data(self.props.mark),
                    "hedron-shortcuts": "true",
                    "enabled": "1" if self.props.enabled else "0",
                    "focus-policy": "ignore-when-editable",
                },
            ),
            payload={"kind": "shortcuts"},
        )


class FocusScrollRequestProps(ElementProps):
    target_id: str
    behavior: Literal["focus", "scroll", "focus-scroll"] = "focus-scroll"


class FocusScrollRequest(Component[FocusScrollRequestProps]):
    """Declare focus/scroll by stable component identity (not CSS selectors)."""

    props_type = FocusScrollRequestProps
    logical_name = "FocusScrollRequest"
    distribution = "hedron-extras"

    def __init__(
        self,
        target_id: str,
        *,
        behavior: Literal["focus", "scroll", "focus-scroll"] = "focus-scroll",
        **kwargs: Any,
    ) -> None:
        if not target_id or target_id.startswith(".") or target_id.startswith("#"):
            raise ValueError(
                "FocusScrollRequest target_id must be a stable component id, not a selector"
            )
        super().__init__(FocusScrollRequestProps(target_id=target_id, behavior=behavior, **kwargs))

    def render(self) -> NodeLike:
        return html.div(
            class_=class_names("hedron-focus-scroll", self.props.class_),
            id=self.props.id,
            data={
                **mark_data(self.props.mark),
                "hedron-focus-target": self.props.target_id,
                "behavior": self.props.behavior,
            },
            hidden=True,
        )
