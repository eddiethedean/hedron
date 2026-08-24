"""Build orchestration: compile CSS/assets into a versioned manifest."""

from __future__ import annotations

import json
import os
import shutil
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedron.build.fingerprint import _relink_fingerprinted_modules
from hedron.build.manifest import _write_build_manifest
from hedron.build.rewrite import _rewrite_css_urls
from hedron.config import HedronSettings, load_hedron_settings, settings_digest
from hedron_core import __version__ as CORE_VERSION
from hedron_core.assets import build_asset_manifest, fingerprint_bytes, fingerprint_file
from hedron_core.codes import HED_THEME_UNKNOWN
from hedron_core.css import compile_css
from hedron_core.diagnostics import error
from hedron_core.discovery import apply_discovery_to_registry, discover_component_folders
from hedron_core.manifests import (
    BUILD_MANIFEST_FORMAT,
    BuildManifest,
    CssSymbolManifest,
)
from hedron_core.registry import get_registry, update_component_meta
from hedron_core.theme import (
    Theme,
    default_theme,
    emit_theme_css,
    ensure_default_theme_registered,
    get_theme,
)
from hedron_core.theme_contract import (
    component_contract_manifest,
    package_identity_manifest,
    resolve_theme,
)

try:
    from importlib.metadata import version as _pkg_version

    _hedron_version = _pkg_version("hedron")
except Exception:  # pragma: no cover  # noqa: BLE001
    _hedron_version = CORE_VERSION

_BUILD_LOCKS_GUARD = threading.Lock()
_BUILD_LOCKS: dict[Path, threading.RLock] = {}


@dataclass(frozen=True, slots=True)
class BuildResult:
    manifest: BuildManifest
    build_dir: Path
    css_bundle_path: Path | None


def _atomic_promote(tmp_root: Path, final_dir: Path) -> None:
    """Promote tmp_root to final_dir using same-device renames only."""
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if final_dir.exists():
        backup = final_dir.parent / f".hedron-build-bak-{uuid.uuid4().hex}"
        final_dir.rename(backup)
    try:
        tmp_root.rename(final_dir)
    except Exception:
        if final_dir.exists():
            shutil.rmtree(final_dir, ignore_errors=True)
        if backup is not None and backup.exists():
            backup.rename(final_dir)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)


@contextmanager
def _build_lock(final_dir: Path):
    """Serialize builds for one output directory across threads and processes."""
    lock_path = final_dir.parent / f".{final_dir.name}.lock"
    with _BUILD_LOCKS_GUARD:
        thread_lock = _BUILD_LOCKS.setdefault(lock_path, threading.RLock())
    with thread_lock:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+b") as lock_file:
            if os.name == "nt":  # pragma: no cover - exercised on Windows
                import msvcrt

                lock_file.seek(0)
                lock_file.write(b"\\0")
                lock_file.flush()
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
                try:
                    yield
                finally:
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def run_build(
    *,
    project_dir: Path | None = None,
    settings: HedronSettings | None = None,
    production: bool = True,
    assets_url_prefix: str = "/hedron-assets",
) -> BuildResult:
    from hedron_core.compile_gate import force_runtime_compile

    with force_runtime_compile():
        return _run_build(
            project_dir=project_dir,
            settings=settings,
            production=production,
            assets_url_prefix=assets_url_prefix,
        )


def _style_component_id(meta: Any) -> str:
    import sys

    mod = sys.modules.get(meta.module)
    if mod is not None:
        sid = getattr(mod, "STYLE_COMPONENT_ID", None)
        if isinstance(sid, str) and sid:
            return sid
        cls = getattr(mod, meta.name, None)
        if cls is not None:
            sid = getattr(cls, "STYLE_COMPONENT_ID", None)
            if isinstance(sid, str) and sid:
                return sid
    return meta.logical_id


def _run_build(
    *,
    project_dir: Path | None = None,
    settings: HedronSettings | None = None,
    production: bool = True,
    assets_url_prefix: str = "/hedron-assets",
) -> BuildResult:
    base = (project_dir or Path.cwd()).resolve()
    settings = settings or load_hedron_settings(base)
    final_dir = settings.resolved_build_dir(base=base)
    with _build_lock(final_dir):
        return _run_build_locked(
            base=base,
            settings=settings,
            production=production,
            assets_url_prefix=assets_url_prefix,
        )


def _run_build_locked(
    *,
    base: Path,
    settings: HedronSettings,
    production: bool,
    assets_url_prefix: str,
) -> BuildResult:
    ensure_default_theme_registered()

    roots = settings.resolved_roots(base=base)
    registered = [r.resolve() for r in roots]
    for root in settings.asset_policy.registered_roots:
        registered.append((base / root).resolve())

    from hedron_core import plugins as plugins_mod
    from hedron_core.registry import restore_registry_builder, snapshot_registry_builder

    # Build may register discovered + plugin components; restore afterward so an
    # in-process app lifespan can load plugins without duplicate registration.
    registry_snapshot = snapshot_registry_builder()
    panel_snapshot = dict(plugins_mod._panels)
    owner_snapshot = dict(plugins_mod._diagnostic_owners)
    from hedron_core.catalog import restore_projection_providers, snapshot_projection_providers

    provider_snapshot = snapshot_projection_providers()

    def _restore_registry() -> None:
        restore_registry_builder(registry_snapshot)
        plugins_mod._panels.clear()
        plugins_mod._panels.update(panel_snapshot)
        plugins_mod._diagnostic_owners.clear()
        plugins_mod._diagnostic_owners.update(owner_snapshot)
        restore_projection_providers(provider_snapshot)

    try:
        discovered = discover_component_folders(roots)
        apply_discovery_to_registry(discovered)

        from hedron.plugins import load_plugins
        from hedron_core.production_gate import resolve_production_plugins

        # Match runtime lifespan: production deny-by-default when plugins omitted.
        enabled = resolve_production_plugins(
            None if settings.plugins is None else list(settings.plugins),
            production=production,
        )
        load_plugins(enabled=enabled)

        return _execute_build(
            base=base,
            settings=settings,
            production=production,
            assets_url_prefix=assets_url_prefix,
            registered=registered,
        )
    finally:
        _restore_registry()


def _execute_build(
    *,
    base: Path,
    settings: HedronSettings,
    production: bool,
    assets_url_prefix: str,
    registered: list[Path],
) -> BuildResult:
    final_dir = settings.resolved_build_dir(base=base)
    final_dir.parent.mkdir(parents=True, exist_ok=True)
    # Same filesystem as final_dir to avoid Errno 18 cross-device rename.
    tmp_root = final_dir.parent / f".hedron-build-tmp-{uuid.uuid4().hex}"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)
    try:
        assets_dir = tmp_root / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        css_parts: list[str] = ["@layer reset {\n}\n"]

        theme_name = settings.theme or "default"
        theme_meta = get_theme(theme_name)
        if theme_meta is None:
            if theme_name != "default":
                raise error(
                    HED_THEME_UNKNOWN,
                    title="Unknown theme",
                    explanation=f"Theme {theme_name!r} is not registered.",
                    remediation='Register the theme or set theme = "default".',
                )
            theme = default_theme()
        else:
            theme = Theme(
                name=theme_meta.name,
                tokens=theme_meta.tokens,
                modes=theme_meta.modes,
                variants=theme_meta.variants,
            )
        css_parts.append(emit_theme_css(theme))
        css_parts.append("@layer base {\n}\n")

        css_symbols: list[CssSymbolManifest] = []
        asset_entries = []
        module_basename_by_path: dict[str, str] = {}

        registry = get_registry()
        for meta in registry.components():
            style_id = _style_component_id(meta)
            if meta.styles_path:
                source = Path(meta.styles_path)
                component_root = source.parent.resolve()
                roots_for_css = registered or [component_root]
                result = compile_css(
                    source.read_text(encoding="utf-8"),
                    component_id=style_id,
                    allow_remote=settings.asset_policy.allow_remote,
                    registered_roots=roots_for_css,
                    component_dir=component_root,
                    production_names=production,
                )
                if any(d.severity.value == "error" for d in result.diagnostics):
                    from hedron_core.diagnostics import HedronError

                    raise HedronError(*result.diagnostics)
                css_text = result.css
                local_rewrites: dict[str, str] = {}
                for rel in result.asset_urls:
                    if rel.startswith(("http://", "https://", "//", "data:", "/")):
                        continue
                    asset_path = (source.parent / rel).resolve()
                    entry = fingerprint_file(
                        asset_path,
                        output_dir=assets_dir,
                        logical_id=f"{meta.logical_id}:{rel}",
                        kind="media",
                    )
                    asset_entries.append(entry)
                    public = f"{assets_url_prefix.rstrip('/')}/{entry.path}"
                    local_rewrites[rel] = public
                if local_rewrites:
                    css_text = _rewrite_css_urls(css_text, local_rewrites)
                css_parts.append(css_text)
                css_symbols.append(result.manifest)
                update_component_meta(
                    meta.logical_id,
                    style_symbols=dict(result.manifest.symbols),
                )

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
                module_basename_by_path[entry.path] = path.name

        # Plugin/package assets registered via register_asset (e.g. DataEditor CSS).
        component_browser_paths = {
            Path(bp).resolve() for meta in registry.components() for bp in meta.browser_modules
        }
        for asset in registry.assets():
            path = Path(asset.path)
            if not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in component_browser_paths:
                continue
            attrs = dict(asset.attributes)
            if asset.kind == "css":
                attrs.setdefault("rel", "stylesheet")
            entry = fingerprint_file(
                path,
                output_dir=assets_dir,
                logical_id=asset.logical_id,
                kind=asset.kind,
                attributes=attrs,
            )
            asset_entries.append(entry)
            if asset.kind == "module":
                module_basename_by_path[entry.path] = path.name

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

        from importlib import resources

        from hedron_core.diagnostics import HedronError

        try:
            proof = Path(str(resources.files("hedron").joinpath("static/hedron-disclose.mjs")))
            if proof.is_file():
                disclose_entry = fingerprint_file(
                    proof,
                    output_dir=assets_dir,
                    logical_id="hedron:disclose",
                    kind="module",
                    attributes={"type": "module"},
                )
                asset_entries.append(disclose_entry)
                module_basename_by_path[disclose_entry.path] = proof.name
        except HedronError:
            raise
        except OSError as exc:
            import logging

            logging.getLogger("hedron.build").warning(
                "Could not fingerprint hedron-disclose.mjs: %s",
                exc,
            )

        _relink_fingerprinted_modules(
            assets_dir,
            asset_entries,
            basename_by_path=module_basename_by_path,
        )

        asset_manifest = build_asset_manifest(asset_entries)
        manifest = BuildManifest(
            format_version=BUILD_MANIFEST_FORMAT,
            theme=theme.name,
            assets=asset_manifest,
            css_symbols=tuple(css_symbols),
            tool_versions={
                "hedron": _hedron_version,
                "hedron-core": CORE_VERSION,
            },
            config_digest=settings_digest(settings),
            theme_resolution_digest=resolve_theme(theme).fingerprint,
            component_manifest_digest=component_contract_manifest()["digest"],
            package_identity_digest=package_identity_manifest()["digest"],
        )

        _write_build_manifest(
            tmp_root,
            manifest=manifest,
            asset_manifest=asset_manifest,
            css_symbols=css_symbols,
        )
        from hedron.interactions import emit_interactions_manifest

        profile = "production" if production else "development"
        emit_interactions_manifest(tmp_root, profile=profile)

        _atomic_promote(tmp_root, final_dir)
        # Ownership transferred; avoid deleting promoted tree in finally.
        tmp_root = Path("/nonexistent-hedron-tmp")

        css_path = final_dir / "assets" / css_entry.path
        loaded = BuildManifest.from_dict(
            json.loads((final_dir / "manifest.json").read_text(encoding="utf-8"))
        )
        loaded.validate_format()
        return BuildResult(manifest=loaded, build_dir=final_dir, css_bundle_path=css_path)
    except Exception:
        if tmp_root.exists() and tmp_root.name.startswith(".hedron-build-tmp-"):
            shutil.rmtree(tmp_root, ignore_errors=True)
        raise
