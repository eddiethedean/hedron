"""CLI commands: style explain / preview / diff / eject (phase 0.58)."""

from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from hedron.cli.discovery import _load_app
from hedron_core.codes import HED_STYLE_EJECT_0002
from hedron_core.css.compiler import compile_css
from hedron_core.css.layers import CASCADE_LAYERS
from hedron_core.design_system import BUILTIN_RECIPES, DesignSystem, DesignSystemPlan
from hedron_core.diagnostics import HedronError, error
from hedron_core.presentation_064 import application_style_hook_manifest
from hedron_core.registry import get_registry
from hedron_core.theme import (
    Theme,
    builtin_themes,
    emit_theme_css,
    ensure_builtin_themes_registered,
    get_theme,
)
from hedron_core.theme_platform import ThemeSpec, conformance_report, package_theme
from hedron_core.typing_aliases import JsonObject

DIFF_SCHEMA = "hedron.design-system-diff/1"
PREVIEW_SCHEMA = "hedron.design-system-preview/1"
SOURCE_MAP_SCHEMA = "hedron.design-system-source-map/1"
PREVIEW_FIXTURE_VERSION = "hedron.design-gallery/1"
APPLICATION_STYLE_EJECTION_SCHEMA = "hedron.style-ejection/1"


def _require_app(args: argparse.Namespace) -> object:
    app_path = getattr(args, "app", None)
    if not app_path:
        raise SystemExit("hedron style commands require --app module:attr")
    app = _load_app(app_path)
    if app is None:
        raise SystemExit(f"Could not load --app {app_path!r}")
    return app


def _theme_from_meta(name: str) -> Theme:
    ensure_builtin_themes_registered()
    for theme in builtin_themes():
        if theme.name == name:
            return theme
    meta = get_theme(name)
    if meta is None:
        known = ", ".join(sorted(t.name for t in builtin_themes()))
        raise SystemExit(f"Unknown design/theme {name!r} (known builtins: {known})")
    return Theme(
        name=meta.name,
        tokens=dict(meta.tokens),
        modes={k: dict(v) for k, v in meta.modes.items()},
        variants={k: dict(v) for k, v in meta.variants.items()},
    )


def _resolve_design(args: argparse.Namespace, *, name: str | None = None) -> DesignSystem:
    """Resolve a DesignSystem from --design, app theme, or an explicit name."""
    app = getattr(args, "_hedron_app", None)
    if app is None and getattr(args, "app", None):
        app = _require_app(args)
        args._hedron_app = app
    stored = None
    if app is not None:
        state = getattr(app, "state", None)
        stored = getattr(state, "hedron_design_system", None)
        if stored is None:
            stored = getattr(app, "hedron_design_system", None)
    design_name = name
    if design_name is None:
        design_name = getattr(args, "design", None)
    if design_name is None and isinstance(stored, DesignSystem):
        return stored
    if design_name is None and app is not None:
        design_name = getattr(app, "hedron_theme", None) or getattr(
            getattr(app, "state", None), "hedron_theme", None
        )
    if not design_name:
        design_name = "default"
    if isinstance(stored, DesignSystem) and stored.name == design_name:
        return stored
    return DesignSystem.from_theme(_theme_from_meta(str(design_name)))


def _assert_project_write_path(path: Path, *, cwd: Path) -> Path:
    """Resolve ``path`` under ``cwd`` and refuse symlink write-through escapes."""
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(cwd)
    except ValueError as exc:
        raise ValueError(f"Refusing to write outside the project root: {resolved}") from exc
    cursor = resolved
    while True:
        if cursor.exists() and cursor.is_symlink():
            raise ValueError(f"Refusing to write through symlink: {cursor}")
        if cursor == cwd or cursor.parent == cursor:
            break
        cursor = cursor.parent
    return resolved


def _plan_human(plan: DesignSystemPlan) -> str:
    lines = [
        f"Design {plan.logical_id}",
        f"schema: {plan.schema}",
        f"base_theme: {plan.base_theme}",
        f"digest: {plan.digest}",
        f"inputs: {json.dumps(dict(plan.inputs), sort_keys=True)}",
        f"groups: {json.dumps(dict(plan.groups), sort_keys=True)}",
        f"recipes: {len(plan.recipes)}",
        f"provenance: {len(plan.provenance)}",
        f"adjustments: {len(plan.adjustments)}",
        f"limitations: {', '.join(plan.limitations) or '(none)'}",
    ]
    return "\n".join(lines)


def _cmd_style_explain(args: argparse.Namespace) -> int:
    surface = getattr(args, "surface", None)
    if surface:
        if getattr(args, "app", None):
            _require_app(args)
        parts = surface.split(".", 1)
        hooks = application_style_hook_manifest()
        component = parts[0]
        part = parts[1] if len(parts) == 2 else None
        hook = hooks.get(component)
        part_map = hook.get("parts") if isinstance(hook, Mapping) else None
        known = isinstance(part_map, Mapping) and (part is None or part in part_map)
        payload = {
            "schema": "hedron.style-explanation/1",
            "surface": surface,
            "property": getattr(args, "property", None),
            "known_public_hook": known,
            "cascade_layers": list(CASCADE_LAYERS),
            "diagnostics": [] if known else [f"Unknown public style hook: {surface}"],
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(f"Surface: {surface}")
            print(f"Public hook: {'yes' if known else 'no'}")
            print("Cascade: " + " < ".join(CASCADE_LAYERS))
            if not known:
                print(f"Unknown public style hook: {surface}", file=sys.stderr)
        return 0 if known else 1
    design = _resolve_design(args)
    plan = design.explain()
    if args.format == "json":
        print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        print(_plan_human(plan))
    return 0


def _cmd_style_inspect(args: argparse.Namespace) -> int:
    """Emit the resolved application-style catalog and public hook contract."""
    if getattr(args, "app", None):
        _require_app(args)
    registry = get_registry()
    styles = [style.to_dict() for style in registry.application_styles()]
    payload = {
        "schema": "hedron.style-inspection/1",
        "cascade_layers": list(CASCADE_LAYERS),
        "application_styles": styles,
        "application_style_hooks": application_style_hook_manifest(),
        "diagnostics": [],
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Cascade: " + " < ".join(CASCADE_LAYERS))
        print(f"Application styles: {len(styles)}")
        for style in styles:
            scope = style.get("scope") or "global"
            print(f"- {style['logical_id']} ({scope}, {style['layer']}) {style['digest']}")
        print("Public hooks: " + ", ".join(sorted(application_style_hook_manifest())))
    return 0


def _cmd_style_custom_css_check(args: argparse.Namespace) -> int:
    """Validate explicitly registered-style CSS without rejecting CSS outright."""
    target = Path(args.custom_css).resolve()
    if not target.exists():
        raise SystemExit(f"hedron style check: path not found: {args.custom_css}")
    paths = [target] if target.is_file() else sorted(target.rglob("*.css"))
    findings: list[dict[str, str]] = []
    for path in paths:
        try:
            compile_css(
                path.read_text(encoding="utf-8"),
                component_id=f"application:{path.stem}",
                layer="application",
                allow_remote=False,
                registered_roots=(path.parent,),
                component_dir=path.parent,
                rewrite_selectors=False,
            )
        except HedronError as exc:
            findings.append({"path": str(path), "diagnostic": str(exc)})
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            findings.append({"path": str(path), "diagnostic": str(exc)})
    payload = {
        "schema": "hedron.style-diagnostics/1",
        "path": str(target),
        "files": len(paths),
        "ok": not findings,
        "diagnostics": findings,
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif findings:
        for finding in findings:
            print(f"{finding['path']}: {finding['diagnostic']}", file=sys.stderr)
    else:
        print(f"ok: validated {len(paths)} custom stylesheet(s)")
    return 1 if findings else 0


def _cmd_style_eject_application(args: argparse.Namespace) -> int:
    """Eject registered application CSS with a provenance sidecar."""
    _require_app(args)
    styles = get_registry().application_styles()
    if not styles:
        print("No registered application styles.", file=sys.stderr)
        return 1
    cwd = Path.cwd().resolve()
    try:
        out_dir = _assert_project_write_path(Path(args.output), cwd=cwd)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    css_path = out_dir / "application-styles.css"
    map_path = out_dir / "source_map.json"
    if not args.overwrite and (css_path.exists() or map_path.exists()):
        print(f"Refusing to overwrite files under {out_dir} (use --overwrite)", file=sys.stderr)
        return 1
    chunks: list[str] = []
    sources: list[JsonObject] = []
    for style in styles:
        source = Path(style.source)
        style_data = style.to_dict(source_root=cwd)
        chunks.append(
            f"/* hedron: {style.logical_id} source={style_data['source']} "
            f"digest={style_data['digest']} */\n"
            + source.read_text(encoding="utf-8").rstrip()
            + "\n"
        )
        sources.append(style_data)
    css_path.write_text("\n".join(chunks), encoding="utf-8")
    map_path.write_text(
        json.dumps(
            {
                "schema": APPLICATION_STYLE_EJECTION_SCHEMA,
                "files": [css_path.name, map_path.name],
                "styles": sources,
                "cascade_layers": list(CASCADE_LAYERS),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"written": [str(css_path), str(map_path)]}, indent=2))
    return 0


def _application_style_manifest_path(path: str | None) -> Path:
    candidate = Path(path or "source_map.json").expanduser().resolve()
    if candidate.is_dir():
        candidate = candidate / "source_map.json"
    if not candidate.is_file():
        raise SystemExit(f"Application style manifest not found: {candidate}")
    return candidate


def _application_style_drift(manifest_path: Path) -> dict[str, Any]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema") != APPLICATION_STYLE_EJECTION_SCHEMA:
        raise SystemExit(f"Unsupported application style manifest: {manifest_path}")
    expected = {
        str(item["logical_id"]): str(item.get("digest") or "")
        for item in payload.get("styles", [])
        if isinstance(item, Mapping) and item.get("logical_id")
    }
    actual = {
        style.logical_id: style.source_digest for style in get_registry().application_styles()
    }
    added = sorted(set(actual) - set(expected))
    removed = sorted(set(expected) - set(actual))
    changed = sorted(
        logical_id
        for logical_id in set(expected) & set(actual)
        if expected[logical_id] != actual[logical_id]
    )
    return {
        "schema": "hedron.style-drift/1",
        "manifest": str(manifest_path),
        "added": added,
        "removed": removed,
        "changed": changed,
        "clean": not (added or removed or changed),
    }


def _cmd_style_update_check(args: argparse.Namespace) -> int:
    """Check an ejected application stylesheet for source drift without overwriting it."""
    _require_app(args)
    try:
        payload = _application_style_drift(_application_style_manifest_path(args.manifest))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise SystemExit(f"Could not read application style manifest: {exc}") from exc
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("clean" if payload["clean"] else "drift detected")
        for key in ("added", "removed", "changed"):
            if payload[key]:
                print(f"{key}: {', '.join(payload[key])}")
    return 0 if payload["clean"] else 1


def _token_swatches(theme: Theme, *, mode: str) -> str:
    tokens = dict(theme.tokens)
    if mode == "dark":
        dark = theme.modes.get("dark") or {}
        tokens.update(dark)
    parts: list[str] = []
    for key, value in sorted(tokens.items()):
        if not key.startswith("color.") and key not in {"focus.ring"}:
            continue
        safe_bg = value if isinstance(value, str) and value.startswith("#") else "#888888"
        parts.append(
            '<div class="swatch">'
            f'<span style="background:{html_lib.escape(safe_bg, quote=True)}"></span>'
            f"<code>{html_lib.escape(key)}</code> "
            f"<code>{html_lib.escape(str(value))}</code></div>"
        )
    return "\n".join(parts)


def _gallery_page(design: DesignSystem, *, modes: list[str]) -> str:
    theme = design.to_theme()
    # Synthetic preview only: neutralize style-tag breakout from hostile token text.
    css = emit_theme_css(theme).replace("</", "<\\/").replace("<", "\\3c ")
    sections: list[str] = []
    for mode in modes:
        sections.append(
            f'<section data-mode="{html_lib.escape(mode)}">'
            f"<h2>{html_lib.escape(mode.title())} mode</h2>"
            f"{_token_swatches(theme, mode=mode)}"
            f"</section>"
        )
    safe_name = html_lib.escape(design.name)
    safe_theme = html_lib.escape(theme.name)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Hedron design preview · {safe_name}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
    .swatch {{ display: flex; align-items: center; gap: 0.75rem; margin: 0.35rem 0; }}
    .swatch span {{ width: 2rem; height: 2rem; border: 1px solid #ccc; display: inline-block; }}
    section {{ margin-bottom: 2rem; }}
    {css}
  </style>
</head>
<body data-hedron-theme="{safe_theme}">
  <h1>Design gallery: {safe_name}</h1>
  <p>Fixed synthetic preview ({html_lib.escape(PREVIEW_FIXTURE_VERSION)}); no application data.</p>
  {"".join(sections)}
</body>
</html>
"""


def _cmd_style_preview(args: argparse.Namespace) -> int:
    design = _resolve_design(args)
    cwd = Path.cwd().resolve()
    try:
        out_resolved = _assert_project_write_path(Path(args.output), cwd=cwd)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    mode = str(args.mode)
    modes = ["light", "dark"] if mode == "all" else [mode]
    out_resolved.parent.mkdir(parents=True, exist_ok=True)
    page = _gallery_page(design, modes=modes)
    if out_resolved.suffix.lower() in {".html", ".htm"}:
        dest = out_resolved
        try:
            _assert_project_write_path(dest, cwd=cwd)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        dest.write_text(page, encoding="utf-8")
        pages = [str(dest.relative_to(cwd))]
    else:
        out_resolved.mkdir(parents=True, exist_ok=True)
        dest = out_resolved / "index.html"
        try:
            _assert_project_write_path(dest, cwd=cwd)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        dest.write_text(page, encoding="utf-8")
        pages = [str(dest.relative_to(cwd))]
    plan = design.explain()
    meta = {
        "schema": PREVIEW_SCHEMA,
        "plan_digest": plan.digest,
        "fixture_version": PREVIEW_FIXTURE_VERSION,
        "modes": modes,
        "viewports": ["desktop"],
        "assets": [],
        "pages": pages,
    }
    print(json.dumps({"written": pages, "preview": meta}, indent=2))
    return 0


def _mapping_diff(base: Mapping[str, object], candidate: Mapping[str, object]) -> dict[str, object]:
    added = {k: candidate[k] for k in candidate.keys() - base.keys()}
    removed = {k: base[k] for k in base.keys() - candidate.keys()}
    changed = {
        k: {"base": base[k], "candidate": candidate[k]}
        for k in base.keys() & candidate.keys()
        if base[k] != candidate[k]
    }
    return {"added": added, "removed": removed, "changed": changed}


def _list_diff(base: list[object], candidate: list[object]) -> dict[str, object]:
    return {
        "base_count": len(base),
        "candidate_count": len(candidate),
        "equal": base == candidate,
        "base": base,
        "candidate": candidate,
    }


def _components_map(plan: DesignSystemPlan) -> dict[str, object]:
    raw = plan.compatibility.get("components", {})
    if not isinstance(raw, dict):
        return {}
    out: dict[str, object] = {}
    for family, names in raw.items():
        key = str(family)
        out[key] = tuple(names) if isinstance(names, list) else names
    return out


def _design_diff(base: DesignSystem, candidate: DesignSystem) -> dict[str, object]:
    base_plan = base.explain()
    cand_plan = candidate.explain()
    base_theme = base.to_theme()
    cand_theme = candidate.to_theme()
    base_css = emit_theme_css(base_theme)
    cand_css = emit_theme_css(cand_theme)
    payload: dict[str, object] = {
        "schema": DIFF_SCHEMA,
        "base_digest": base_plan.digest,
        "candidate_digest": cand_plan.digest,
        "inputs": _mapping_diff(dict(base_plan.inputs), dict(cand_plan.inputs)),
        "tokens": _mapping_diff(dict(base_theme.tokens), dict(cand_theme.tokens)),
        "groups": _mapping_diff(dict(base_plan.groups), dict(cand_plan.groups)),
        "recipes": _list_diff(list(base_plan.recipes), list(cand_plan.recipes)),
        "components": {
            "compatibility": _mapping_diff(
                _components_map(base_plan),
                _components_map(cand_plan),
            )
        },
        "assets": _list_diff(list(base_plan.assets), list(cand_plan.assets)),
        "emitted_output": {
            "css_equal": base_css == cand_css,
            "base_sha256": hashlib.sha256(base_css.encode("utf-8")).hexdigest(),
            "candidate_sha256": hashlib.sha256(cand_css.encode("utf-8")).hexdigest(),
        },
    }
    return payload


def _diff_human(payload: dict[str, Any]) -> str:
    lines = [
        f"schema: {payload['schema']}",
        f"base_digest: {payload['base_digest']}",
        f"candidate_digest: {payload['candidate_digest']}",
        f"css_equal: {payload['emitted_output']['css_equal']}",
    ]
    for section in ("inputs", "tokens", "groups"):
        block = payload[section]
        lines.append(
            f"{section}: +{len(block['added'])} -{len(block['removed'])} ~{len(block['changed'])}"
        )
    recipes = payload["recipes"]
    lines.append(
        f"recipes: equal={recipes['equal']} "
        f"({recipes['base_count']} → {recipes['candidate_count']})"
    )
    return "\n".join(lines)


def _cmd_style_diff(args: argparse.Namespace) -> int:
    if getattr(args, "ejected_path", None):
        _require_app(args)
        payload = _application_style_drift(
            _application_style_manifest_path(args.manifest or args.ejected_path)
        )
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("clean" if payload["clean"] else "drift detected")
            for key in ("added", "removed", "changed"):
                if payload[key]:
                    print(f"{key}: {', '.join(payload[key])}")
        return 0 if payload["clean"] else 1
    # Ensure app/themes are loaded when --app is provided.
    if getattr(args, "app", None):
        _require_app(args)
    ensure_builtin_themes_registered()
    base = _resolve_design(args, name=args.base)
    candidate = _resolve_design(args, name=args.candidate)
    payload = _design_diff(base, candidate)
    if args.format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    else:
        print(_diff_human(payload))
    return 0


def _selection_label(args: argparse.Namespace) -> str:
    if getattr(args, "group", None):
        return f"group:{args.group}"
    if getattr(args, "recipe", None):
        return f"recipe:{args.recipe}"
    if getattr(args, "component", None):
        return f"component:{args.component}"
    return "*"


def _eject_theme_source(design: DesignSystem, *, selection: str) -> str:
    theme = design.to_theme()
    modes = {k: dict(v) for k, v in theme.modes.items()}
    variants = {k: dict(v) for k, v in theme.variants.items()}
    lines = [
        '"""Ejected Hedron Theme (public API)."""',
        "",
        "from hedron_core.theme import Theme, register_theme_instance",
        "",
        f"# selection: {selection}",
        "THEME = Theme(",
        f"    name={theme.name!r},",
        f"    tokens={dict(theme.tokens)!r},",
        f"    modes={modes!r},",
        f"    variants={variants!r},",
        f"    palette={dict(theme.palette)!r},",
        f"    density={theme.density!r},",
        f"    shape={dict(theme.shape)!r},",
        f"    nav_width={theme.nav_width!r},",
        f"    elevation={dict(theme.elevation)!r},",
        f"    parent={theme.parent!r},",
        ")",
        "",
        "register_theme_instance(THEME)",
        "",
    ]
    if selection.startswith("group:"):
        group = selection.split(":", 1)[1]
        value = design.groups.get(group)
        lines.insert(5, f"# group {group!r} = {value!r}")
    elif selection.startswith("recipe:"):
        recipe_name = selection.split(":", 1)[1]
        catalog = dict(BUILTIN_RECIPES)
        for recipe in design.recipes:
            catalog[recipe.name] = recipe
        recipe = catalog.get(recipe_name)
        if recipe is None:
            raise error(
                HED_STYLE_EJECT_0002,
                title="Unknown recipe for style eject",
                explanation=f"Recipe {recipe_name!r} is not in the design catalog.",
                remediation="Pass a built-in or design recipe name.",
            )
        lines.insert(5, f"# recipe {recipe.to_dict()!r}")
    elif selection.startswith("component:"):
        lines.insert(5, f"# component selection {selection.split(':', 1)[1]!r}")
    return "\n".join(lines)


def _cmd_style_eject(args: argparse.Namespace) -> int:
    selected = [
        flag
        for flag in (
            getattr(args, "group", None),
            getattr(args, "recipe", None),
            getattr(args, "component", None),
        )
        if flag
    ]
    if len(selected) > 1:
        print("Choose at most one of --group / --recipe / --component", file=sys.stderr)
        return 2
    if getattr(args, "app", None):
        _require_app(args)
    ensure_builtin_themes_registered()
    design = _resolve_design(args, name=args.name)

    cwd = Path.cwd().resolve()
    try:
        out_dir = _assert_project_write_path(Path(args.output), cwd=cwd)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    selection = _selection_label(args)
    if selection.startswith("group:"):
        group = selection.split(":", 1)[1]
        if group not in design.groups and group not in {
            "density",
            "geometry",
            "typography",
            "elevation",
            "motion",
            "navigation",
        }:
            print(f"Unknown group for style eject: {group!r}", file=sys.stderr)
            return 1
    from hedron_core.diagnostics import HedronError

    try:
        source = _eject_theme_source(design, selection=selection)
    except HedronError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "theme.py"
    map_path = out_dir / "source_map.json"
    overwrite = bool(getattr(args, "overwrite", False))
    for path in (dest, map_path):
        if path.exists() and not overwrite:
            print(
                f"Refusing to overwrite {path} (use --overwrite)",
                file=sys.stderr,
            )
            return 1
        try:
            _assert_project_write_path(path, cwd=cwd)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
    dest.write_text(source, encoding="utf-8")
    plan = design.explain()
    theme_css = emit_theme_css(design.to_theme())
    source_map = {
        "schema": SOURCE_MAP_SCHEMA,
        "design_id": design.logical_id,
        "selection": selection,
        "files": ["theme.py", "source_map.json"],
        "plan_digest": plan.digest,
        "theme_digest": hashlib.sha256(
            json.dumps(dict(design.to_theme().tokens), sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "css_digest": hashlib.sha256(theme_css.encode("utf-8")).hexdigest(),
        "parity_digest": plan.digest,
    }
    map_path.write_text(json.dumps(source_map, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "design": design.name,
                "selection": selection,
                "written": [str(dest), str(map_path)],
            },
            indent=2,
        )
    )
    return 0


def _read_theme_spec(path: Path) -> ThemeSpec:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not read theme spec {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("theme spec JSON must contain an object")
    return ThemeSpec.from_dict(payload)


def _cmd_style_init(args: argparse.Namespace) -> int:
    cwd = Path.cwd().resolve()
    try:
        dest = _assert_project_write_path(Path(args.output), cwd=cwd)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if dest.exists():
        print(f"Refusing to overwrite {dest} (choose a new path)", file=sys.stderr)
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    starter = ThemeSpec(
        name=args.name,
        tokens={
            "color.bg": "#ffffff",
            "color.fg": "#111827",
            "color.muted": "#4b5563",
            "color.focus": "#1d4ed8",
            "font.family": "system-ui",
            "font.size": "1rem",
            "space.unit": "0.25rem",
        },
        metadata={"starter": True},
    )
    dest.write_text(
        json.dumps(starter.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"written": str(dest), "fingerprint": starter.fingerprint}, indent=2))
    return 0


def _cmd_style_package(args: argparse.Namespace) -> int:
    try:
        spec = _read_theme_spec(Path(args.spec))
        packaged = package_theme(spec, profile=args.profile, licenses=tuple(args.license or ()))
        dest = _assert_project_write_path(Path(args.output), cwd=Path.cwd().resolve())
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if dest.exists() and not args.overwrite:
        print(f"Refusing to overwrite {dest} (use --overwrite)", file=sys.stderr)
        return 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(packaged.archive)
    print(json.dumps({"written": str(dest), "manifest": dict(packaged.manifest)}, indent=2))
    return 0


def _cmd_style_conform(args: argparse.Namespace) -> int:
    try:
        spec = _read_theme_spec(Path(args.spec))
        report = conformance_report(spec, profile=args.profile)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1
