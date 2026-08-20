"""Self-contained accessibility shell utilities (phase 0.54 / RFC-0081).

``SkipLink`` and ``RequestIndicator`` are styled entirely by the Hedron default
stylesheet so applications never author CSS for keyboard or busy affordances.
"""

from __future__ import annotations

from typing import Any

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.builtins.appearance import require_choice
from hedron_core.codes import HED_HTML_0006
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["RequestIndicator", "SkipLink"]

INDICATOR_PLACEMENTS: tuple[str, ...] = ("inline", "top", "bottom")


class SkipLinkProps(ElementProps):
    target: SafeUrl
    label: str = "Skip to main content"


class SkipLink(Component[SkipLinkProps]):
    """Keyboard-first bypass link to the shell's main panel."""

    props_type = SkipLinkProps
    logical_name = "SkipLink"

    def __init__(
        self,
        target: SafeUrl | str = "#main-panel",
        *,
        label: str = "Skip to main content",
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        if isinstance(target, str):
            if not target.startswith("#"):
                raise error(
                    HED_HTML_0006,
                    title="SkipLink target must be a same-document fragment",
                    explanation=f"target={target!r} does not start with '#'.",
                    remediation="Pass the main panel id as a fragment, e.g. '#main-panel'.",
                )
            if len(target) < 2:
                raise error(
                    HED_HTML_0006,
                    title="SkipLink target is empty",
                    explanation="target must name an element id after '#'.",
                    remediation="Pass '#main-panel' or the id given to AppShell(panel_id=...).",
                )
            url = SafeUrl.parse(target, purpose=UrlPurpose.NAVIGATION)
        else:
            url = target
        if not label.strip():
            raise error(
                HED_HTML_0006,
                title="SkipLink label is required",
                explanation="A skip link needs discernible text for screen readers.",
                remediation="Pass label='Skip to main content'.",
            )
        super().__init__(
            SkipLinkProps(
                target=url,
                label=label,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.a(
            self.props.label,
            href=self.props.target,
            id=self.props.id,
            class_=class_names("hedron-skip-link", self.props.class_),
            data={"hedron-skip-link": "true", **mark_data(self.props.mark)},
        )


class RequestIndicatorProps(ElementProps):
    label: str = "Loading…"
    placement: str = "inline"
    visible_label: bool = True


class RequestIndicator(Component[RequestIndicatorProps]):
    """HTMX request indicator with a polite live region and no application CSS.

    Reference it from HTMX controls via ``indicator='#<id>'``; the element also
    carries HTMX's ``htmx-indicator`` class so it stays hidden while idle.
    """

    props_type = RequestIndicatorProps
    logical_name = "RequestIndicator"

    def __init__(
        self,
        label: str = "Loading…",
        *,
        placement: str = "inline",
        visible_label: bool = True,
        hidden_label: bool | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: Any,
    ) -> None:
        require_choice(placement, INDICATOR_PLACEMENTS, label="placement")
        if not label.strip():
            raise error(
                HED_HTML_0006,
                title="RequestIndicator label is required",
                explanation="The busy state must be announced with text, not color alone.",
                remediation="Pass label='Loading…'.",
            )
        # ``hidden_label`` is retained as a compatibility alias for ``visible_label``.
        show_label = visible_label if hidden_label is None else not hidden_label
        super().__init__(
            RequestIndicatorProps(
                label=label,
                placement=placement,
                visible_label=show_label,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        label_class = "hedron-request-indicator-label"
        if not self.props.visible_label:
            label_class = class_names(label_class, "hedron-visually-hidden")
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-request-indicator htmx-indicator", self.props.class_),
            "role": "status",
            "aria": {"live": "polite"},
            "data": {
                "hedron-request-indicator": "true",
                "hedron-indicator-placement": self.props.placement,
                **mark_data(self.props.mark),
            },
        }
        return html.div(
            html.span(class_="hedron-request-indicator-dot", aria={"hidden": "true"}),
            html.span(self.props.label, class_=label_class),
            **attrs,
        )
