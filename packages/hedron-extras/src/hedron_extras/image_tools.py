"""Interactive image tools for phase 0.16."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, Literal

from pydantic import Field

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_extras.host import extras_host

_MAX_SOURCE_CHARS = 2048


def _asset_src(src: str | SafeUrl) -> SafeUrl:
    if isinstance(src, SafeUrl):
        return src
    if not src or len(src) > _MAX_SOURCE_CHARS:
        raise ValueError(
            "Image source must be a declared URL/file/byte reference within size limits"
        )
    if src.lower().startswith("javascript:"):
        raise ValueError("JavaScript image sources are not allowed")
    return SafeUrl.parse(src, purpose=UrlPurpose.ASSET)


class ImageCompareProps(ElementProps):
    before_src: SafeUrl
    after_src: SafeUrl
    before_label: str = "Before"
    after_label: str = "After"
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    position: float = 0.5


class ImageCompare(Component[ImageCompareProps]):
    props_type = ImageCompareProps
    logical_name = "ImageCompare"
    distribution = "hedron-extras"

    def __init__(
        self,
        before_src: str | SafeUrl,
        after_src: str | SafeUrl,
        *,
        before_label: str = "Before",
        after_label: str = "After",
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        position: float = 0.5,
        **kwargs: Any,
    ) -> None:
        pos = max(0.0, min(1.0, position))
        super().__init__(
            ImageCompareProps(
                before_src=_asset_src(before_src),
                after_src=_asset_src(after_src),
                before_label=before_label,
                after_label=after_label,
                orientation=orientation,
                position=pos,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        return extras_host(
            "hedron-extras-image-tools",
            html.figure(
                html.img(src=self.props.before_src, alt=self.props.before_label),
                html.img(src=self.props.after_src, alt=self.props.after_label),
                html.input(
                    type="range",
                    min="0",
                    max="100",
                    value=str(int(self.props.position * 100)),
                    aria={"label": "Compare position"},
                    data={"keyboard-alt": "range"},
                ),
                html.figcaption(f"{self.props.before_label} / {self.props.after_label}"),
                class_=class_names("hedron-image-compare", self.props.class_),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-image": "compare",
                    "orientation": self.props.orientation,
                    "static-fallback": "side-by-side",
                },
            ),
            payload={"kind": "compare"},
        )


class ImageCropProps(ElementProps):
    src: SafeUrl
    shape: Literal["rect", "circle"] = "rect"
    x: float = 0.0
    y: float = 0.0
    width: float = 1.0
    height: float = 1.0
    name: str = "crop"
    source_width: int = 0
    source_height: int = 0
    revision: str = "0"


class ImageCrop(Component[ImageCropProps]):
    props_type = ImageCropProps
    logical_name = "ImageCrop"
    distribution = "hedron-extras"

    def __init__(
        self,
        src: str | SafeUrl,
        *,
        shape: Literal["rect", "circle"] = "rect",
        x: float = 0.0,
        y: float = 0.0,
        width: float = 1.0,
        height: float = 1.0,
        name: str = "crop",
        source_width: int = 0,
        source_height: int = 0,
        revision: str = "0",
        **kwargs: Any,
    ) -> None:
        for label, value in (("x", x), ("y", y), ("width", width), ("height", height)):
            if value < 0.0 or value > 1.0:
                raise ValueError(f"ImageCrop {label} must be normalized 0..1")
        if x + width > 1.0 or y + height > 1.0:
            raise ValueError("ImageCrop rect must stay within the normalized unit square")
        if source_width < 0 or source_height < 0:
            raise ValueError("ImageCrop source dimensions must be >= 0")
        super().__init__(
            ImageCropProps(
                src=_asset_src(src),
                shape=shape,
                x=x,
                y=y,
                width=width,
                height=height,
                name=name,
                source_width=source_width,
                source_height=source_height,
                revision=revision,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        fields = [
            html.img(src=self.props.src, alt="Crop source"),
            html.input(type="hidden", name=f"{self.props.name}__shape", value=self.props.shape),
            html.label(
                "X",
                html.input(
                    type="number",
                    name=f"{self.props.name}__x",
                    value=str(self.props.x),
                    min="0",
                    max="1",
                    step="0.01",
                ),
            ),
            html.label(
                "Y",
                html.input(
                    type="number",
                    name=f"{self.props.name}__y",
                    value=str(self.props.y),
                    min="0",
                    max="1",
                    step="0.01",
                ),
            ),
            html.label(
                "Width",
                html.input(
                    type="number",
                    name=f"{self.props.name}__w",
                    value=str(self.props.width),
                    min="0",
                    max="1",
                    step="0.01",
                ),
            ),
            html.label(
                "Height",
                html.input(
                    type="number",
                    name=f"{self.props.name}__h",
                    value=str(self.props.height),
                    min="0",
                    max="1",
                    step="0.01",
                ),
            ),
            html.input(
                type="hidden",
                name=f"{self.props.name}__revision",
                value=self.props.revision,
            ),
            html.input(
                type="hidden",
                name=f"{self.props.name}__source_width",
                value=str(self.props.source_width),
            ),
            html.input(
                type="hidden",
                name=f"{self.props.name}__source_height",
                value=str(self.props.source_height),
            ),
            html.input(type="hidden", name=f"{self.props.name}__confirmed", value="server"),
        ]
        return extras_host(
            "hedron-extras-image-tools",
            html.form(
                *fields,
                class_=class_names("hedron-image-crop", self.props.class_),
                id=self.props.id,
                method="post",
                data={
                    **mark_data(self.props.mark),
                    "hedron-image": "crop",
                    "shape": self.props.shape,
                    "decode-limit": "server",
                    "drag-alternative": "numeric",
                    "source-width": str(self.props.source_width),
                    "source-height": str(self.props.source_height),
                    "revision": self.props.revision,
                    "server-confirmed": "true",
                },
            ),
            payload={
                "kind": "crop",
                "source_width": self.props.source_width,
                "source_height": self.props.source_height,
                "revision": self.props.revision,
            },
        )


class RegionProps(Props):
    kind: Literal["box", "lasso"] = "box"
    points: list[list[float]] = Field(default_factory=list)


class ImageRegionSelectProps(ElementProps):
    src: SafeUrl
    regions: list[RegionProps] = Field(default_factory=list)
    name: str = "region"
    mode: Literal["box", "lasso"] = "box"


class ImageRegionSelect(Component[ImageRegionSelectProps]):
    props_type = ImageRegionSelectProps
    logical_name = "ImageRegionSelect"
    distribution = "hedron-extras"

    def __init__(
        self,
        src: str | SafeUrl,
        *,
        regions: Sequence[RegionProps | dict[str, Any]] | None = None,
        name: str = "region",
        mode: Literal["box", "lasso"] = "box",
        **kwargs: Any,
    ) -> None:
        parsed = [
            r if isinstance(r, RegionProps) else RegionProps.model_validate(r)
            for r in (regions or [])
        ]
        for region in parsed:
            for pt in region.points:
                if len(pt) != 2 or any(c < 0.0 or c > 1.0 for c in pt):
                    raise ValueError("Region points must be normalized [x, y] pairs")
        super().__init__(
            ImageRegionSelectProps(
                src=_asset_src(src),
                regions=parsed,
                name=name,
                mode=mode,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        payload = json.dumps(
            [{"kind": r.kind, "points": r.points} for r in self.props.regions],
            separators=(",", ":"),
        )
        return extras_host(
            "hedron-extras-image-tools",
            html.div(
                html.img(src=self.props.src, alt="Region selection source"),
                html.textarea(
                    payload,
                    name=self.props.name,
                    rows=3,
                    cols=40,
                    placeholder="Numeric region points (normalized)",
                    aria={"label": "Region points alternative to drawing"},
                ),
                html.input(type="hidden", name=f"{self.props.name}__confirmed", value="server"),
                class_=class_names("hedron-image-region", self.props.class_),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-image": "region",
                    "mode": self.props.mode,
                    "drag-alternative": "textarea",
                    "server-confirmed": "true",
                },
            ),
            payload={"kind": "region", "mode": self.props.mode},
        )


class AnnotationProps(Props):
    label: str
    x: float
    y: float
    width: float = 0.0
    height: float = 0.0


class ImageAnnotationsProps(ElementProps):
    src: SafeUrl
    annotations: list[AnnotationProps] = Field(default_factory=list)
    name: str = "annotations"


class ImageAnnotations(Component[ImageAnnotationsProps]):
    props_type = ImageAnnotationsProps
    logical_name = "ImageAnnotations"
    distribution = "hedron-extras"

    def __init__(
        self,
        src: str | SafeUrl,
        annotations: Sequence[AnnotationProps | dict[str, Any]] | None = None,
        *,
        name: str = "annotations",
        **kwargs: Any,
    ) -> None:
        parsed = [
            a if isinstance(a, AnnotationProps) else AnnotationProps.model_validate(a)
            for a in (annotations or [])
        ]
        if len(parsed) > 500:
            raise ValueError("Annotation point budget exceeded (max 500)")
        for ann in parsed:
            for label, value in (
                ("x", ann.x),
                ("y", ann.y),
                ("width", ann.width),
                ("height", ann.height),
            ):
                if value < 0.0 or value > 1.0:
                    raise ValueError(f"Annotation {label} must be normalized 0..1")
        super().__init__(
            ImageAnnotationsProps(
                src=_asset_src(src),
                annotations=parsed,
                name=name,
                **kwargs,
            )
        )

    def render(self) -> NodeLike:
        items = [
            html.li(f"{a.label} @ ({a.x:.2f},{a.y:.2f})", data={"ann-label": a.label})
            for a in self.props.annotations
        ]
        return extras_host(
            "hedron-extras-image-tools",
            html.div(
                html.img(src=self.props.src, alt="Annotated image"),
                html.ul(*items, aria={"label": "Annotations list alternative"}),
                html.input(type="hidden", name=f"{self.props.name}__confirmed", value="server"),
                class_=class_names("hedron-image-annotations", self.props.class_),
                id=self.props.id,
                data={
                    **mark_data(self.props.mark),
                    "hedron-image": "annotations",
                    "drag-alternative": "list",
                    "server-confirmed": "true",
                },
            ),
            payload={"kind": "annotations", "count": len(self.props.annotations)},
        )
