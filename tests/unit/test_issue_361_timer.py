"""#361: viewport debounce timeout must live on bag(el).timer."""

from __future__ import annotations

from hedron_maps.assets_047 import map_module_path


def test_viewport_timeout_uses_state_timer() -> None:
    src = map_module_path().read_text(encoding="utf-8")
    assert "let pending" not in src
    assert "state.timer = setTimeout" in src
    assert "if (state.timer) clearTimeout(state.timer)" in src
