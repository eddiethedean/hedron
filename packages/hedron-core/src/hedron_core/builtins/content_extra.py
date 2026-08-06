"""Extra content built-ins: Math, HelpInspector, IFrame, Geolocation (phase 0.15)."""

from __future__ import annotations

from html import escape as html_escape
from urllib.parse import urlsplit

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, TrustedHtml, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = [
    "GeolocationButton",
    "GeolocationHint",
    "HelpInspector",
    "IFrame",
    "Math",
]

# Fully restrictive: no scripts, forms, same-origin, popups, etc.
_DEFAULT_IFRAME_SANDBOX = ""


def _is_remote_url(url: SafeUrl) -> bool:
    scheme = urlsplit(url.value).scheme.lower()
    return scheme in {"http", "https"}


def _asset_url(value: SafeUrl | str, *, allow_external: bool = False) -> SafeUrl:
    if isinstance(value, SafeUrl):
        return value
    return SafeUrl.parse(value, purpose=UrlPurpose.ASSET, allow_external=allow_external)


class MathProps(Props):
    latex: str
    display: bool = False
    class_: str | None = None
    mark: str | None = None


class Math(Component[MathProps]):
    """Accessible LaTeX/math text without executing JavaScript.

    Baseline renders escaped source inside ``<code>`` under ``.hedron-math``.
    KaTeX / MathJax remain optional progressive enhancements via pinned assets
    later; this component never injects or runs scripts.
    """

    props_type = MathProps
    logical_name = "Math"
    distribution = "hedron-core"

    def __init__(
        self,
        latex: str,
        *,
        display: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            MathProps(latex=latex, display=display, class_=class_, mark=mark, **kwargs)
        )

    def render(self) -> NodeLike:
        # Serializer escapes text; never treat latex as HTML or execute JS.
        code = html.code(self.props.latex, class_="hedron-math-source")
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names(
                "hedron-math hedron-math-display" if self.props.display else "hedron-math",
                self.props.class_,
            ),
            "data": {
                "hedron-math": "display" if self.props.display else "inline",
                **mark_data(self.props.mark),
            },
        }
        if self.props.display:
            return html.div(code, role="math", **attrs)
        return html.span(code, role="math", **attrs)


class HelpInspectorProps(ElementProps):
    title: str
    open: bool = False


class HelpInspector(Component[HelpInspectorProps]):
    """Bounded details/summary disclosure for object or help inspection."""

    props_type = HelpInspectorProps
    logical_name = "HelpInspector"
    distribution = "hedron-core"

    def __init__(
        self,
        title: str,
        body: NodeLike | str,
        *,
        open: bool = False,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            HelpInspectorProps(
                title=title,
                open=open,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._body = body

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "id": self.props.id,
            "class_": class_names("hedron-help-inspector", self.props.class_),
            "data": {
                "hedron-help-inspector": "true",
                **mark_data(self.props.mark),
            },
        }
        if self.props.open:
            attrs["open"] = True
        return html.details(
            html.summary(self.props.title),
            html.div(self._body, class_="hedron-help-inspector-body"),
            **attrs,
        )


class IFrameProps(Props):
    src: SafeUrl
    title: str
    sandbox: str = _DEFAULT_IFRAME_SANDBOX
    allow: str | None = None
    referrerpolicy: str = "no-referrer"
    width: str | int | None = None
    height: str | int | None = None
    allow_remote: bool = False
    class_: str | None = None
    mark: str | None = None


class IFrame(Component[IFrameProps]):
    """Sandboxed iframe with SafeUrl src and local-vs-remote policy.

    Default sandbox is fully restrictive (empty token list). Remote ``http(s)``
    sources require ``allow_remote=True``. ``srcdoc`` remains forbidden at the
    HTML layer; use TrustedHtml elsewhere for deliberate HTML trust boundaries.
    """

    props_type = IFrameProps
    logical_name = "IFrame"
    distribution = "hedron-core"

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        title: str,
        sandbox: str = _DEFAULT_IFRAME_SANDBOX,
        allow: str | None = None,
        referrerpolicy: str = "no-referrer",
        width: str | int | None = None,
        height: str | int | None = None,
        allow_remote: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        url = _asset_url(src, allow_external=allow_remote)
        if _is_remote_url(url) and not allow_remote:
            raise error(
                "HED-SEC-0001",
                title="Remote iframe rejected",
                explanation=(
                    f"IFrame remote http(s) sources require allow_remote=True; got {url.value!r}."
                ),
                remediation="Pass a same-origin relative SafeUrl, or set allow_remote=True.",
            )
        super().__init__(
            IFrameProps(
                src=url,
                title=title,
                sandbox=sandbox,
                allow=allow,
                referrerpolicy=referrerpolicy,
                width=width,
                height=height,
                allow_remote=allow_remote,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        # ``iframe`` is forbidden via html.*; TrustedHtml is the approved sink
        # (same pattern as PdfViewer / object).
        src = html_escape(str(self.props.src), quote=True)
        title = html_escape(self.props.title, quote=True)
        sandbox = html_escape(self.props.sandbox, quote=True)
        referrerpolicy = html_escape(self.props.referrerpolicy, quote=True)
        mode = "remote" if self.props.allow_remote else "local"
        class_value = html_escape(class_names("hedron-iframe", self.props.class_), quote=True)
        extra = ""
        if self.props.allow is not None:
            extra += f' allow="{html_escape(self.props.allow, quote=True)}"'
        if self.props.width is not None:
            extra += f' width="{html_escape(str(self.props.width), quote=True)}"'
        if self.props.height is not None:
            extra += f' height="{html_escape(str(self.props.height), quote=True)}"'
        markup = (
            f'<iframe src="{src}" title="{title}" sandbox="{sandbox}" '
            f'referrerpolicy="{referrerpolicy}" class="{class_value}" '
            f'data-hedron-iframe="{mode}"{extra}></iframe>'
        )
        wrap_attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-iframe-wrap", self.props.class_),
            "role": "region",
            "aria": {"label": self.props.title},
        }
        wrap_attrs["data"] = {
            "hedron-iframe-wrap": mode,
            **mark_data(self.props.mark),
        }
        return html.div(
            html.raw(TrustedHtml.reviewed(markup, source="hedron-core:IFrame")),
            **wrap_attrs,
        )


class GeolocationButtonProps(Props):
    label: str = "Share location"
    lat_name: str = "lat"
    lon_name: str = "lon"
    accuracy_name: str = "accuracy"
    class_: str | None = None
    mark: str | None = None


class GeolocationButton(Component[GeolocationButtonProps]):
    """Permission-gated geolocation form fields with progressive-enhancement hooks.

    Coordinates are **client-reported and spoofable**. Never treat them as an
    authorization factor. Without JS, users can still submit lat/lon manually.
    """

    props_type = GeolocationButtonProps
    logical_name = "GeolocationButton"
    distribution = "hedron-core"

    def __init__(
        self,
        *,
        label: str = "Share location",
        lat_name: str = "lat",
        lon_name: str = "lon",
        accuracy_name: str = "accuracy",
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            GeolocationButtonProps(
                label=label,
                lat_name=lat_name,
                lon_name=lon_name,
                accuracy_name=accuracy_name,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.fieldset(
            html.legend(self.props.label),
            html.p(
                "Location is spoofable and is never an authorization factor.",
                class_="hedron-geolocation-note",
                data={"hedron-geolocation-spoofable": "true"},
            ),
            html.button(
                self.props.label,
                type="button",
                class_="hedron-geolocation-request",
                data={"hedron-geolocation": "request"},
                aria={"label": self.props.label},
            ),
            html.label(
                "Latitude",
                html.input(
                    type="text",
                    name=self.props.lat_name,
                    inputmode="decimal",
                    autocomplete="off",
                    data={"hedron-geolocation-field": "lat"},
                ),
            ),
            html.label(
                "Longitude",
                html.input(
                    type="text",
                    name=self.props.lon_name,
                    inputmode="decimal",
                    autocomplete="off",
                    data={"hedron-geolocation-field": "lon"},
                ),
            ),
            html.label(
                "Accuracy (m)",
                html.input(
                    type="text",
                    name=self.props.accuracy_name,
                    inputmode="decimal",
                    autocomplete="off",
                    data={"hedron-geolocation-field": "accuracy"},
                ),
            ),
            class_=class_names("hedron-geolocation", self.props.class_),
            data={
                "hedron-geolocation": "true",
                "spoofable": "true",
                **mark_data(self.props.mark),
            },
        )


_DEFAULT_GEO_HINT = (
    "Browser geolocation is permission-gated, client-reported, and spoofable. "
    "Never use coordinates for authorization."
)


class GeolocationHintProps(Props):
    text: str = _DEFAULT_GEO_HINT
    class_: str | None = None
    mark: str | None = None


class GeolocationHint(Component[GeolocationHintProps]):
    """Static reminder that geolocation inputs are spoofable."""

    props_type = GeolocationHintProps
    logical_name = "GeolocationHint"
    distribution = "hedron-core"

    def __init__(
        self,
        text: str = _DEFAULT_GEO_HINT,
        *,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(GeolocationHintProps(text=text, class_=class_, mark=mark, **kwargs))

    def render(self) -> NodeLike:
        return html.p(
            self.props.text,
            role="note",
            class_=class_names("hedron-geolocation-hint", self.props.class_),
            data={
                "hedron-geolocation-spoofable": "true",
                **mark_data(self.props.mark),
            },
        )
