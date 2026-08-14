"""Typed ChartSpec / ChartPlan models (phase 0.38 / RFC-0069)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1
SCHEMA_ID = "hedron-chart-spec/1"

FieldType = Literal["number", "string", "boolean", "temporal", "geo"]
RendererPref = Literal["svg", "canvas"]
Density = Literal["compact", "ordinary", "wide"]


class ChartModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FieldDef(ChartModel):
    name: str
    type: FieldType = "number"
    key: bool = False


class DataRef(ChartModel):
    name: str | None = None
    rows: tuple[dict[str, Any], ...] = ()
    fields: tuple[FieldDef, ...] = ()


class Encoding(ChartModel):
    field: str | None = None
    type: FieldType | None = None
    scale: str | None = None
    title: str | None = None
    aggregate: str | None = None
    stack: str | None = None
    bin: bool | dict[str, Any] | None = None
    sort: str | list[str] | None = None
    value: Any = None


class MarkDef(ChartModel):
    type: str
    encodings: dict[str, Encoding] = Field(default_factory=dict)
    tooltip: bool = True
    filled: bool | None = None
    stroke_width: float | None = None
    opacity: float | None = None
    identity: str | None = None


class ScaleDef(ChartModel):
    name: str
    type: str = "linear"
    domain: list[Any] | None = None
    range: list[Any] | None = None
    nice: bool = True
    zero: bool | None = None
    clamp: bool = False
    padding: float | None = None


class GuideDef(ChartModel):
    kind: Literal["axis", "legend", "title", "caption"] = "axis"
    scale: str | None = None
    title: str | None = None
    orient: str | None = None
    format: str | None = None
    ticks: int | None = None


class TransformDef(ChartModel):
    op: str
    field: str | None = None
    as_: str | None = Field(default=None, alias="as")
    params: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class AnnotationDef(ChartModel):
    kind: Literal["text", "reference_line", "reference_band"] = "text"
    text: str | None = None
    x: Any = None
    y: Any = None
    x2: Any = None
    y2: Any = None


class InteractionDef(ChartModel):
    inspect: bool = True
    focus_navigation: bool = True
    legend_filter: bool = True
    crosshair: bool = False
    select: bool = True
    brush: bool = False
    zoom_pan_reset: bool = False
    drill_intent: str | None = None


class ThemeDef(ChartModel):
    mode: Literal["light", "dark", "forced-colors", "print"] = "light"
    density: Density = "ordinary"
    locale: str = "en-US"
    timezone: str = "UTC"
    tokens: dict[str, str] = Field(default_factory=dict)


class ExportPolicy(ChartModel):
    svg: bool = True
    png: bool = True
    csv: bool = True
    json_export: bool = Field(default=True, alias="json")
    print: bool = True
    max_px: int = 4096

    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=True)


class AccessibilityDef(ChartModel):
    title: str
    description: str
    summary: str | None = None
    include_table: bool = True


class ChartSpec(ChartModel):
    """Immutable, JSON-serializable, schema-versioned chart specification."""

    schema_version: int = SCHEMA_VERSION
    data: DataRef = Field(default_factory=DataRef)
    marks: tuple[MarkDef, ...] = ()
    scales: tuple[ScaleDef, ...] = ()
    guides: tuple[GuideDef, ...] = ()
    transforms: tuple[TransformDef, ...] = ()
    composition: dict[str, Any] = Field(default_factory=dict)
    annotations: tuple[AnnotationDef, ...] = ()
    interaction: InteractionDef = Field(default_factory=InteractionDef)
    theme: ThemeDef = Field(default_factory=ThemeDef)
    export: ExportPolicy = Field(default_factory=ExportPolicy)
    renderer: RendererPref = "svg"
    accessibility: AccessibilityDef

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", by_alias=True)


class RendererDecision(ChartModel):
    paint: RendererPref
    reason: str
    mark_count: int
    canvas_threshold: int


class AccessibilityPlan(ChartModel):
    title: str
    description: str
    encoding_explanation: str
    summary: str
    interaction_help: str
    table_rows: tuple[dict[str, Any], ...] = ()
    include_table: bool = True


class ChartPlan(ChartModel):
    """Deterministic compilation result consumed by host, fallback, Explorer, export."""

    schema_id: str = SCHEMA_ID
    schema_version: int = SCHEMA_VERSION
    spec_fingerprint: str
    data_fingerprint: str
    domains: dict[str, list[Any]] = Field(default_factory=dict)
    guides: tuple[GuideDef, ...] = ()
    marks: tuple[dict[str, Any], ...] = ()
    mark_count: int = 0
    renderer: RendererDecision
    accessibility: AccessibilityPlan
    assets: tuple[str, ...] = ()
    export: ExportPolicy = Field(default_factory=ExportPolicy)
    warnings: tuple[str, ...] = ()
    limits: dict[str, int] = Field(default_factory=dict)
    theme: ThemeDef = Field(default_factory=ThemeDef)
    interaction: InteractionDef = Field(default_factory=InteractionDef)
    layout: dict[str, Any] = Field(default_factory=dict)
    transformed_rows: tuple[dict[str, Any], ...] = ()

    def to_json_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
