"""Load and write versioned build manifests."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from hedron_core.diagnostics import error
from hedron_core.manifests import (
    AssetManifest,
    BuildManifest,
    CssSymbolManifest,
    write_json_atomic,
)


def _artifact_stem(logical_id: str) -> str:
    return logical_id.replace(":", "__").replace("/", "_").replace("\\", "_")


def _write_build_manifest(
    tmp_root: Path,
    *,
    manifest: BuildManifest,
    asset_manifest: AssetManifest,
    css_symbols: Sequence[CssSymbolManifest],
) -> None:
    write_json_atomic(tmp_root / "manifest.json", manifest.to_dict())
    write_json_atomic(tmp_root / "assets.json", asset_manifest.to_dict())
    for sym in css_symbols:
        write_json_atomic(
            tmp_root / "css-symbols" / f"{_artifact_stem(sym.component_id)}.json",
            sym.to_dict(),
        )


def load_build_manifest(build_dir: Path) -> BuildManifest:
    path = build_dir / "manifest.json"
    if not path.is_file():
        from hedron_core.codes import HED_BUILD_MISSING_MANIFEST

        raise error(
            HED_BUILD_MISSING_MANIFEST,
            title="Build manifest missing",
            explanation=f"No manifest.json in {build_dir}.",
            remediation="Run `hedron build` before starting in production mode.",
        )
    manifest = BuildManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
    manifest.validate_format()
    return manifest
