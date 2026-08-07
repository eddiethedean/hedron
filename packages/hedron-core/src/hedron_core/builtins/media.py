"""Media presentation and capture built-ins (phase 0.15)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape as html_escape
from typing import Any, Literal

from hedron_core.builtins._base import class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, TrustedHtml, UrlPurpose
from hedron_core.typing_aliases import HtmlAttrValue

__all__ = [
    "Audio",
    "CameraCapture",
    "Gallery",
    "GalleryItem",
    "Logo",
    "MicrophoneCapture",
    "PageIcon",
    "PdfViewer",
    "Video",
]


def _asset_url(value: SafeUrl | str, *, allow_external: bool = False) -> SafeUrl:
    if isinstance(value, SafeUrl):
        return value
    return SafeUrl.parse(value, purpose=UrlPurpose.ASSET, allow_external=allow_external)


def _nav_url(value: SafeUrl | str, *, allow_external: bool = False) -> SafeUrl:
    if isinstance(value, SafeUrl):
        return value
    return SafeUrl.parse(value, purpose=UrlPurpose.NAVIGATION, allow_external=allow_external)


def _track_nodes(tracks: Sequence[Mapping[str, Any] | NodeLike]) -> list[NodeLike]:
    from hedron_core.a11y.surfaces import MediaTrackContract

    nodes: list[NodeLike] = []
    for track in tracks:
        if isinstance(track, Mapping):
            kind = str(track.get("kind", "captions"))
            language = str(track.get("srclang") or track.get("language") or "")
            src_raw = track.get("src")
            src_str = None if src_raw is None else str(src_raw)
            MediaTrackContract(
                kind=kind,  # type: ignore[arg-type]
                language=language,
                src=src_str,
                reviewed=bool(track.get("reviewed", False)),
            ).validated()
            src = _asset_url(track["src"])  # type: ignore[index]
            attrs: dict[str, HtmlAttrValue] = {
                "src": src,
                "kind": kind,
            }
            if language:
                attrs["srclang"] = language
            if track.get("label"):
                attrs["label"] = str(track["label"])
            if track.get("default"):
                attrs["default"] = True
            nodes.append(html.track(**attrs))
        else:
            nodes.append(track)
    return nodes


class AudioProps(Props):
    src: SafeUrl
    controls: bool = True
    autoplay: bool = False
    loop: bool = False
    muted: bool = False
    preload: str | None = None
    class_: str | None = None
    mark: str | None = None


class Audio(Component[AudioProps]):
    """HTML ``<audio>`` with SafeUrl src and optional caption/subtitle tracks."""

    props_type = AudioProps
    logical_name = "Audio"
    distribution = "hedron-core"

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        tracks: Sequence[Mapping[str, Any] | NodeLike] = (),
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = False,
        preload: str | None = None,
        allow_external: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            AudioProps(
                src=_asset_url(src, allow_external=allow_external),
                controls=controls,
                autoplay=autoplay,
                loop=loop,
                muted=muted,
                preload=preload,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._tracks = tuple(tracks)

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "src": self.props.src,
            "class_": class_names("hedron-audio", self.props.class_),
        }
        if self.props.controls:
            attrs["controls"] = True
        if self.props.autoplay:
            attrs["autoplay"] = True
        if self.props.loop:
            attrs["loop"] = True
        if self.props.muted:
            attrs["muted"] = True
        if self.props.preload:
            attrs["preload"] = self.props.preload
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        children = _track_nodes(self._tracks)
        children.append("Your browser does not support the audio element.")
        return html.audio(*children, **attrs)


class VideoProps(Props):
    src: SafeUrl
    controls: bool = True
    autoplay: bool = False
    loop: bool = False
    muted: bool = False
    preload: str | None = None
    poster: SafeUrl | None = None
    class_: str | None = None
    mark: str | None = None


class Video(Component[VideoProps]):
    """HTML ``<video>`` with SafeUrl src, optional poster, and caption tracks."""

    props_type = VideoProps
    logical_name = "Video"
    distribution = "hedron-core"

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        tracks: Sequence[Mapping[str, Any] | NodeLike] = (),
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = False,
        preload: str | None = None,
        poster: SafeUrl | str | None = None,
        allow_external: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        poster_url = None if poster is None else _asset_url(poster, allow_external=allow_external)
        super().__init__(
            VideoProps(
                src=_asset_url(src, allow_external=allow_external),
                controls=controls,
                autoplay=autoplay,
                loop=loop,
                muted=muted,
                preload=preload,
                poster=poster_url,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._tracks = tuple(tracks)

    def render(self) -> NodeLike:
        attrs: dict[str, HtmlAttrValue] = {
            "src": self.props.src,
            "class_": class_names("hedron-video", self.props.class_),
        }
        if self.props.controls:
            attrs["controls"] = True
        if self.props.autoplay:
            attrs["autoplay"] = True
        if self.props.loop:
            attrs["loop"] = True
        if self.props.muted:
            attrs["muted"] = True
        if self.props.preload:
            attrs["preload"] = self.props.preload
        if self.props.poster is not None:
            attrs["poster"] = self.props.poster
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        children = _track_nodes(self._tracks)
        children.append("Your browser does not support the video element.")
        return html.video(*children, **attrs)


class PdfViewerProps(Props):
    src: SafeUrl
    title: str = "PDF document"
    class_: str | None = None
    mark: str | None = None


class PdfViewer(Component[PdfViewerProps]):
    """PDF presentation via ``<object>`` (TrustedHtml; ``iframe`` remains forbidden in html.*).

    Prefer pairing ``src`` with :func:`~hedron.builtins.media.media_file_response` for
    authorized Range delivery. Sandbox notes: ``object``/``embed`` inherit document CSP;
    do not pass untrusted PDF URLs. Prefer same-origin authorized media routes.
    """

    props_type = PdfViewerProps
    logical_name = "PdfViewer"
    distribution = "hedron-core"

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        title: str = "PDF document",
        allow_external: bool = False,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            PdfViewerProps(
                src=_asset_url(src, allow_external=allow_external),
                title=title,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        src = html_escape(str(self.props.src), quote=True)
        title = html_escape(self.props.title, quote=True)
        # object/embed are forbidden via html.*; TrustedHtml is the approved sink.
        markup = (
            f'<object data="{src}" type="application/pdf" title="{title}" '
            f'class="hedron-pdf-viewer">'
            f'<a href="{src}">Open {title}</a>'
            f"</object>"
        )
        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-pdf-viewer-wrap", self.props.class_),
            "role": "region",
            "aria": {"label": self.props.title},
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.div(
            html.raw(TrustedHtml.reviewed(markup, source="hedron-core:PdfViewer")),
            **attrs,
        )


class GalleryItem(Props):
    """One gallery entry: image asset plus optional selection link and caption."""

    src: SafeUrl
    alt: str
    href: SafeUrl | None = None
    caption: str | None = None


def _gallery_item(value: GalleryItem | Mapping[str, Any]) -> GalleryItem:
    if isinstance(value, GalleryItem):
        return value
    src = _asset_url(value["src"])
    href_raw = value.get("href")
    href = None if href_raw is None else _nav_url(href_raw)
    return GalleryItem(
        src=src,
        alt=str(value.get("alt", "")),
        href=href,
        caption=None if value.get("caption") is None else str(value["caption"]),
    )


class GalleryProps(Props):
    lightbox: bool = False
    mark: str | None = None
    class_: str | None = None


class Gallery(Component[GalleryProps]):
    """Responsive image list; lightbox mode uses native ``<dialog>`` open links."""

    props_type = GalleryProps
    logical_name = "Gallery"
    distribution = "hedron-core"

    def __init__(
        self,
        items: Sequence[GalleryItem | Mapping[str, Any]],
        *,
        lightbox: bool = False,
        mark: str | None = None,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(GalleryProps(lightbox=lightbox, mark=mark, class_=class_, **kwargs))
        self._items = tuple(_gallery_item(item) for item in items)

    def render(self) -> NodeLike:
        figures: list[NodeLike] = []
        dialogs: list[NodeLike] = []
        for index, item in enumerate(self._items):
            img = html.img(src=item.src, alt=item.alt, loading="lazy")
            if self.props.lightbox:
                dialog_id = f"hedron-gallery-lb-{index}"
                open_href = SafeUrl.parse(f"#{dialog_id}", purpose=UrlPurpose.NAVIGATION)
                parts: list[NodeLike] = [
                    html.a(img, href=open_href, class_="hedron-gallery-lightbox-open")
                ]
                if item.caption:
                    parts.append(html.figcaption(item.caption))
                if item.href is not None:
                    parts.append(html.a("Select", href=item.href, class_="hedron-gallery-select"))
                figures.append(html.figure(*parts, class_="hedron-gallery-item"))
                dialogs.append(
                    html.dialog(
                        html.form(
                            html.button("Close", type="submit", formmethod="dialog"),
                            method="dialog",
                        ),
                        html.img(src=item.src, alt=item.alt),
                        id=dialog_id,
                        class_="hedron-gallery-lightbox",
                    )
                )
                continue

            body: list[NodeLike] = [img]
            if item.caption:
                body.append(html.figcaption(item.caption))
            if item.href is not None:
                # Selection via link (form POSTs remain an application composition).
                figures.append(
                    html.figure(
                        html.a(*body, href=item.href, class_="hedron-gallery-select"),
                        class_="hedron-gallery-item",
                    )
                )
            else:
                figures.append(html.figure(*body, class_="hedron-gallery-item"))

        attrs: dict[str, HtmlAttrValue] = {
            "class_": class_names("hedron-gallery", self.props.class_),
            "role": "list",
        }
        data = mark_data(self.props.mark)
        if data:
            attrs["data"] = data
        return html.div(*figures, *dialogs, **attrs)


class LogoProps(Props):
    src: SafeUrl
    alt: str
    href: SafeUrl | None = None
    class_: str | None = None


class Logo(Component[LogoProps]):
    """Application logo as ``img``, optionally wrapped in a navigation link."""

    props_type = LogoProps
    logical_name = "Logo"
    distribution = "hedron-core"

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        alt: str,
        href: SafeUrl | str | None = None,
        allow_external: bool = False,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            LogoProps(
                src=_asset_url(src, allow_external=allow_external),
                alt=alt,
                href=None if href is None else _nav_url(href, allow_external=allow_external),
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        img = html.img(
            src=self.props.src,
            alt=self.props.alt,
            class_=class_names("hedron-logo", self.props.class_),
        )
        if self.props.href is None:
            return img
        return html.a(img, href=self.props.href, class_="hedron-logo-link")


class PageIconProps(Props):
    src: SafeUrl
    alt: str = "Application icon"
    class_: str | None = None


class PageIcon(Component[PageIconProps]):
    """Page / app icon helper (``img`` with accessible alt)."""

    props_type = PageIconProps
    logical_name = "PageIcon"
    distribution = "hedron-core"

    def __init__(
        self,
        src: SafeUrl | str,
        *,
        alt: str = "Application icon",
        allow_external: bool = False,
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            PageIconProps(
                src=_asset_url(src, allow_external=allow_external),
                alt=alt,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.img(
            src=self.props.src,
            alt=self.props.alt,
            class_=class_names("hedron-page-icon", self.props.class_),
        )


class MicrophoneCaptureProps(Props):
    name: str = "microphone"
    label: str = "Record audio"
    accept: str = "audio/*"
    capture: Literal["user", "environment"] = "user"
    class_: str | None = None


class MicrophoneCapture(Component[MicrophoneCaptureProps]):
    """Audio capture via ``<input type=file capture>``.

    Browser capture is advisory markup. For timed chunk sessions, compose with
    :class:`~hedron_core.media_session.MediaSession` (phase 0.10): grant permission,
    enforce cadence/duration/bandwidth budgets, then accept uploaded chunks or a
    completed file from this control as the ``upload`` fallback.
    """

    props_type = MicrophoneCaptureProps
    logical_name = "MicrophoneCapture"
    distribution = "hedron-core"

    def __init__(
        self,
        *,
        name: str = "microphone",
        label: str = "Record audio",
        accept: str = "audio/*",
        capture: Literal["user", "environment"] = "user",
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            MicrophoneCaptureProps(
                name=name,
                label=label,
                accept=accept,
                capture=capture,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.label(
            self.props.label,
            html.input(
                type="file",
                name=self.props.name,
                accept=self.props.accept,
                capture=self.props.capture,
                aria={"label": self.props.label},
            ),
            class_=class_names("hedron-microphone-capture", self.props.class_),
        )


class CameraCaptureProps(Props):
    name: str = "camera"
    label: str = "Capture media"
    accept: str = "video/*"
    capture: Literal["user", "environment"] = "environment"
    class_: str | None = None


class CameraCapture(Component[CameraCaptureProps]):
    """Camera capture via ``<input type=file capture>``.

    Same composition model as :class:`MicrophoneCapture`: use this control for
    one-shot uploads, or feed chunks into :class:`~hedron_core.media_session.MediaSession`
    when a live capture session is required.
    """

    props_type = CameraCaptureProps
    logical_name = "CameraCapture"
    distribution = "hedron-core"

    def __init__(
        self,
        *,
        name: str = "camera",
        label: str = "Capture media",
        accept: str = "video/*",
        capture: Literal["user", "environment"] = "environment",
        class_: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            CameraCaptureProps(
                name=name,
                label=label,
                accept=accept,
                capture=capture,
                class_=class_,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return html.label(
            self.props.label,
            html.input(
                type="file",
                name=self.props.name,
                accept=self.props.accept,
                capture=self.props.capture,
                aria={"label": self.props.label},
            ),
            class_=class_names("hedron-camera-capture", self.props.class_),
        )
