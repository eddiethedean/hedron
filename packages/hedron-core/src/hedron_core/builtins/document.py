"""Document shell built-ins."""

from __future__ import annotations

import html as html_lib
from collections.abc import Sequence
from typing import ClassVar

from hedron_core.builtins._base import collect_children
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import HedronError, error
from hedron_core.html import html
from hedron_core.htmx_extensions import parse_htmx_extensions
from hedron_core.models import Props
from hedron_core.security import SafeUrl, TrustedHtml, UrlPurpose, reject_asset_path_traversal
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = ["Fragment", "Head", "Page", "PageProps", "Title"]


def _runtime_object(value: object) -> object:
    """Preserve validation for callers that bypass static type checking."""
    return value


def _validate_page_script(url: SafeUrl) -> SafeUrl:
    if url.purpose is not UrlPurpose.ASSET:
        raise error(
            "HED-SEC-0001",
            title="Page script requires ASSET purpose",
            explanation=f"Got purpose={url.purpose.value!r}.",
            remediation="Use SafeUrl.parse(path, purpose=UrlPurpose.ASSET).",
        )
    raw = url.value
    # Same-origin relative asset paths only (no scheme, no protocol-relative).
    if raw.startswith("//") or "://" in raw:
        raise error(
            "HED-SEC-0001",
            title="Page scripts must be same-origin relative assets",
            explanation=f"Rejected script src {raw!r}.",
            remediation="Use a path like /assets/app.js under script-src 'self'.",
        )
    if not raw.startswith("/"):
        raise error(
            "HED-SEC-0001",
            title="Page scripts must be root-relative",
            explanation=f"Rejected script src {raw!r}.",
            remediation="Use a root-relative asset path beginning with '/'.",
        )
    try:
        reject_asset_path_traversal(raw, purpose=UrlPurpose.ASSET)
    except HedronError:
        raise error(
            "HED-SEC-0001",
            title="Page script path must be normalized without '..'",
            explanation=f"Rejected script src {raw!r}.",
            remediation="Use a clean root-relative asset path such as /assets/app.js.",
        ) from None
    return url


def _script_tag(url: SafeUrl, *, defer: bool = False, async_: bool = False) -> TrustedHtml:
    href = html_lib.escape(url.value, quote=True)
    attrs = ""
    if async_:
        attrs += " async"
    elif defer:
        attrs += " defer"
    return TrustedHtml.reviewed(
        f'<script src="{href}"{attrs}></script>',
        source="hedron-core:Page.scripts",
    )


class PageProps(Props):
    lang: str = "en"
    title: str | None = None
    data_theme: str | None = None
    data_hedron_theme: str | None = None
    dir: str | None = None
    script_defer: bool = True
    script_async: bool = False


class Page(Component[PageProps]):
    """Full HTML document shell."""

    props_type = PageProps
    hedron_document_shell: ClassVar[bool] = True
    slots: ClassVar[dict[str, str]] = {"head": "optional", "body": "required"}

    def __init__(
        self,
        *body: NodeLike,
        lang: str = "en",
        title: str | None = None,
        head: NodeLike = None,
        children: NodeLike = None,
        data_theme: str | None = None,
        data_hedron_theme: str | None = None,
        dir: str | None = None,
        scripts: Sequence[SafeUrl] | None = None,
        script_defer: bool = True,
        script_async: bool = False,
        htmx_extensions: object = None,
        **kwargs: object,
    ) -> None:
        if script_async and script_defer:
            raise error(
                "HED-SEC-0001",
                title="Page scripts cannot be both async and defer",
                explanation="script_async and script_defer are mutually exclusive.",
                remediation="Pass script_async=True with script_defer=False, or use defer alone.",
            )
        super().__init__(
            PageProps(
                lang=lang,
                title=title,
                data_theme=data_theme,
                data_hedron_theme=data_hedron_theme,
                dir=dir,
                script_defer=script_defer,
                script_async=script_async,
                **kwargs,
            )
        )
        self._children = collect_children(*body, children=children)
        if head is not None:
            self._slot_values["head"] = head
        validated: list[SafeUrl] = []
        for item in scripts or ():
            item_value = _runtime_object(item)
            if not isinstance(item_value, SafeUrl):
                raise TypeError("Page.scripts entries must be SafeUrl instances")
            validated.append(_validate_page_script(item_value))
        self._scripts = tuple(validated)
        self._htmx_extensions = parse_htmx_extensions(htmx_extensions)

    @property
    def htmx_extensions(self) -> object:
        return self._htmx_extensions

    def render(self) -> NodeLike:
        from hedron_core.htmx_extensions import declare_page_extensions

        declare_page_extensions(self._htmx_extensions)
        head_nodes: list[NodeLike] = [
            html.meta(charset="utf-8"),
            html.meta(name="viewport", content="width=device-width, initial-scale=1"),
        ]
        if self.props.title:
            head_nodes.append(html.title(self.props.title))
        if "head" in self._slot_values:
            head_nodes.append(self._slot_values["head"])
        html_attrs: dict[str, HtmlAttrValue] = {"lang": self.props.lang}
        if self.props.dir:
            html_attrs["dir"] = self.props.dir
        data_attrs: dict[str, str | bool | int | float | None] = {}
        if self.props.data_theme:
            data_attrs["theme"] = self.props.data_theme
        if self.props.data_hedron_theme:
            data_attrs["hedron-theme"] = self.props.data_hedron_theme
        if data_attrs:
            html_attrs["data"] = data_attrs
        body_nodes: list[NodeLike] = list(self._children)
        # Allowlisted PE scripts are TrustedHtml escapes of SafeUrl ASSET paths only —
        # free-form <script> nodes remain forbidden in the component tree.
        for url in self._scripts:
            body_nodes.append(
                html.raw(
                    _script_tag(
                        url,
                        defer=self.props.script_defer and not self.props.script_async,
                        async_=self.props.script_async,
                    )
                )
            )
        return html.html(
            html.head(*head_nodes),
            html.body(*body_nodes),
            **html_attrs,
        )


class FragmentProps(Props):
    pass


class Fragment(Component[FragmentProps]):
    props_type = FragmentProps

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(FragmentProps(**kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return list(self._children)


class HeadProps(Props):
    pass


class Head(Component[HeadProps]):
    props_type = HeadProps

    def __init__(self, *nodes: NodeLike, children: NodeLike = None, **kwargs: object) -> None:
        super().__init__(HeadProps(**kwargs))
        self._children = collect_children(*nodes, children=children)

    def render(self) -> NodeLike:
        return html.head(*self._children)


class TitleProps(Props):
    text: str


class Title(Component[TitleProps]):
    props_type = TitleProps

    def __init__(
        self,
        text: str | None = None,
        *,
        children: str | None = None,
        **kwargs: object,
    ) -> None:
        value = text if text is not None else (children or "")
        super().__init__(TitleProps(text=value, **kwargs))

    def render(self) -> NodeLike:
        return html.title(self.props.text)
