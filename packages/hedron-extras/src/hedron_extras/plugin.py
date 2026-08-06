"""Register hedron-extras components, assets, and feature manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset, register_component
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
from hedron_extras.specialty import DeviceBridge, Joystick, TerminalView
from hedron_extras.workbench import (
    CallableActionForm,
    ChartWorkbench,
    CodeEditor,
    DataExplorer,
    JSONEditor,
)

_ROOT = Path(__file__).resolve().parent
_ASSETS = _ROOT / "assets"

PLUGIN_META = PluginMeta(
    name="hedron_extras",
    version="0.16.0",
    distribution="hedron-extras",
    hedron_version=">=0.16,<0.17",
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)

_CORE_COMPONENTS: tuple[type[Any], ...] = (
    ChoiceCards,
    TreeView,
    Steps,
    SplitPane,
    FloatingAction,
    KeyboardShortcuts,
    FocusScrollRequest,
    AvatarProfile,
    BadgeLink,
    MetricCard,
    TodoList,
    DataExplorer,
    JSONEditor,
    CodeEditor,
    ChartWorkbench,
    CallableActionForm,
    ImageCompare,
    ImageCrop,
    ImageRegionSelect,
    ImageAnnotations,
    Calendar,
    SignaturePad,
    Typeahead,
    LogConsole,
    TokenWeightedText,
    DiagramOutput,
    BrowserPythonSandbox,
    TerminalView,
    Joystick,
    DeviceBridge,
)

_FEATURE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "name": "composition",
        "stability": "beta",
        "description": "ChoiceCards, TreeView, Steps, SplitPane, FAB, shortcuts",
        "http_fallback": True,
        "a11y_notes": "Semantic controls with keyboard and no-JS fallbacks.",
        "security_notes": "No filesystem authority from TreeView.",
    },
    {
        "name": "workbench",
        "stability": "beta",
        "description": "DataExplorer, JSONEditor, CodeEditor, ChartWorkbench, CallableActionForm",
        "dependencies": (),
        "assets": ("assets/code_editor/editor.js",),
        "http_fallback": True,
        "a11y_notes": "Textarea fallbacks for editors.",
        "security_notes": (
            "CodeEditor never evaluates buffers; DataExplorer emits TransformPlan only."
        ),
    },
    {
        "name": "image_tools",
        "stability": "beta",
        "assets": ("assets/image_tools/image.js",),
        "http_fallback": True,
        "a11y_notes": "Numeric/list alternatives to drag.",
        "security_notes": "Declared sources only; decode limits server-owned.",
    },
    {
        "name": "calendar",
        "stability": "beta",
        "assets": ("assets/calendar/calendar.js",),
        "http_fallback": True,
    },
    {
        "name": "signature",
        "stability": "beta",
        "assets": ("assets/signature/signature.js",),
        "http_fallback": True,
        "a11y_notes": "File upload alternative to pointer drawing.",
    },
    {
        "name": "typeahead",
        "stability": "beta",
        "assets": ("assets/typeahead/typeahead.js",),
        "http_fallback": True,
        "a11y_notes": "Combobox pattern with datalist fallback.",
    },
    {
        "name": "display",
        "stability": "beta",
        "description": "LogConsole and presentation recipes",
        "http_fallback": True,
        "security_notes": "No process-global stdout capture.",
    },
    {
        "name": "sandbox",
        "stability": "beta",
        "assets": ("assets/sandbox/bridge.js",),
        "http_fallback": False,
        "security_notes": "Origin isolation; no server/session; network deny.",
        "a11y_notes": "Budget and teardown documented; limited AT surface.",
    },
    {
        "name": "terminal",
        "stability": "experimental",
        "assets": ("assets/terminal/terminal.js",),
        "http_fallback": False,
        "security_notes": "Fail-closed without allowlist+authz+audit.",
        "a11y_notes": "Limited; command form is the accessible path.",
    },
    {
        "name": "joystick",
        "stability": "experimental",
        "http_fallback": True,
        "a11y_notes": "Range input alternative.",
        "security_notes": "Bounded event rate.",
    },
    {
        "name": "device_bridge",
        "stability": "experimental",
        "http_fallback": True,
        "security_notes": "Command allowlist; CSRF required for mutating commands.",
    },
)


def _register_asset(rel: str) -> str | None:
    path = _ROOT / rel
    if not path.is_file():
        return None
    digest = content_digest(path.read_bytes())
    logical = f"hedron-extras:{rel.replace('/', '.')}"
    register_asset(
        logical_id=logical,
        kind="js",
        path=str(path),
        digest=digest,
        content_type="text/javascript",
    )
    return logical


def register(ctx: PluginContext) -> None:
    for cls in _CORE_COMPONENTS:
        logical = (
            f"{cls.distribution}:{cls.__module__}.{getattr(cls, 'logical_name', cls.__name__)}"
        )
        register_component(
            logical_id=logical,
            name=getattr(cls, "logical_name", cls.__name__) or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=getattr(cls, "props_type", type(None)).__name__,
            accessibility_notes="See feature manifest a11y_notes.",
        )

    asset_ids: list[str] = []
    for rel in (
        "assets/code_editor/editor.js",
        "assets/sandbox/bridge.js",
        "assets/terminal/terminal.js",
        "assets/image_tools/image.js",
        "assets/calendar/calendar.js",
        "assets/signature/signature.js",
        "assets/typeahead/typeahead.js",
        "assets/composition/composition.js",
    ):
        aid = _register_asset(rel)
        if aid:
            asset_ids.append(aid)

    for spec in _FEATURE_SPECS:
        assets = tuple(spec.get("assets") or ())
        ctx.register_feature(
            name=str(spec["name"]),
            stability=spec.get("stability", "beta"),  # type: ignore[arg-type]
            dependencies=tuple(spec.get("dependencies") or ()),
            assets=assets,
            a11y_notes=str(spec.get("a11y_notes") or ""),
            security_notes=str(spec.get("security_notes") or ""),
            http_fallback=bool(spec.get("http_fallback", True)),
            description=str(spec.get("description") or ""),
        )

    ctx.register_explorer_panel(
        panel_id="hedron-extras-features",
        title="Extras features",
        description="Curated extras feature manifests and stability labels",
        path="/hedron-explorer/extras",
    )
    ctx.register_diagnostic_owner("HED-EXTRAS-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
