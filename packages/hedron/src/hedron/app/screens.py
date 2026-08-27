"""Advanced screen normalization helpers used by the canonical ``@app.page`` surface."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, ParamSpec, TypeAlias

from hedron_core.builtins.document import Page
from hedron_core.builtins.layout import Grid, Stack
from hedron_core.builtins.shell import AppShell, NavLink
from hedron_core.codes import HED_SCREEN_0001, HED_SCREEN_0002, HED_SCREEN_0003
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error

__all__ = [
    "PageOptions",
    "SCREEN_LAYOUTS",
    "ScreenHandle",
    "ScreenLayout",
    "ScreenResult",
    "normalize_screen_result",
    "validate_screen_registration",
]

P = ParamSpec("P")

ScreenLayout = Literal["stack", "grid", "plain"]
SCREEN_LAYOUTS: tuple[ScreenLayout, ...] = ("stack", "grid", "plain")
ScreenResult: TypeAlias = NodeLike | Sequence[NodeLike] | Page
PageOptions: TypeAlias = Mapping[str, object]


@dataclass(frozen=False)
class ScreenHandle(Generic[P]):
    """Inspectable navigable page handle for advanced page composition."""

    path: str
    name: str
    title: str
    layout: ScreenLayout
    handler: Callable[..., Any]
    shell: AppShell | None = None
    navigation: tuple[ScreenHandle[Any], ...] = ()
    page_options: Mapping[str, object] = field(default_factory=dict)
    __wrapped__: Callable[..., Any] | None = None

    @property
    def logical_id(self) -> str:
        """Stable handle id for catalogs, bundles, and refresh targeting."""
        return f"screen:{self.name}"

    def link(
        self,
        label: str | None = None,
        *,
        method: Literal["get", "post", "put", "patch", "delete"] = "get",
        target: str | None = None,
        swap: str = "innerHTML",
        select: str | None = None,
        select_oob: str | None = None,
        push_url: bool | str = False,
        disabled_elt: str | None = None,
        indicator: str | None = None,
        active: bool = False,
        external: bool = False,
        preload: str | None = None,
        leading_icon: str | None = None,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
    ) -> NodeLike:
        """Build a ``NavLink`` to this screen's path (does not bypass route dependencies)."""
        text = label if label is not None else self.title
        return NavLink(
            text,
            self.path,
            method=method,
            target=target,
            swap=swap,
            select=select,
            select_oob=select_oob,
            push_url=push_url,
            disabled_elt=disabled_elt,
            indicator=indicator,
            active=active,
            external=external,
            preload=preload,
            leading_icon=leading_icon,
            id=id,
            class_=class_,
            mark=mark,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.handler(*args, **kwargs)


def validate_screen_registration(
    *,
    path: str,
    name: str,
    title: str,
    layout: str,
    existing_paths: Mapping[str, str],
    existing_names: Mapping[str, str],
) -> ScreenLayout:
    """Validate decorator metadata before route registration."""
    if not title or not str(title).strip():
        raise error(
            HED_SCREEN_0001,
            title="Screen title is required",
            explanation="title must be an explicit non-empty string; it is not inferred.",
            remediation="Pass title=... to @app.page or return an explicit Page.",
        )
    if layout not in SCREEN_LAYOUTS:
        raise error(
            HED_SCREEN_0001,
            title="Unsupported screen layout",
            explanation=f"layout={layout!r} is outside the closed inventory.",
            remediation=f"Use one of: {', '.join(SCREEN_LAYOUTS)}.",
        )
    if path in existing_paths:
        raise error(
            HED_SCREEN_0002,
            title="Duplicate screen path",
            explanation=f"path={path!r} is already registered as {existing_paths[path]!r}.",
            remediation="Choose a distinct path or rename the existing screen.",
        )
    if name in existing_names:
        raise error(
            HED_SCREEN_0002,
            title="Duplicate screen name",
            explanation=f"name={name!r} is already registered at {existing_names[name]!r}.",
            remediation="Pass a distinct name=... or change the handler name.",
        )
    return layout  # type: ignore[return-value]


def normalize_screen_result(
    result: object,
    *,
    title: str,
    layout: ScreenLayout = "stack",
    shell: AppShell | None = None,
    navigation: Sequence[ScreenHandle[Any]] = (),
    page_options: PageOptions | None = None,
) -> Page:
    """Normalize ``NodeLike`` / bounded sequence / ``Page`` into a titled ``Page``."""
    options = dict(page_options or {})
    if inspect.isgenerator(result) or inspect.isasyncgen(result) or inspect.iscoroutine(result):
        if inspect.iscoroutine(result):
            result.close()
        raise error(
            HED_SCREEN_0003,
            title="Unsupported screen return",
            explanation="Screens cannot return generators, async generators, or bare coroutines.",
            remediation="Return a Page, a NodeLike, or a bounded sequence of nodes.",
        )
    if isinstance(result, Page):
        return _validate_explicit_page(
            result,
            title=title,
            shell=shell,
            page_options=options,
        )
    nodes = _coerce_bounded_nodes(result)
    if not nodes:
        raise error(
            HED_SCREEN_0001,
            title="Empty screen content",
            explanation="Screen handlers must return visible content or an explicit empty state.",
            remediation=(
                "Return at least one node, or an explicit Page with an empty-state component."
            ),
        )
    body: NodeLike = _apply_layout(nodes, layout=layout)
    body = _compose_shell(body, shell=shell, navigation=navigation)
    page_kwargs = dict(options)
    page_kwargs.setdefault("title", title)
    return Page(body, **page_kwargs)  # type: ignore[arg-type]


def _validate_explicit_page(
    page: Page,
    *,
    title: str,
    shell: AppShell | None,
    page_options: Mapping[str, object],
) -> Page:
    page_title = getattr(page.props, "title", None)
    if page_title is not None and str(page_title) != str(title):
        raise error(
            HED_SCREEN_0001,
            title="Conflicting Page title",
            explanation=(f"Decorator title={title!r} conflicts with Page(title={page_title!r})."),
            remediation="Match titles or omit title on the returned Page.",
        )
    if shell is not None:
        raise error(
            HED_SCREEN_0001,
            title="Conflicting screen shell",
            explanation="An explicit Page cannot be combined with decorator shell=...",
            remediation="Compose AppShell inside the Page, or omit shell= on @app.page.",
        )
    if page_options:
        conflicting = sorted(
            key
            for key, value in page_options.items()
            if key != "title"
            and getattr(page.props, key, None) not in (None, value)
            and getattr(page.props, key, None) is not None
        )
        if conflicting:
            raise error(
                HED_SCREEN_0001,
                title="Conflicting Page options",
                explanation=(
                    f"page_options conflict with returned Page on: {', '.join(conflicting)}."
                ),
                remediation="Align page_options with the Page, or return nodes instead of Page.",
            )
    if page_title is None and title:
        # Preserve escape hatch but apply required decorator title when Page omitted it.
        object.__setattr__(page, "props", page.props.model_copy(update={"title": title}))
    return page


def _coerce_bounded_nodes(result: object) -> list[NodeLike]:
    if result is None:
        return []
    if isinstance(result, (str, bytes, bytearray)):
        return [result]  # type: ignore[list-item]
    if isinstance(result, Component):
        return [result]
    if isinstance(result, Mapping):
        raise error(
            HED_SCREEN_0003,
            title="Unsupported screen return",
            explanation="Mappings are not valid screen content.",
            remediation="Return a Page, component, or a list/tuple of nodes.",
        )
    if isinstance(result, Sequence):
        try:
            items = list(result)
        except TypeError as exc:
            raise error(
                HED_SCREEN_0003,
                title="Unsupported screen return",
                explanation="Screen sequences must be bounded and materializable.",
                remediation="Return a list or tuple of nodes.",
            ) from exc
        return list(items)
    return [result]  # type: ignore[list-item]


def _apply_layout(nodes: Sequence[NodeLike], *, layout: ScreenLayout) -> NodeLike:
    if layout == "plain":
        return nodes[0] if len(nodes) == 1 else list(nodes)
    if layout == "grid":
        return Grid(*nodes)
    return Stack(*nodes)


def _compose_shell(
    body: NodeLike,
    *,
    shell: AppShell | None,
    navigation: Sequence[ScreenHandle[Any]],
) -> NodeLike:
    nav_from_handles: list[NodeLike] = [item.link() for item in navigation]
    if shell is None:
        if not nav_from_handles:
            return body
        return AppShell(nav=nav_from_handles, body=body)
    if getattr(shell, "_body", ()):
        raise error(
            HED_SCREEN_0001,
            title="Conflicting AppShell body",
            explanation=(
                "Decorator shell= already has a body; screen content cannot merge silently."
            ),
            remediation="Pass shell chrome without body, or compose the Page yourself.",
        )
    existing_nav = list(getattr(shell, "_nav", ()) or ())
    return AppShell(
        nav=existing_nav or nav_from_handles or None,
        body=body,
        banner=getattr(shell, "_banner", None),
        brand=getattr(shell, "_brand", None),
        env_badge=getattr(shell, "_env_badge", None),
        account=getattr(shell, "_account", None),
        nav_groups=getattr(shell, "_nav_groups", None) or None,
        nav_footer=getattr(shell, "_nav_footer", None),
        app_footer=getattr(shell, "_app_footer", None),
        panel_id=shell.props.panel_id,
        content_width=shell.props.content_width,
        mobile_collapse=shell.props.mobile_collapse,
        class_=shell.props.class_,
        id=shell.props.id,
    )
