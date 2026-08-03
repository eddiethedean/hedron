"""Build orchestration: compile HDN/CSS/assets into a versioned manifest."""

from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from hedron_core import __version__ as CORE_VERSION
from hedron_core.assets import build_asset_manifest, fingerprint_bytes, fingerprint_file
from hedron_core.css import compile_css
from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders
from hedron_core.hdn import compile_hdn
from hedron_core.manifests import (
    BUILD_MANIFEST_FORMAT,
    BuildManifest,
    CssSymbolManifest,
    write_json_atomic,
)
from hedron_core.registry import get_registry, update_component_meta
from hedron_core.theme import default_theme, emit_theme_css, ensure_default_theme_registered, get_theme

from hedron.config import HedronSettings, load_hedron_settings, settings_digest

try:
    from importlib.metadata import version as _pkg_version

    _hedron_version = _pkg_version("hedron")
except Exception:  # pragma: no cover
    _hedron_version = CORE_VERSION

__all__ = ["BuildResult", "run_build"]


@dataclass(frozen=True, slots=True)
class BuildResult:
    manifest: BuildManifest
    build_dir: Path
    css_bundle_path: Path | None


def run_build(
    *,
    project_dir: Path | None = None,
    settings: HedronSettings | None = None,
    production: bool = True,
) -> BuildResult:
    base = (project_dir or Path.cwd()).resolve()
    settings = settings or load_hedron_settings(base)
    ensure_default_theme_registered()

    roots = settings.resolved_roots(base=base)
    # Always include settings registered asset roots relative to base
    registered = list(roots)
    for root in settings.asset_policy.registered_roots:
        registered.append((base / root).resolve())

    discovered = discover_component_folders(roots)
    apply_discovery_to_registry(discovered)

    final_dir = settings.resolved_build_dir(base=base)
    final_dir.mkdir(parents=True, exist_ok=True)
    tmp_root = Path(tempfile.mkdtemp(prefix="hedron-build-"))
    try:
        assets_dir = tmp_root / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        hdn_dir = tmp_root / "hdn"
        hdn_dir.mkdir(parents=True, exist_ok=True)

        css_parts: list[str] = []
        # reset layer empty placeholder for deterministic order
        css_parts.append("@layer reset {\n}\n")

        theme_name = settings.theme or "default"
        theme_meta = get_theme(theme_name)
        if theme_meta is None:
            theme = default_theme()
        else:
            from hedron_core.theme import Theme

            theme = Theme(
                name=theme_meta.name,
                tokens=theme_meta.tokens,
                modes=theme_meta.modes,
                variants=theme_meta.variants,
            )
        css_parts.append(emit_theme_css(theme))
        css_parts.append("@layer base {\n}\n")

        css_symbols: list[CssSymbolManifest] = []
        hdn_programs: dict[str, str] = {}
        asset_entries = []

        registry = get_registry()
        for meta in registry.components():
            if meta.styles_path:
                source = Path(meta.styles_path)
                result = compile_css(
                    source.read_text(encoding="utf-8"),
                    component_id=meta.logical_id,
                    allow_remote=settings.asset_policy.allow_remote,
                    registered_roots=registered or [source.parent.resolve()],
                    component_dir=source.parent.resolve(),
                    production_names=production,
                )
                if any(d.severity.value == "error" for d in result.diagnostics):
                    from hedron_core.diagnostics import HedronError

                    raise HedronError(*result.diagnostics)
                css_parts.append(result.css)
                css_symbols.append(result.manifest)
                update_component_meta(
                    meta.logical_id,
                    style_symbols=dict(result.manifest.symbols),
                )
                # fingerprint referenced relative assets
                for rel in result.asset_urls:
                    if rel.startswith(("http://", "https://", "//", "data:")):
                        continue
                    asset_path = (source.parent / rel).resolve()
                    entry = fingerprint_file(
                        asset_path,
                        output_dir=assets_dir,
                        logical_id=f"{meta.logical_id}:{rel}",
                        kind="media",
                    )
                    asset_entries.append(entry)

            if meta.hdn_source:
                hdn_source = Path(meta.hdn_source).read_text(encoding="utf-8")
                compiled = compile_hdn(hdn_source)
                rel = f"hdn/{meta.name}.json"
                # store ops as simple JSON via program digest marker
                from hedron_core.manifests import canonical_json

                payload = {
                    "format_version": compiled.program.format_version,
                    "digest": compiled.digest,
                    "ops": [
                        {"kind": op.kind, "data": dict(op.data)} for op in compiled.program.ops
                    ],
                    "source_map": list(compiled.program.source_map),
                    "dependencies": list(compiled.program.dependencies),
                }
                out = hdn_dir / f"{meta.name}.json"
                out.write_text(canonical_json(payload) + "\n", encoding="utf-8")
                hdn_programs[meta.logical_id] = rel

            for browser_path in meta.browser_modules:
                path = Path(browser_path)
                entry = fingerprint_file(
                    path,
                    output_dir=assets_dir,
                    logical_id=f"{meta.logical_id}:browser",
                    kind="module",
                    attributes={"type": "module"},
                )
                asset_entries.append(entry)

        css_parts.append("@layer utilities {\n}\n")
        css_parts.append("@layer overrides {\n}\n")
        bundle = "".join(css_parts).encode("utf-8")
        css_entry = fingerprint_bytes(
            bundle,
            output_dir=assets_dir,
            logical_id="app:components.css",
            kind="css",
            filename_prefix="components",
            suffix=".css",
            content_type="text/css",
            attributes={"rel": "stylesheet"},
        )
        asset_entries.insert(0, css_entry)

        # First-party WC proof module if present in package
        try:
            from importlib import resources

            proof = Path(str(resources.files("hedron").joinpath("static/hedron-disclose.mjs")))
            if proof.is_file():
                asset_entries.append(
                    fingerprint_file(
                        proof,
                        output_dir=assets_dir,
                        logical_id="hedron:disclose",
                        kind="module",
                        attributes={"type": "module"},
                    )
                )
        except Exception:
            pass

        asset_manifest = build_asset_manifest(asset_entries)
        manifest = BuildManifest(
            format_version=BUILD_MANIFEST_FORMAT,
            theme=theme.name,
            assets=asset_manifest,
            css_symbols=tuple(css_symbols),
            hdn_programs=hdn_programs,
            tool_versions={
                "hedron": _hedron_version,
                "hedron-core": CORE_VERSION,
            },
            config_digest=settings_digest(settings),
        )

        # Write temp outputs
        write_json_atomic(tmp_root / "manifest.json", manifest.to_dict())
        write_json_atomic(tmp_root / "assets.json", asset_manifest.to_dict())
        for sym in css_symbols:
            write_json_atomic(
                tmp_root / "css-symbols" / f"{sym.component_id.replace(':', '_')}.json",
                sym.to_dict(),
            )

        # Atomic promote
        if final_dir.exists():
            backup = final_dir.with_suffix(".bak")
            if backup.exists():
                shutil.rmtree(backup)
            final_dir.rename(backup)
            try:
                tmp_root.rename(final_dir)
                shutil.rmtree(backup, ignore_errors=True)
            except Exception:
                if final_dir.exists():
                    shutil.rmtree(final_dir, ignore_errors=True)
                backup.rename(final_dir)
                raise
        else:
            tmp_root.rename(final_dir)

        css_path = final_dir / "assets" / css_entry.path
        loaded = BuildManifest.from_dict(
            __import__("json").loads((final_dir / "manifest.json").read_text(encoding="utf-8"))
        )
        loaded.validate_format()
        return BuildResult(manifest=loaded, build_dir=final_dir, css_bundle_path=css_path)
    except Exception:
        shutil.rmtree(tmp_root, ignore_errors=True)
        raise


def load_build_manifest(build_dir: Path) -> BuildManifest:
    path = build_dir / "manifest.json"
    if not path.is_file():
        from hedron_core.codes import HED_BUILD_MISSING_MANIFEST
        from hedron_core.diagnostics import error

        raise error(
            HED_BUILD_MISSING_MANIFEST,
            title="Build manifest missing",
            explanation=f"No manifest.json in {build_dir}.",
            remediation="Run `hedron build` before starting in production mode.",
        )
    import json

    manifest = BuildManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
    manifest.validate_format()
    return manifest
