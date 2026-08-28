"""Contract tests for the composable satellite plugin boundary."""

from __future__ import annotations

import ast
import importlib
import tomllib
from pathlib import Path

import pytest

from hedron_core.plugins import PluginContext, PluginDefinition, PluginMeta

PLUGIN_MODULES = (
    "hedron_charts.plugin",
    "hedron_data.plugin",
    "hedron_elements.plugin",
    "hedron_extras.plugin",
    "hedron_extras.experimental",
    "hedron_extras.sandbox_plugin",
    "hedron_gradio.plugin",
    "hedron_maps.plugin",
    "hedron_mcp.plugin",
    "hedron_notebook.plugin",
    "hedron_sample_kit.plugin",
)

EXPECTED_CONTRIBUTIONS = {
    "hedron_charts.plugin": (
        "components",
        "primary-element",
        "runtime-assets",
        "vendor-hosts",
        "renderers",
        "catalog",
    ),
    "hedron_data.plugin": ("components", "editor-element", "catalog"),
    "hedron_elements.plugin": ("static-assets", "elements", "feature", "catalog"),
    "hedron_extras.plugin": ("assets", "components", "features", "catalog"),
    "hedron_extras.experimental": ("assets", "components", "features"),
    "hedron_extras.sandbox_plugin": ("asset", "component", "feature"),
    "hedron_gradio.plugin": ("feature", "catalog"),
    "hedron_maps.plugin": ("component", "map-element", "maplibre-assets", "catalog"),
    "hedron_mcp.plugin": ("feature", "catalog"),
    "hedron_notebook.plugin": ("feature",),
    "hedron_sample_kit.plugin": (
        "component",
        "explorer",
        "projection",
        "bundle",
        "variants",
    ),
}

PLUGIN_SATELLITE_DEPENDENCIES = {
    "hedron-charts": ("hedron-core>=1.0.0,<2.0",),
    "hedron-gradio": ("hedron-core>=1.0.0,<2.0",),
    "hedron-maps": ("hedron-core>=1.0.0,<2.0",),
    "hedron-mcp": ("hedron-core>=1.0.0,<2.0",),
    "hedron-notebook": ("hedron-core>=1.0.0,<2.0", "hedron>=1.0.0,<2.0"),
    "hedron-sample-kit": ("hedron-core>=1.0.0,<2.0",),
}

FORBIDDEN_REGISTRATION_IMPORTS = {
    "hedron_core.auto": {"register_renderer"},
    "hedron_core.registry": {
        "register_asset",
        "register_browser_module",
        "register_component",
        "register_element_definition",
    },
}

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("module_name", PLUGIN_MODULES)
def test_satellite_entry_points_delegate_to_plugin_definition(module_name: str) -> None:
    module = importlib.import_module(module_name)
    definition = module.PLUGIN

    assert isinstance(definition, PluginDefinition)
    assert module.register.PLUGIN_META is definition.meta
    assert definition.meta.hedron_version == ">=1.0,<2.0"
    assert (
        tuple(item.name for item in definition.contributions) == EXPECTED_CONTRIBUTIONS[module_name]
    )


@pytest.mark.parametrize("module_name", PLUGIN_MODULES)
def test_satellite_entry_points_only_register_through_context(module_name: str) -> None:
    module = importlib.import_module(module_name)
    source_path = Path(module.__file__ or "")
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

    violations: list[str] = []
    for node in ast.walk(tree):
        if (
            not isinstance(node, ast.ImportFrom)
            or node.module not in FORBIDDEN_REGISTRATION_IMPORTS
        ):
            continue
        forbidden = FORBIDDEN_REGISTRATION_IMPORTS[node.module]
        violations.extend(alias.name for alias in node.names if alias.name in forbidden)

    assert not violations, f"{module_name} bypasses PluginContext: {sorted(violations)}"


@pytest.mark.parametrize(("distribution", "required"), PLUGIN_SATELLITE_DEPENDENCIES.items())
def test_plugin_satellites_require_the_core_1_0_contract(
    distribution: str, required: tuple[str, ...]
) -> None:
    metadata = tomllib.loads(
        (ROOT / "packages" / distribution / "pyproject.toml").read_text(encoding="utf-8")
    )
    dependencies = metadata["project"]["dependencies"]

    assert all(requirement in dependencies for requirement in required)


def test_plugin_context_owns_renderer_registration(monkeypatch: pytest.MonkeyPatch) -> None:
    registered: list[object] = []
    renderer = object()
    monkeypatch.setattr("hedron_core.auto.register_renderer", registered.append)

    meta = PluginMeta(
        name="renderer-plugin",
        version="1.0.0",
        distribution="renderer-plugin",
        hedron_version=">=1.0,<2.0",
    )
    PluginContext(meta).register_renderer(renderer)

    assert registered == [renderer]


def test_plugin_definition_applies_contributions_in_declared_order() -> None:
    calls: list[str] = []
    meta = PluginMeta(
        name="test-plugin",
        version="1.0.0",
        distribution="test-plugin",
        hedron_version=">=1.0,<2.0",
    )
    definition = PluginDefinition.from_callbacks(
        meta,
        (
            ("first", lambda _ctx: calls.append("first")),
            ("second", lambda _ctx: calls.append("second")),
        ),
    )

    definition.register(PluginContext(meta))

    assert calls == ["first", "second"]


def test_plugin_definition_rejects_a_context_for_another_plugin() -> None:
    first = PluginMeta(
        name="first",
        version="1.0.0",
        distribution="first",
        hedron_version=">=1.0,<2.0",
    )
    second = PluginMeta(
        name="second",
        version="1.0.0",
        distribution="second",
        hedron_version=">=1.0,<2.0",
    )

    with pytest.raises(ValueError, match="does not match"):
        PluginDefinition(first).register(PluginContext(second))


def test_plugin_definition_rejects_duplicate_contribution_names() -> None:
    meta = PluginMeta(
        name="test-plugin",
        version="1.0.0",
        distribution="test-plugin",
        hedron_version=">=1.0,<2.0",
    )

    with pytest.raises(ValueError, match="unique"):
        PluginDefinition.from_callbacks(
            meta,
            (("same", lambda _ctx: None), ("same", lambda _ctx: None)),
        )
