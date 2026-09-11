"""Register hedron-extras components, assets, and feature manifests.

EXTRAS-025 landmines (CodeEditor, TerminalView, Joystick, DeviceBridge) register
via ``hedron_extras.experimental`` / ``hedron[experimental-ui]`` — not this plugin.

``BrowserPythonSandbox`` registers via ``hedron_extras_sandbox`` (opt-in). Import
remains ``from hedron_extras.sandbox import BrowserPythonSandbox``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_core.codes import HED_ASSET_MISSING
from hedron_core.component import Component
from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_core.plugins import (
    PluginCapabilities,
    PluginContext,
    PluginDefinition,
    PluginMeta,
)
from hedron_extras.composition import (
    ChoiceCards,
    FloatingAction,
    FocusScrollRequest,
    KeyboardShortcuts,
    SplitPane,
    Steps,
    TreeView,
)
from hedron_extras.descriptor import extras_features
from hedron_extras.display import DiagramOutput, LogConsole, TokenWeightedText
from hedron_extras.editors import Calendar, SignaturePad, Typeahead
from hedron_extras.image_tools import ImageAnnotations, ImageCompare, ImageCrop, ImageRegionSelect
from hedron_extras.recipes import AvatarProfile, BadgeLink, MetricCard, TodoList
from hedron_extras.workbench import (
    CallableActionForm,
    ChartWorkbench,
    DataExplorer,
    JSONEditor,
)

_ROOT = Path(__file__).resolve().parent

PLUGIN_META = PluginMeta(
    name="hedron_extras",
    version="1.0.10",
    distribution="hedron-extras",
    hedron_version=">=1.0,<2.0",
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)

_LIFECYCLE_REL = "assets/lifecycle/host.js"

# relative path → (browser module logical id, custom element tag, component classes)
_BROWSER_HOSTS: tuple[tuple[str, str, str, tuple[type[Component[Any]], ...]], ...] = (
    (
        _LIFECYCLE_REL,
        "hedron-extras:image-tools",
        "hedron-extras-image-tools",
        (ImageCompare, ImageCrop, ImageRegionSelect, ImageAnnotations),
    ),
    (
        _LIFECYCLE_REL,
        "hedron-extras:calendar",
        "hedron-extras-calendar",
        (Calendar,),
    ),
    (
        _LIFECYCLE_REL,
        "hedron-extras:signature",
        "hedron-extras-signature",
        (SignaturePad,),
    ),
    (
        _LIFECYCLE_REL,
        "hedron-extras:typeahead",
        "hedron-extras-typeahead",
        (Typeahead,),
    ),
    (
        _LIFECYCLE_REL,
        "hedron-extras:composition",
        "hedron-extras-composition",
        (
            ChoiceCards,
            TreeView,
            Steps,
            SplitPane,
            FloatingAction,
            KeyboardShortcuts,
            FocusScrollRequest,
        ),
    ),
)

_STATIC_COMPONENTS: tuple[type[Component[Any]], ...] = (
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


def _module_asset(rel: str) -> tuple[str, Path]:
    path = _ROOT / rel
    if not path.is_file():
        raise error(
            HED_ASSET_MISSING,
            title="Extras browser asset missing",
            explanation=f"Declared hedron-extras asset {rel!r} was not found at {path}.",
            remediation="Reinstall hedron-extras or repair the package wheel.",
        )
    logical = _asset_logical_id(rel)
    return logical, path


def _register_module_asset(ctx: PluginContext, rel: str) -> tuple[str, Path]:
    logical, path = _module_asset(rel)
    ctx.register_asset(
        logical_id=logical,
        kind="module",
        path=str(path),
        digest=content_digest(path.read_bytes()),
        content_type="text/javascript",
        attributes={"type": "module"},
    )
    return logical, path


def _register_assets(ctx: PluginContext) -> None:
    _register_module_asset(ctx, _LIFECYCLE_REL)


def _register_components(ctx: PluginContext) -> None:
    module_by_cls: dict[type[Component[Any]], str] = {}
    _, lifecycle_path = _module_asset(_LIFECYCLE_REL)

    for _rel, module_id, tag_name, classes in _BROWSER_HOSTS:
        ctx.register_browser_module(
            logical_id=module_id,
            tag_name=tag_name,
            module_path=str(lifecycle_path),
            observed_attributes=("data-hedron-payload",),
            events=(),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
        for cls in classes:
            module_by_cls[cls] = str(lifecycle_path)

    for cls in (*module_by_cls, *_STATIC_COMPONENTS):
        logical = (
            f"{cls.distribution}:{cls.__module__}.{getattr(cls, 'logical_name', cls.__name__)}"
        )
        modules = (module_by_cls[cls],) if cls in module_by_cls else ()
        ctx.register_component(
            logical_id=logical,
            name=getattr(cls, "logical_name", cls.__name__) or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=getattr(cls, "props_type", type(None)).__name__,
            browser_modules=modules,
            accessibility_notes="See feature manifest a11y_notes.",
        )


def _register_features(ctx: PluginContext) -> None:
    for feature in extras_features(assets={"lifecycle": _asset_logical_id(_LIFECYCLE_REL)}):
        feature.register(ctx)


def _register_catalog(ctx: PluginContext) -> None:
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


PLUGIN = PluginDefinition.from_callbacks(
    PLUGIN_META,
    (
        ("assets", _register_assets),
        ("components", _register_components),
        ("features", _register_features),
        ("catalog", _register_catalog),
    ),
)


def register(ctx: PluginContext) -> None:
    PLUGIN.register(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
