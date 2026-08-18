"""#362: failed MapLibre runtime scripts must not hang remount."""

from __future__ import annotations

from hedron_maps.assets_047 import map_module_path


def test_load_script_retries_failed_runtime_and_is_abortable() -> None:
    src = map_module_path().read_text(encoding="utf-8")
    assert "data-hedron-maplibre-error" in src
    assert "existing.remove()" in src
    assert "signal.addEventListener" in src
    assert src.count("once: true, signal") >= 2
