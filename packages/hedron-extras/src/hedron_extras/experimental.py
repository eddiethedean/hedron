"""Experimental UI landmines quarantined from ``hedron[extras]`` (EXTRAS-025).

Install ``hedron[experimental-ui]`` and either set ``HEDRON_EXPERIMENTAL_UI=1`` or
enable the ``hedron_extras_experimental`` plugin explicitly. Do not treat these
surfaces as product UI under ``hedron[extras]``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_core.codes import HED_ASSET_MISSING
from hedron_core.diagnostics import error
from hedron_core.identifiers import content_digest
from hedron_core.plugins import (
    PluginCapabilities,
    PluginContext,
    PluginDefinition,
    PluginMeta,
)
from hedron_extras.specialty import DeviceBridge, Joystick, TerminalPolicy, TerminalView
from hedron_extras.workbench import CodeEditor

__all__ = [
    "CodeEditor",
    "DeviceBridge",
    "Joystick",
    "PLUGIN_META",
    "TerminalPolicy",
    "TerminalView",
    "register",
]

_ROOT = Path(__file__).resolve().parent

PLUGIN_META = PluginMeta(
    name="hedron_extras_experimental",
    version="1.0.6",
    distribution="hedron-extras",
    hedron_version=">=1.0,<2.0",
    depends_on=("hedron_extras",),
    capabilities=PluginCapabilities(
        python=True,
        styles=False,
        assets=True,
        browser_js=True,
        explorer_panels=False,
    ),
)

_BROWSER_HOSTS: tuple[tuple[str, str, str, tuple[type[Any], ...]], ...] = (
    (
        "assets/code_editor/editor.js",
        "hedron-extras:code-editor",
        "hedron-extras-code-editor",
        (CodeEditor,),
    ),
    (
        "assets/terminal/terminal.js",
        "hedron-extras:terminal",
        "hedron-extras-terminal",
        (TerminalView,),
    ),
)

_STATIC_COMPONENTS: tuple[type[Any], ...] = (
    Joystick,
    DeviceBridge,
)


def _asset_logical_id(rel: str) -> str:
    return f"hedron-extras:{rel.replace('/', '.')}"


def _module_asset(rel: str) -> tuple[str, Path]:
    path = _ROOT / rel
    if not path.is_file():
        raise error(
            HED_ASSET_MISSING,
            title="Extras experimental browser asset missing",
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
    for rel, _module_id, _tag_name, _classes in _BROWSER_HOSTS:
        _register_module_asset(ctx, rel)


def _register_components(ctx: PluginContext) -> None:
    """Register EXTRAS-025 landmines (CodeEditor / TerminalView / joystick / device)."""
    module_by_cls: dict[type[Any], str] = {}

    for rel, module_id, tag_name, classes in _BROWSER_HOSTS:
        _, path = _module_asset(rel)
        ctx.register_browser_module(
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
        ctx.register_component(
            logical_id=logical,
            name=getattr(cls, "logical_name", cls.__name__) or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=getattr(cls, "props_type", type(None)).__name__,
            browser_modules=modules,
            accessibility_notes="Experimental landmine — see hedron[experimental-ui].",
        )


def _register_features(ctx: PluginContext) -> None:
    feature_specs: tuple[dict[str, Any], ...] = (
        {
            "name": "code_editor",
            "stability": "experimental",
            "description": "CodeEditor CSP-safe host stub (no pinned CodeMirror 6)",
            "assets": (_asset_logical_id("assets/code_editor/editor.js"),),
            "http_fallback": True,
            "a11y_notes": "Textarea fallback; host stub only.",
            "security_notes": "CodeEditor never evaluates buffers.",
        },
        {
            "name": "terminal",
            "stability": "experimental",
            "assets": (_asset_logical_id("assets/terminal/terminal.js"),),
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
            "security_notes": "Command allowlist; host must enforce CSRF on mutating posts.",
        },
    )

    for spec in feature_specs:
        ctx.register_feature(
            name=str(spec["name"]),
            stability=spec.get("stability", "experimental"),  # type: ignore[arg-type]
            dependencies=tuple(spec.get("dependencies") or ()),
            assets=tuple(spec.get("assets") or ()),
            a11y_notes=str(spec.get("a11y_notes") or ""),
            security_notes=str(spec.get("security_notes") or ""),
            http_fallback=bool(spec.get("http_fallback", True)),
            description=str(spec.get("description") or ""),
        )


PLUGIN = PluginDefinition.from_callbacks(
    PLUGIN_META,
    (
        ("assets", _register_assets),
        ("components", _register_components),
        ("features", _register_features),
    ),
)


def register(ctx: PluginContext) -> None:
    PLUGIN.register(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
