"""Flagship catalog compiler, seal, production validation, and static inspect."""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path
from typing import cast

from hedron_core.catalog import (
    InteractionCatalog,
    InteractionManifest,
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


def app_interactions(app: object, *, sealed: bool = False) -> InteractionCatalog:
    cached = getattr(getattr(app, "state", None), "hedron_interactions", None)
    if isinstance(cached, InteractionCatalog):
        return cached
    live = get_sealed_catalog()
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    if live is not None and (not app_id or not live.app_id or live.app_id == app_id):
        return live
    if sealed:
        return seal_interaction_catalog(app_id=app_id or None)
    return compile_interaction_catalog(app_id=app_id or None)


def seal_app_catalog(app: object, *, profile: str = "production") -> InteractionCatalog:
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    catalog = seal_interaction_catalog(app_id=app_id or None, profile=profile)  # type: ignore[arg-type]
    state = getattr(app, "state", None)
    if state is not None:
        state.hedron_interactions = catalog
    return catalog


def emit_interactions_manifest(
    directory: Path,
    *,
    app_id: str | None = None,
    profile: str = "production",
) -> Path:
    catalog = compile_interaction_catalog(app_id=app_id, profile=profile)  # type: ignore[arg-type]
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
            from hedron_core.catalog import _catalog_error

            raise _catalog_error(
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
    for path in sorted(Path(root).rglob("*.py")):
        if any(
            part.startswith(".") or part in {"__pycache__", ".venv", "node_modules"}
            for part in path.parts
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
    return any(token in {"refreshable", "command"} for token in names)


def _is_command(decorators: Iterable[ast.AST]) -> bool:
    return any("command" in _decorator_names(item) for item in decorators)


def _decorator_names(node: ast.AST) -> tuple[str, ...]:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.Attribute):
        return (node.attr, *_decorator_names(node.value))
    if isinstance(node, ast.Call):
        return _decorator_names(node.func)
    return ()
