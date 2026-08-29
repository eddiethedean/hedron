"""Component folder discovery."""

from __future__ import annotations

import importlib.util
import logging
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import TypeGuard, cast

from hedron_core.component import Component
from hedron_core.diagnostics import HedronError, error
from hedron_core.models import Props
from hedron_core.registry import (
    ComponentMeta,
    get_registry,
    register_browser_module,
    register_component,
    update_component_meta,
)

logger = logging.getLogger("hedron.discovery")

__all__ = ["DiscoveredComponent", "discover_component_folders", "load_component_module"]


def _is_component_class(value: object) -> TypeGuard[type[Component[Props]]]:
    return isinstance(value, type) and issubclass(value, Component) and value is not Component


@dataclass(frozen=True, slots=True)
class DiscoveredComponent:
    name: str
    folder: Path
    component_py: Path | None
    styles_css: Path | None
    browser_mjs: Path | None
    examples_py: Path | None


def discover_component_folders(roots: Sequence[Path]) -> tuple[DiscoveredComponent, ...]:
    found: list[DiscoveredComponent] = []
    for root in roots:
        root = root.resolve()
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith((".", "_")):
                continue
            component_py = child / "component.py"
            styles_css = child / "styles.css"
            browser_mjs = child / "browser.mjs"
            examples_py = child / "examples.py"
            if not any(p.is_file() for p in (component_py, styles_css, browser_mjs)):
                continue
            found.append(
                DiscoveredComponent(
                    name=child.name,
                    folder=child,
                    component_py=component_py if component_py.is_file() else None,
                    styles_css=styles_css if styles_css.is_file() else None,
                    browser_mjs=browser_mjs if browser_mjs.is_file() else None,
                    examples_py=examples_py if examples_py.is_file() else None,
                )
            )
    return tuple(found)


def load_component_module(path: Path, *, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise error(
            "HED-CONFIG-0003",
            title="Cannot load component module",
            explanation=f"Failed to load {path}.",
            remediation="Ensure component.py is a valid Python module.",
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def apply_discovery_to_registry(
    discovered: Sequence[DiscoveredComponent],
    *,
    distribution: str = "app",
) -> tuple[ComponentMeta, ...]:
    """Register/update components found in folders."""
    results: list[ComponentMeta] = []
    for item in discovered:
        logical_name = item.name
        module_name = f"hedron_discovered.{logical_name}"
        cls: type[Component[Props]] | None = None
        if item.component_py is not None:
            mod = load_component_module(item.component_py, module_name=module_name)
            candidate: object = getattr(mod, logical_name, None) or getattr(mod, "Component", None)
            if _is_component_class(candidate):
                cls = candidate
            if cls is None:
                # take first Component subclass
                namespace = cast(dict[str, object], vars(mod))
                for value in namespace.values():
                    if _is_component_class(value):
                        cls = value
                        break
        dist = distribution
        name = logical_name
        if cls is not None:
            dist = getattr(cls, "distribution", None) or distribution
            name = getattr(cls, "logical_name", None) or logical_name
        logical_id = f"{dist}:{module_name}.{name}"
        existing = get_registry().get(logical_id)
        browser_modules = ()
        if item.browser_mjs is not None:
            browser_modules = (str(item.browser_mjs),)
            tag = f"hedron-{logical_name.lower().replace('_', '-')}"
            try:
                register_browser_module(
                    logical_id=f"{logical_id}:browser",
                    tag_name=tag,
                    module_path=str(item.browser_mjs),
                )
            except HedronError as exc:
                if exc.diagnostic.code == "HED-ASSET-0010":
                    logger.warning(
                        "Skipping duplicate browser module %s: %s",
                        logical_id,
                        exc.diagnostic.title,
                    )
                else:
                    raise
        if existing is None and cls is not None:
            register_component(
                logical_id=logical_id,
                name=name,
                module=module_name,
                distribution=dist,
                props_model=getattr(getattr(cls, "props_type", None), "__name__", None),
                styles_path=str(item.styles_css) if item.styles_css else None,
                browser_modules=browser_modules,
                folder_path=str(item.folder),
                asset_roots=(str(item.folder),),
            )
        elif existing is not None:
            update_component_meta(
                logical_id,
                styles_path=str(item.styles_css) if item.styles_css else None,
                browser_modules=browser_modules,
                folder_path=str(item.folder),
                asset_roots=(str(item.folder),),
            )
        elif item.styles_css or item.browser_mjs:
            register_component(
                logical_id=logical_id,
                name=logical_name,
                module=module_name,
                distribution=dist,
                styles_path=str(item.styles_css) if item.styles_css else None,
                browser_modules=browser_modules,
                folder_path=str(item.folder),
                asset_roots=(str(item.folder),),
            )
        meta = get_registry().get(logical_id)
        if meta is not None:
            results.append(meta)
    return tuple(results)
