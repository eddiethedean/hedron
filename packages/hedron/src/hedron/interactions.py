"""Flagship catalog compiler, seal, production validation, and static inspect."""

from __future__ import annotations

import ast
from collections.abc import Iterable
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path
from typing import cast

from hedron_core.catalog import (
    InteractionCatalog,
    InteractionManifest,
    RedactionProfile,
    compile_interaction_catalog,
    get_sealed_catalog,
    seal_interaction_catalog,
)
from hedron_core.codes import HED_CATALOG_0006
from hedron_core.typing_aliases import JsonObject

__all__ = [
    "app_interactions",
    "emit_interactions_manifest",
    "inspect_interactions_static",
    "seal_app_catalog",
    "validate_production_interactions",
]


def _runtime_scope(app: object) -> AbstractContextManager[object]:
    runtime = getattr(app, "_hedron_runtime", None)
    activate = getattr(runtime, "activate", None)
    if callable(activate):
        return cast(AbstractContextManager[object], activate())
    return nullcontext()


def app_interactions(app: object, *, sealed: bool = False) -> InteractionCatalog:
    cached = getattr(getattr(app, "state", None), "hedron_interactions", None)
    if isinstance(cached, InteractionCatalog):
        return cached
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    with _runtime_scope(app):
        live = get_sealed_catalog()
        if live is not None and (not app_id or not live.app_id or live.app_id == app_id):
            return live
        if sealed:
            return seal_interaction_catalog(app_id=app_id or None)
        return compile_interaction_catalog(app_id=app_id or None)


def seal_app_catalog(
    app: object, *, profile: RedactionProfile = "production"
) -> InteractionCatalog:
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    with _runtime_scope(app):
        catalog = seal_interaction_catalog(  # type: ignore[arg-type]
            app_id=app_id or None,
            profile=profile,
        )
    runtime = getattr(app, "_hedron_runtime", None)
    if runtime is not None:
        runtime.catalog = catalog
    state = getattr(app, "state", None)
    if state is not None:
        state.hedron_interactions = catalog
    return catalog


def emit_interactions_manifest(
    directory: Path,
    *,
    app: object | None = None,
    app_id: str | None = None,
    profile: RedactionProfile = "production",
) -> Path:
    resolved_app_id = app_id
    if app is not None and resolved_app_id is None:
        resolved_app_id = str(getattr(app, "hedron_app_id", "") or "") or None
    scope = _runtime_scope(app) if app is not None else nullcontext()
    with scope:
        catalog = compile_interaction_catalog(  # type: ignore[arg-type]
            app_id=resolved_app_id,
            profile=profile,
        )
    path = Path(directory) / "interactions.json"
    catalog.to_manifest(profile=profile).write_json(path)  # type: ignore[arg-type]
    return path


def validate_production_interactions(
    build_dir: Path,
    catalog: InteractionCatalog,
) -> InteractionManifest | None:
    path = Path(build_dir) / "interactions.json"
    if not path.is_file():
        if catalog.entries:
            from hedron_core.catalog import catalog_error

            raise catalog_error(
                HED_CATALOG_0006,
                title="Production interaction manifest missing",
                explanation=f"Production mode requires {path} when handlers are registered.",
                remediation=(
                    "Run `hedron build` with `--app` so interactions.json matches live handlers."
                ),
            )
        return None
    loaded = InteractionManifest.read_json(path)
    loaded.validate_against(catalog)
    return loaded


def inspect_interactions_static(
    root: Path,
    *,
    manifest: Path | None = None,
) -> JsonObject:
    """Read a manifest or scan sources without importing the target project."""
    if manifest is not None:
        loaded = InteractionManifest.read_json(manifest)
        payload = loaded.as_mapping()
        payload["provenance"] = {
            **dict(loaded.provenance),
            "mode": "static-manifest",
            "unknown": False,
        }
        return payload
    entries: list[JsonObject] = []
    source_root = Path(root)
    for path in sorted(source_root.rglob("*.py")):
        try:
            relative_parts = path.relative_to(source_root).parts
        except ValueError:
            relative_parts = path.parts
        if any(
            part.startswith(".") or part in {"__pycache__", ".venv", "node_modules"}
            for part in relative_parts
        ):
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(_is_handle_decorator(item) for item in node.decorator_list):
                kind = "command" if _is_command(node.decorator_list) else "view"
                entries.append(
                    {
                        "logical_id": node.name,
                        "kind": kind,
                        "descriptor_fingerprint": "unknown",
                        "effect_state": "unknown",
                        "provenance": {
                            "mode": "static-source",
                            "unknown": True,
                        },
                    }
                )
    return cast(
        JsonObject,
        {
            "format_version": 1,
            "profile": "development",
            "mode": "static",
            "unknown": True,
            "entries": entries,
            "projections": [],
            "diagnostics": ["static mode labels runtime-only facts unknown"],
            "provenance": {"mode": "static-source", "unknown": True},
        },
    )


def _is_handle_decorator(node: ast.AST) -> bool:
    names = _decorator_names(node)
    return any(token in {"view", "action", "refreshable", "command"} for token in names)


def _is_command(decorators: Iterable[ast.AST]) -> bool:
    return any(
        token in {"action", "command"} for item in decorators for token in _decorator_names(item)
    )


def _decorator_names(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        return (node.attr, *_decorator_names(node.value))
    if isinstance(node, ast.Call):
        return _decorator_names(node.func)
    return ()
