"""Package-owned extras inventory (DESCRIPTOR-051).

``ExtrasFeature`` lives in hedron-extras. It projects into
``PluginContext.register_feature`` / ``FeatureManifest`` and does not replace
``FeatureBundle`` or ``InteractionCatalog``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hedron_core.plugins import PluginContext
from hedron_core.plugins.meta import StabilityLabel

__all__ = ["ExtrasFeature", "SUPPORTED_BROWSER_TAGS", "extras_features"]

SUPPORTED_BROWSER_TAGS: tuple[str, ...] = (
    "hedron-extras-image-tools",
    "hedron-extras-calendar",
    "hedron-extras-signature",
    "hedron-extras-typeahead",
    "hedron-extras-composition",
)

EXPERIMENTAL_BROWSER_TAGS: tuple[str, ...] = (
    "hedron-extras-sandbox",
    "hedron-extras-code-editor",
    "hedron-extras-terminal",
)


def _stability(maturity: str) -> StabilityLabel:
    if maturity in {"experimental", "recipe", "stable", "beta"}:
        return maturity  # type: ignore[return-value]
    return "beta"


@dataclass(frozen=True, slots=True)
class ExtrasFeature:
    """Versioned extras inventory row (D-088 / RFC-0078)."""

    name: str
    component_tag: str
    python_facade: tuple[str, ...]
    schemas: tuple[str, ...] = ()
    events: tuple[str, ...] = ()
    assets: tuple[str, ...] = ()
    optional_dependencies: tuple[str, ...] = ()
    fallback: str = "http"
    limits: dict[str, int | str] = field(default_factory=dict)
    maturity: str = "beta"
    accessibility_contract: str = ""
    explorer_projection: str = "packages-panel"
    jinja_projection: str = "component-facade"
    conformance_projection: str = "optional-surface"
    http_fallback: bool = True
    description: str = ""
    security_notes: str = ""

    def register(self, ctx: PluginContext) -> None:
        ctx.register_feature(
            name=self.name,
            stability=_stability(self.maturity),
            dependencies=self.optional_dependencies,
            assets=self.assets,
            a11y_notes=self.accessibility_contract,
            security_notes=self.security_notes,
            http_fallback=self.http_fallback,
            description=self.description or self.name,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "component_tag": self.component_tag,
            "python_facade": list(self.python_facade),
            "schemas": list(self.schemas),
            "events": list(self.events),
            "assets": list(self.assets),
            "optional_dependencies": list(self.optional_dependencies),
            "fallback": self.fallback,
            "limits": dict(self.limits),
            "maturity": self.maturity,
            "accessibility_contract": self.accessibility_contract,
            "explorer_projection": self.explorer_projection,
            "jinja_projection": self.jinja_projection,
            "conformance_projection": self.conformance_projection,
            "http_fallback": self.http_fallback,
            "description": self.description,
            "security_notes": self.security_notes,
        }


def extras_features(*, assets: dict[str, str] | None = None) -> tuple[ExtrasFeature, ...]:
    """Canonical Supported + recipe inventory for the default extras plugin.

    Sandbox is registered by ``hedron_extras_sandbox``, not this list.
    """
    asset = assets or {}
    lifecycle = asset.get("lifecycle", "")
    image = (lifecycle,) if lifecycle else ()
    return (
        ExtrasFeature(
            name="composition",
            component_tag="hedron-extras-composition",
            python_facade=(
                "ChoiceCards",
                "TreeView",
                "Steps",
                "SplitPane",
                "FloatingAction",
                "KeyboardShortcuts",
                "FocusScrollRequest",
            ),
            schemas=("TreeNodeProps",),
            events=("select", "expand"),
            assets=image,
            fallback="semantic-controls",
            limits={"tree_nodes": 5_000},
            maturity="beta",
            accessibility_contract="Semantic controls with keyboard and no-JS fallbacks.",
            security_notes="No filesystem authority from TreeView.",
            description="ChoiceCards, TreeView, Steps, SplitPane, FAB, shortcuts",
        ),
        ExtrasFeature(
            name="workbench",
            component_tag="",
            python_facade=("DataExplorer", "JSONEditor", "ChartWorkbench", "CallableActionForm"),
            schemas=("TransformPlan",),
            events=("apply", "cancel"),
            fallback="textarea",
            limits={"json_max_chars": 200_000, "data_max_rows": 10_000},
            maturity="beta",
            accessibility_contract="Textarea fallbacks for editors.",
            security_notes=(
                "DataExplorer emits TransformPlan only. CodeEditor is quarantined under "
                "hedron[experimental-ui] (EXTRAS-025). JSON is never eval'd."
            ),
            optional_dependencies=("json_editor", "data_explorer", "chart_workbench"),
            description="DataExplorer, JSONEditor, ChartWorkbench, CallableActionForm",
        ),
        ExtrasFeature(
            name="image_tools",
            component_tag="hedron-extras-image-tools",
            python_facade=(
                "ImageCompare",
                "ImageCrop",
                "ImageRegionSelect",
                "ImageAnnotations",
            ),
            schemas=("normalized-rect", "normalized-region"),
            events=("crop", "region", "annotate"),
            assets=image,
            fallback="numeric-inputs",
            limits={"annotation_max": 500, "coord": "0..1"},
            maturity="beta",
            accessibility_contract="Numeric/list alternatives to drag.",
            security_notes="Declared sources only; decode limits server-owned.",
        ),
        ExtrasFeature(
            name="calendar",
            component_tag="hedron-extras-calendar",
            python_facade=("Calendar",),
            assets=image,
            fallback="input-date",
            maturity="beta",
        ),
        ExtrasFeature(
            name="signature",
            component_tag="hedron-extras-signature",
            python_facade=("SignaturePad",),
            assets=image,
            fallback="file-upload",
            limits={"max_bytes": 2_000_000},
            maturity="beta",
            accessibility_contract="File upload alternative to pointer drawing.",
        ),
        ExtrasFeature(
            name="typeahead",
            component_tag="hedron-extras-typeahead",
            python_facade=("Typeahead",),
            events=("query", "select"),
            assets=image,
            fallback="datalist",
            limits={"max_options": 5_000, "page_size": 50},
            maturity="beta",
            accessibility_contract="Combobox pattern with datalist fallback.",
        ),
        ExtrasFeature(
            name="display",
            component_tag="",
            python_facade=("LogConsole", "TokenWeightedText", "DiagramOutput"),
            fallback="pre",
            maturity="beta",
            security_notes="No process-global stdout capture.",
            description="LogConsole, TokenWeightedText, DiagramOutput",
        ),
        ExtrasFeature(
            name="recipes",
            component_tag="",
            python_facade=("AvatarProfile", "BadgeLink", "MetricCard", "TodoList"),
            maturity="recipe",
            description="AvatarProfile, BadgeLink, MetricCard, TodoList composition recipes",
        ),
    )


def sandbox_feature(*, assets: tuple[str, ...] = ()) -> ExtrasFeature:
    return ExtrasFeature(
        name="sandbox",
        component_tag="hedron-extras-sandbox",
        python_facade=("BrowserPythonSandbox",),
        assets=assets,
        fallback="none",
        limits={"cpu_ms": 60_000, "memory_mb": 1024, "output_chars": 2_000_000},
        maturity="experimental",
        http_fallback=False,
        accessibility_contract="Budget and teardown documented; limited AT surface.",
        security_notes="Origin isolation; no server/session; network deny.",
        description="Experimental isolated browser Python sandbox (opt-in plugin).",
    )
