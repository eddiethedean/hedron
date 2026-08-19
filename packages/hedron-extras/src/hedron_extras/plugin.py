"""Register hedron-extras components, assets, and feature manifests.

EXTRAS-025 landmines (CodeEditor, TerminalView, Joystick, DeviceBridge) register
via ``hedron_extras.experimental`` / ``hedron[experimental-ui]`` — not this plugin.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_core.codes import HED_ASSET_MISSING
from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset, register_browser_module, register_component
from hedron_extras.composition import (
    ChoiceCards,
    FloatingAction,
    FocusScrollRequest,
    KeyboardShortcuts,
    SplitPane,
    Steps,
    TreeView,
)
from hedron_extras.display import DiagramOutput, LogConsole, TokenWeightedText
from hedron_extras.editors import Calendar, SignaturePad, Typeahead
from hedron_extras.image_tools import ImageAnnotations, ImageCompare, ImageCrop, ImageRegionSelect
from hedron_extras.recipes import AvatarProfile, BadgeLink, MetricCard, TodoList
from hedron_extras.sandbox import BrowserPythonSandbox
from hedron_extras.workbench import (
    CallableActionForm,
    ChartWorkbench,
    DataExplorer,
    JSONEditor,
)

_ROOT = Path(__file__).resolve().parent

PLUGIN_META = PluginMeta(
    name="hedron_extras",
    version="0.50.1",
    distribution="hedron-extras",
    hedron_version=">=0.50,<0.51",
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)

# relative path → (browser module logical id, custom element tag, component classes)
_BROWSER_HOSTS: tuple[tuple[str, str, str, tuple[type[Any], ...]], ...] = (
    (
        "assets/sandbox/bridge.js",
        "hedron-extras:sandbox-bridge",
        "hedron-extras-sandbox",
        (BrowserPythonSandbox,),
    ),
    (
        "assets/image_tools/image.js",
        "hedron-extras:image-tools",
        "hedron-extras-image-tools",
        (ImageCompare, ImageCrop, ImageRegionSelect, ImageAnnotations),
    ),
    (
        "assets/calendar/calendar.js",
        "hedron-extras:calendar",
        "hedron-extras-calendar",
        (Calendar,),
    ),
    (
        "assets/signature/signature.js",
        "hedron-extras:signature",
        "hedron-extras-signature",
        (SignaturePad,),
    ),
    (
        "assets/typeahead/typeahead.js",
        "hedron-extras:typeahead",
        "hedron-extras-typeahead",
        (Typeahead,),
    ),
    (
        "assets/composition/composition.js",
        "hedron-extras:composition",
        "hedron-extras-composition",
        (ChoiceCards, TreeView, Steps, SplitPane, FloatingAction, KeyboardShortcuts),
    ),
)

_STATIC_COMPONENTS: tuple[type[Any], ...] = (
    FocusScrollRequest,
    AvatarProfile,
    BadgeLink,
    MetricCard,
    TodoList,
    DataExplorer,
    JSONEditor,
    ChartWorkbench,
    CallableActionForm,
    LogConsole,
    TokenWeightedText,
    DiagramOutput,
)


def _asset_logical_id(rel: str) -> str:
    return f"hedron-extras:{rel.replace('/', '.')}"


def _register_module_asset(rel: str) -> tuple[str, Path]:
    path = _ROOT / rel
    if not path.is_file():
        raise error(
            HED_ASSET_MISSING,
            title="Extras browser asset missing",
            explanation=f"Declared hedron-extras asset {rel!r} was not found at {path}.",
            remediation="Reinstall hedron-extras or repair the package wheel.",
        )
    digest = content_digest(path.read_bytes())
    logical = _asset_logical_id(rel)
    register_asset(
        logical_id=logical,
        kind="module",
        path=str(path),
        digest=digest,
        content_type="text/javascript",
        attributes={"type": "module"},
    )
    return logical, path


def register(ctx: PluginContext) -> None:
    module_by_cls: dict[type[Any], str] = {}
    asset_logical_by_rel: dict[str, str] = {}

    for rel, module_id, tag_name, classes in _BROWSER_HOSTS:
        asset_id, path = _register_module_asset(rel)
        asset_logical_by_rel[rel] = asset_id
        register_browser_module(
            logical_id=module_id,
            tag_name=tag_name,
            module_path=str(path),
            observed_attributes=("data-hedron-payload",),
            events=(),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
        for cls in classes:
            module_by_cls[cls] = str(path)

    for cls in (*module_by_cls, *_STATIC_COMPONENTS):
        logical = (
            f"{cls.distribution}:{cls.__module__}.{getattr(cls, 'logical_name', cls.__name__)}"
        )
        modules = (module_by_cls[cls],) if cls in module_by_cls else ()
        register_component(
            logical_id=logical,
            name=getattr(cls, "logical_name", cls.__name__) or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=getattr(cls, "props_type", type(None)).__name__,
            browser_modules=modules,
            accessibility_notes="See feature manifest a11y_notes.",
        )

    feature_specs: tuple[dict[str, Any], ...] = (
        {
            "name": "composition",
            "stability": "beta",
            "description": "ChoiceCards, TreeView, Steps, SplitPane, FAB, shortcuts",
            "assets": (asset_logical_by_rel["assets/composition/composition.js"],),
            "http_fallback": True,
            "a11y_notes": "Semantic controls with keyboard and no-JS fallbacks.",
            "security_notes": "No filesystem authority from TreeView.",
        },
        {
            "name": "workbench",
            "stability": "beta",
            "description": "DataExplorer, JSONEditor, ChartWorkbench, CallableActionForm",
            "http_fallback": True,
            "a11y_notes": "Textarea fallbacks for editors.",
            "security_notes": (
                "DataExplorer emits TransformPlan only. CodeEditor is quarantined under "
                "hedron[experimental-ui] (EXTRAS-025)."
            ),
        },
        {
            "name": "image_tools",
            "stability": "beta",
            "assets": (asset_logical_by_rel["assets/image_tools/image.js"],),
            "http_fallback": True,
            "a11y_notes": "Numeric/list alternatives to drag.",
            "security_notes": "Declared sources only; decode limits server-owned.",
        },
        {
            "name": "calendar",
            "stability": "beta",
            "assets": (asset_logical_by_rel["assets/calendar/calendar.js"],),
            "http_fallback": True,
        },
        {
            "name": "signature",
            "stability": "beta",
            "assets": (asset_logical_by_rel["assets/signature/signature.js"],),
            "http_fallback": True,
            "a11y_notes": "File upload alternative to pointer drawing.",
        },
        {
            "name": "typeahead",
            "stability": "beta",
            "assets": (asset_logical_by_rel["assets/typeahead/typeahead.js"],),
            "http_fallback": True,
            "a11y_notes": "Combobox pattern with datalist fallback.",
        },
        {
            "name": "display",
            "stability": "beta",
            "description": "LogConsole, TokenWeightedText, DiagramOutput",
            "http_fallback": True,
            "security_notes": "No process-global stdout capture.",
        },
        {
            "name": "recipes",
            "stability": "recipe",
            "description": "AvatarProfile, BadgeLink, MetricCard, TodoList composition recipes",
            "http_fallback": True,
        },
        {
            "name": "sandbox",
            "stability": "beta",
            "assets": (asset_logical_by_rel["assets/sandbox/bridge.js"],),
            "http_fallback": False,
            "security_notes": "Origin isolation; no server/session; network deny.",
            "a11y_notes": "Budget and teardown documented; limited AT surface.",
        },
    )

    for spec in feature_specs:
        ctx.register_feature(
            name=str(spec["name"]),
            stability=spec.get("stability", "beta"),  # type: ignore[arg-type]
            dependencies=tuple(spec.get("dependencies") or ()),
            assets=tuple(spec.get("assets") or ()),
            a11y_notes=str(spec.get("a11y_notes") or ""),
            security_notes=str(spec.get("security_notes") or ""),
            http_fallback=bool(spec.get("http_fallback", True)),
            description=str(spec.get("description") or ""),
        )

    # Packages view lists plugin panels; dedicated /extras route is not shipped yet.
    ctx.register_explorer_provider(
        panel_id="hedron-extras-features",
        title="Extras features",
        description="Curated extras feature manifests and stability labels",
        path="/hedron-explorer/packages",
        capabilities=("html",),
    )
    ctx.register_diagnostic_owner("HED-EXTRAS-")
    from hedron_core.catalog import SurfaceProjectionProvider

    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.extras",
            provider="hedron-extras",
            provider_version=PLUGIN_META.version,
            surface="curated extras",
            limitations=("current extras only; landmines stay experimental",),
        )
    )


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
