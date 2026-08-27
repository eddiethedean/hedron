"""PLUGIN-040 external element consumer contracts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from hedron.plugins import load_plugins
from hedron_core import get_registry
from hedron_core.diagnostics import HedronError
from hedron_core.plugins import PluginContext, PluginMeta
from hedron_core.registry import reset_registry_for_tests

ROOT = Path(__file__).resolve().parents[2]
_CONSUMER_SRC = ROOT / "examples" / "element-author-plugin" / "src"
VERIFY = ROOT / "examples" / "element-author-plugin" / "verify_consumer.py"
sys.path.insert(0, str(_CONSUMER_SRC))

from element_author_plugin.plugin import register as register_consumer  # noqa: E402

LOGICAL_ID = "element-author-plugin:author-probe"


class _EntryPoint:
    def __init__(self, name: str, target: object) -> None:
        self.name = name
        self._target = target

    def load(self) -> object:
        return self._target


def test_external_consumer_loads_and_can_be_disabled() -> None:
    reset_registry_for_tests()
    entry_point = _EntryPoint("element_author_plugin", register_consumer)
    disabled = load_plugins(enabled=[], entry_points=[entry_point])
    assert disabled.loaded == []
    assert get_registry().get_element_definition(LOGICAL_ID) is None

    enabled = load_plugins(enabled=["element_author_plugin"], entry_points=[entry_point])
    assert [item.meta.name for item in enabled.loaded] == ["element_author_plugin"]
    definition = get_registry().get_element_definition(LOGICAL_ID)
    assert definition is not None
    assert definition.tag_name == "ext-author-probe"
    assert definition.first_party is False
    source = _CONSUMER_SRC / "element_author_plugin" / "plugin.py"
    text = source.read_text(encoding="utf-8")
    assert "ctx.register_element_definition" in text
    assert "from hedron_core.registry import register_element_definition" not in text


def _plugin(name: str, logical_id: str, tag_name: str):
    def register(ctx: PluginContext) -> None:
        ctx.register_element_definition(
            logical_id=logical_id,
            tag_name=tag_name,
            abi_version=1,
            module_asset_id=f"{name}:module",
        )

    register.PLUGIN_META = PluginMeta(  # type: ignore[attr-defined]
        name=name,
        version="0.1.0",
        distribution=name,
        hedron_version=">=0.67,<2.0",
    )
    return register


@pytest.mark.parametrize(
    ("second_logical_id", "second_tag"),
    (
        ("plugin-two:other", "ext-shared"),
        ("plugin-one:probe", "ext-other"),
    ),
)
def test_element_definition_conflicts_roll_back(
    second_logical_id: str,
    second_tag: str,
) -> None:
    reset_registry_for_tests()
    first = _plugin("plugin_one", "plugin-one:probe", "ext-shared")
    second = _plugin("plugin_two", second_logical_id, second_tag)
    with pytest.raises(HedronError) as exc:
        load_plugins(
            entry_points=[
                _EntryPoint("plugin_one", first),
                _EntryPoint("plugin_two", second),
            ]
        )
    assert exc.value.diagnostic.code == "HED-ELEMENT-0001"
    assert get_registry().get_element_definition("plugin-one:probe") is None


def test_verify_consumer_script() -> None:
    completed = subprocess.run(
        [sys.executable, str(VERIFY)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "ok" in completed.stdout
