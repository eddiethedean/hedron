"""Verify the external element-author plugin registers via public APIs."""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PLUGIN_ROOT.parents[1]
sys.path.insert(0, str(PLUGIN_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "hedron-core" / "src"))

from element_author_plugin.plugin import PLUGIN_META, register  # noqa: E402

from hedron_core.plugins import PluginContext  # noqa: E402
from hedron_core.registry import get_registry, reset_registry_for_tests  # noqa: E402


def main() -> int:
    reset_registry_for_tests()
    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    definition = get_registry().get_element_definition("element-author-plugin:author-probe")
    assert definition is not None
    assert definition.tag_name == "ext-author-probe"
    assert definition.first_party is False
    source = PLUGIN_ROOT / "src" / "element_author_plugin" / "plugin.py"
    text = source.read_text(encoding="utf-8")
    assert "from hedron_core.registry import register_element_definition" not in text
    assert "ctx.register_element_definition" in text
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
