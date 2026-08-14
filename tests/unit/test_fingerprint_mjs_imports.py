"""Fingerprinted ES modules must keep relative imports reachable (#214)."""

from __future__ import annotations

from pathlib import Path

from hedron.build import _relink_fingerprinted_modules, _rewrite_module_imports
from hedron_core.assets import fingerprint_file
from hedron_core.registry import reset_registry_for_tests
from hedron_elements.assets import bridge_path, example_module_path
from hedron_elements.plugin import register as register_elements


def test_rewrite_module_imports_maps_relative_specifiers() -> None:
    src = 'import { track } from "./hedron-bridge.mjs";\nexport { x } from "./other.mjs";\n'
    out = _rewrite_module_imports(
        src,
        {
            "hedron-bridge.mjs": "hedron-bridge.abc123.mjs",
            "other.mjs": "other.def456.mjs",
        },
    )
    assert 'from "./hedron-bridge.abc123.mjs"' in out
    assert 'from "./other.def456.mjs"' in out
    assert "./hedron-bridge.mjs" not in out


def test_fingerprint_alone_leaves_unhashed_import(tmp_path: Path) -> None:
    """Document the copy-only fingerprint gap that #214 fixes in the build relink pass."""
    src = Path("packages/hedron-elements/src/hedron_elements/static")
    example = fingerprint_file(
        src / "hedron-example.mjs",
        output_dir=tmp_path,
        logical_id="e",
        kind="module",
    )
    bridge = fingerprint_file(
        src / "hedron-bridge.mjs",
        output_dir=tmp_path,
        logical_id="b",
        kind="module",
    )
    text = (tmp_path / example.path).read_text(encoding="utf-8")
    assert "./hedron-bridge.mjs" in text
    assert not (tmp_path / "hedron-bridge.mjs").exists()
    assert (tmp_path / bridge.path).exists()


def test_relink_rewrites_elements_example_to_hashed_bridge(tmp_path: Path) -> None:
    example_src = example_module_path()
    bridge_src = bridge_path()
    assert example_src.is_file() and bridge_src.is_file()

    example = fingerprint_file(
        example_src,
        output_dir=tmp_path,
        logical_id="hedron-elements:example.mjs",
        kind="module",
        attributes={"type": "module"},
    )
    bridge = fingerprint_file(
        bridge_src,
        output_dir=tmp_path,
        logical_id="hedron-elements:bridge.mjs",
        kind="module",
        attributes={"type": "module"},
    )
    entries = [example, bridge]
    basename_by_path = {
        example.path: example_src.name,
        bridge.path: bridge_src.name,
    }
    _relink_fingerprinted_modules(tmp_path, entries, basename_by_path=basename_by_path)

    example_entry = next(e for e in entries if "example" in e.logical_id)
    bridge_entry = next(e for e in entries if "bridge" in e.logical_id)
    text = (tmp_path / example_entry.path).read_text(encoding="utf-8")

    assert f'from "./{bridge_entry.path}"' in text
    assert "./hedron-bridge.mjs" not in text
    assert (tmp_path / bridge_entry.path).is_file()
    assert (tmp_path / example_entry.path).is_file()
    # Importer was re-emitted so the fingerprinted name tracks rewritten bytes.
    assert example_entry.path != example.path or example_entry.digest != example.digest


def test_production_build_relinks_elements_modules(tmp_path: Path) -> None:
    from hedron.build import run_build
    from hedron.config import HedronSettings

    class _Ctx:
        def register_diagnostic_owner(self, prefix: str) -> None:
            self.prefix = prefix

        def register_feature(self, **kwargs: object) -> None:
            self.feature = kwargs

        def register_explorer_panel(self, **kwargs: object) -> None:
            return None

    reset_registry_for_tests()
    try:
        register_elements(_Ctx())  # type: ignore[arg-type]
        result = run_build(
            project_dir=tmp_path,
            settings=HedronSettings(
                build_dir=".hedron/build",
                theme="default",
                plugins=(),
            ),
            production=True,
        )
    finally:
        reset_registry_for_tests()

    assets = result.build_dir / "assets"
    example_files = list(assets.glob("hedron-example.*.mjs"))
    bridge_files = list(assets.glob("hedron-bridge.*.mjs"))
    assert example_files, "expected fingerprinted hedron-example module"
    assert bridge_files, "expected fingerprinted hedron-bridge module"
    text = example_files[0].read_text(encoding="utf-8")
    assert f'from "./{bridge_files[0].name}"' in text
    assert "./hedron-bridge.mjs" not in text
