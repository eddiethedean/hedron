"""Host-neutral PAGE asset injection and static directory locator.

Adapters (FastAPI, Flask, Django) mount :func:`static_directory` at
``/hedron-static`` and call :func:`inject_page_assets` on PAGE HTML so HTMX and
bundled extensions load without depending on the FastAPI flagship package.
"""

from __future__ import annotations

import html as html_lib
import re
from collections.abc import Callable, Mapping, Sequence
from importlib import resources
from pathlib import Path
from typing import Protocol

from hedron_core.application_assets import (
    ApplicationAssetSpec,
    application_spec_to_asset_ref,
    compile_application_asset_plan,
    emit_safe_application_assets,
    ordered_registry_assets,
    specs_from_asset_refs,
)
from hedron_core.codes import HED_EXT_0005
from hedron_core.diagnostics import error
from hedron_core.head_support import merge_registered_head, reject_invented_fragment_scripts
from hedron_core.htmx_extensions import (
    ExtensionPlan,
    ExtensionSet,
    compile_extension_plan,
)
from hedron_core.rendering import AssetRef, RenderMode
from hedron_core.security_policy import SecurityPolicy

__all__ = [
    "DEFAULT_STATIC_PREFIX",
    "htmx_core_script_end",
    "inject_htmx_core",
    "inject_htmx_bridge",
    "inject_htmx_extensions",
    "inject_alpine_plan",
    "inject_page_assets",
    "inject_page_theme",
    "static_directory",
]

DEFAULT_STATIC_PREFIX = "/hedron-static"
_THEME_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_HTML_TAG_RE = re.compile(r"<html\b", re.IGNORECASE)
_THEME_ATTR_RE = re.compile(r"\bdata-hedron-theme\s*=", re.IGNORECASE)
_COLOR_MODE_ATTR_RE = re.compile(r"\bdata-theme\s*=", re.IGNORECASE)
_SAFE_PASSTHROUGH_ATTRS = frozenset({"integrity", "crossorigin"})


class _HtmxConfigPolicy(Protocol):
    htmx_browser_preset: bool

    def htmx_config_json(self) -> str: ...


def static_directory() -> Path:
    """Return the filesystem path to bundled Hedron static assets."""
    return Path(str(resources.files("hedron_core").joinpath("static")))


def htmx_core_script_end(html_text: str) -> int | None:
    """Return the index immediately after the HTMX core ``</script>`` tag, if present."""
    marker = "htmx.min.js"
    marker_at = html_text.find(marker)
    if marker_at < 0:
        return None
    script_at = html_text.rfind("<script", 0, marker_at)
    if script_at < 0:
        return None
    close_at = html_text.find("</script>", marker_at)
    if close_at < 0:
        return None
    return close_at + len("</script>")


def _prefix_href(path: str, *, static_href: Callable[[str], str] | None) -> str:
    href = path if path.startswith("/") else f"/{path}"
    if static_href is None:
        return href
    return static_href(href)


def inject_page_theme(
    html_text: str,
    mode: RenderMode,
    theme: str | None,
    *,
    preference: object | None = None,
) -> str:
    """Apply server-first theme markers to PAGE HTML unless the page chose them."""
    if mode is not RenderMode.PAGE:
        return html_text
    color_mode: str | None = None
    if preference is not None:
        from hedron_core.builtins.theme_preference import ThemePreference, theme_markers

        if not isinstance(preference, ThemePreference):
            raise TypeError("preference must be a ThemePreference")
        theme = preference.theme
        color_mode = preference.color_mode
        markers = theme_markers(preference)
    else:
        markers = {}
    if not theme or _THEME_ATTR_RE.search(html_text):
        return html_text
    if _THEME_NAME_RE.fullmatch(theme) is None:
        return html_text
    match = _HTML_TAG_RE.search(html_text)
    if match is None:
        return html_text
    safe_theme = html_lib.escape(theme, quote=True)
    suffix = f' data-hedron-theme="{safe_theme}"'
    if color_mode is not None and not _COLOR_MODE_ATTR_RE.search(html_text):
        suffix += f' data-hedron-color-mode="{html_lib.escape(color_mode, quote=True)}"'
        suffix += f' data-theme="{html_lib.escape(markers["data-theme"], quote=True)}"'
    return html_text[: match.end()] + suffix + html_text[match.end() :]


def inject_htmx_core(
    html_text: str,
    mode: RenderMode,
    *,
    policy: SecurityPolicy | _HtmxConfigPolicy | None = None,
    static_href: Callable[[str], str] | None = None,
) -> str:
    """Inject the bundled HTMX runtime and profile-driven secure v2 defaults."""
    if mode is not RenderMode.PAGE:
        return html_text
    sec: SecurityPolicy | _HtmxConfigPolicy = (
        SecurityPolicy.from_name("standard") if policy is None else policy
    )
    if sec.htmx_browser_preset:
        config = f"<meta name=\"htmx-config\" content='{sec.htmx_config_json()}'>"
        if 'name="htmx-config"' not in html_text and "name='htmx-config'" not in html_text:
            if "</head>" in html_text:
                html_text = html_text.replace("</head>", f"{config}</head>", 1)
            else:
                html_text = config + html_text
    htmx_src = _prefix_href(f"{DEFAULT_STATIC_PREFIX}/htmx.min.js", static_href=static_href)
    tag = f'<script src="{htmx_src}" defer></script>'
    if "htmx.min.js" in html_text:
        return html_text
    if "</head>" in html_text:
        return html_text.replace("</head>", f"{tag}\n</head>", 1)
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{tag}</body>", 1)
    return html_text + tag


def inject_htmx_bridge(
    html_text: str,
    mode: RenderMode,
    *,
    static_href: Callable[[str], str] | None = None,
) -> str:
    """Inject Hedron's minimal HTMX lifecycle bridge after HTMX core."""
    if mode is not RenderMode.PAGE or "hedron-htmx.mjs" in html_text:
        return html_text
    bridge_src = _prefix_href("/hedron-static/hedron-htmx.mjs", static_href=static_href)
    tag = f'<script type="module" src="{bridge_src}"></script>'
    core_end = htmx_core_script_end(html_text)
    if core_end is not None:
        return html_text[:core_end] + "\n" + tag + html_text[core_end:]
    if "</head>" in html_text:
        return html_text.replace("</head>", f"{tag}\n</head>", 1)
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{tag}</body>", 1)
    return html_text + tag


def _plan_or_compat(plan: ExtensionPlan | None) -> ExtensionPlan:
    if plan is not None:
        return plan
    return compile_extension_plan(declaration=ExtensionSet.unset(), required=(), mode="page")


def _verify_extension_asset(ext: object) -> None:

    rel = str(getattr(ext, "path", "")).removeprefix("/hedron-static/")
    path = static_directory() / rel
    if not path.is_file():
        raise error(
            HED_EXT_0005,
            title="Missing vendored HTMX extension",
            explanation=f"{getattr(ext, 'name', rel)!r} is not present at {path}.",
            remediation="Restore the pinned local asset; Hedron does not fetch CDNs.",
        )
    import hashlib

    digest = f"sha256-{hashlib.sha256(path.read_bytes()).hexdigest()}"
    expected = str(getattr(ext, "digest", ""))
    if digest != expected:
        raise error(
            HED_EXT_0005,
            title="HTMX extension digest mismatch",
            explanation=f"{getattr(ext, 'name', rel)} digest {digest} != {expected}.",
            remediation="Re-vendor the pinned extension or restore the catalog digest.",
        )


def apply_hx_ext_attribute(html_text: str, hx_ext: str) -> str:
    """Emit catalog public ids on the document element. Empty plans omit hx-ext."""
    if not hx_ext:
        return html_text
    match = _HTML_TAG_RE.search(html_text)
    if match is None:
        return html_text
    tag = html_text[match.start() : html_text.find(">", match.start()) + 1]
    if re.search(r"\bhx-ext\s*=", tag, re.IGNORECASE):
        return html_text
    insertion = html_text[: match.end()] + f' hx-ext="{html_lib.escape(hx_ext, quote=True)}"'
    return insertion + html_text[match.end() :]


def inject_htmx_extensions(
    html_text: str,
    *,
    static_href: Callable[[str], str] | None = None,
    plan: ExtensionPlan | None = None,
) -> str:
    """Insert planned HTMX extensions after the core runtime script.

    ``plan=None`` keeps the 0.47 compatibility default (sse + head-support).
    """
    resolved = _plan_or_compat(plan)
    if not resolved.inject or not resolved.ids:
        return html_text
    tags: list[str] = []
    for ext in resolved.assets:
        _verify_extension_asset(ext)
        ext_path = _prefix_href(ext.path, static_href=static_href)
        if ext.path in html_text or ext_path in html_text:
            continue
        tags.append(f'<script src="{ext_path}" defer></script>')
    if tags:
        injection = "\n".join(tags)
        core_end = htmx_core_script_end(html_text)
        if core_end is not None:
            html_text = html_text[:core_end] + "\n" + injection + html_text[core_end:]
        elif "</body>" in html_text:
            html_text = html_text.replace("</body>", f"{injection}\n</body>", 1)
        else:
            html_text = html_text + injection
    return apply_hx_ext_attribute(html_text, resolved.hx_ext)


def inject_alpine_plan(
    html_text: str,
    mode: RenderMode,
    browser_plan: object | None = None,
    *,
    static_href: Callable[[str], str] | None = None,
) -> str:
    """Inject the single local CSP-safe Alpine runtime when the PAGE demands it."""
    if mode is not RenderMode.PAGE:
        return html_text
    from hedron_core.alpine import BrowserFeaturePlan

    if not isinstance(browser_plan, BrowserFeaturePlan) or browser_plan.feature_off:
        return html_text
    runtime = _prefix_href("/hedron-static/hedron-alpine.mjs", static_href=static_href)
    marker = (
        '<meta name="hedron-browser-plan" '
        f'content="{html_lib.escape(browser_plan.fingerprint, quote=True)}">'
    )
    scripts: list[str] = []
    from hedron_core.browser_assets_067 import ALPINE_FILE_INTEGRITY

    for asset in browser_plan.assets:
        href = _prefix_href(asset, static_href=static_href)
        if href in html_text:
            continue
        integrity = ALPINE_FILE_INTEGRITY.get(asset)
        integrity_attrs = (
            f' integrity="{html_lib.escape(integrity, quote=True)}" crossorigin="anonymous"'
            if integrity
            else ""
        )
        scripts.append(
            f'<script type="module" src="{html_lib.escape(href, quote=True)}"'
            f"{integrity_attrs}></script>"
        )
    if (
        runtime not in html_text
        and "hedron-alpine.mjs" not in html_text
        and runtime not in browser_plan.assets
    ):
        scripts.insert(
            0,
            f'<script type="module" src="{html_lib.escape(runtime, quote=True)}"></script>',
        )
    if not scripts:
        if marker in html_text:
            return html_text
        if "</head>" in html_text:
            return html_text.replace("</head>", f"{marker}\n</head>", 1)
        if "</body>" in html_text:
            return html_text.replace("</body>", f"{marker}\n</body>", 1)
        return html_text + marker
    tag = f"{marker}\n" + "\n".join(scripts)
    if "</head>" in html_text:
        return html_text.replace("</head>", f"{tag}\n</head>", 1)
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{tag}\n</body>", 1)
    return html_text + tag


def _attr_suffix(attributes: Mapping[str, str]) -> str:
    parts: list[str] = []
    for key in sorted(attributes):
        lowered = key.lower()
        if lowered not in _SAFE_PASSTHROUGH_ATTRS:
            continue
        parts.append(f' {lowered}="{html_lib.escape(str(attributes[key]), quote=True)}"')
    return "".join(parts)


def _render_asset_tag(spec: ApplicationAssetSpec, *, defer_js: bool) -> str:
    href = html_lib.escape(spec.href, quote=True)
    attrs: dict[str, str] = {}
    if spec.integrity:
        attrs["integrity"] = spec.integrity
        attrs.setdefault("crossorigin", "anonymous")
    extra = _attr_suffix(attrs)
    if spec.kind == "css":
        return f'<link rel="stylesheet" href="{href}"{extra}>'
    if spec.kind == "module":
        return f'<script type="module" src="{href}"{extra}></script>'
    defer = " defer" if defer_js else ""
    return f'<script src="{href}"{defer}{extra}></script>'


def _collect_emit_specs(
    assets: Sequence[AssetRef] | None,
    asset_attributes: Mapping[str, Mapping[str, str]] | None,
) -> tuple[ApplicationAssetSpec, ...]:
    """Merge live registry assets with call-site AssetRefs; topo-sort when ok."""
    registry = ordered_registry_assets()
    by_path = {spec.href: spec for spec in registry}
    call_site = specs_from_asset_refs(
        assets or (),
        asset_attributes=asset_attributes,
        registry_by_path=by_path,
    )
    # Prefer call-site overrides when the same logical_id / href appears.
    by_id: dict[str, ApplicationAssetSpec] = {spec.logical_id: spec for spec in registry}
    seen_href = {spec.href: spec.logical_id for spec in registry}
    for spec in call_site:
        if spec.href in seen_href:
            prior = seen_href[spec.href]
            by_id[prior] = ApplicationAssetSpec(
                logical_id=prior,
                kind=spec.kind,
                href=spec.href,
                depends_on=by_id[prior].depends_on or spec.depends_on,
                placement=by_id[prior].placement if prior in by_id else spec.placement,
                integrity=spec.integrity or by_id.get(prior, spec).integrity,
            )
            continue
        by_id[spec.logical_id] = spec
        seen_href[spec.href] = spec.logical_id
    if not by_id:
        return ()
    plan = compile_application_asset_plan(tuple(by_id.values()))
    return emit_safe_application_assets(plan, fallback=tuple(by_id.values()))


def _insert_before_close(html_text: str, close: str, injection: str) -> str:
    if close in html_text:
        return html_text.replace(close, f"{injection}\n{close}", 1)
    return html_text + injection


def inject_page_assets(
    html_text: str,
    mode: RenderMode,
    *,
    policy: SecurityPolicy | _HtmxConfigPolicy | None = None,
    static_href: Callable[[str], str] | None = None,
    include_default_styles: bool = True,
    include_ui_modules: bool = True,
    assets: Sequence[AssetRef] | None = None,
    asset_attributes: Mapping[str, Mapping[str, str]] | None = None,
    theme: str | None = None,
    theme_preference: object | None = None,
    plan: ExtensionPlan | None = None,
    browser_plan: object | None = None,
    demand_driven: bool = False,
) -> str:
    """Inject HTMX core, default CSS/UI modules, build assets, then extensions.

    Extension scripts are pinned immediately after the core runtime so deferred
    scripts execute in dependency order (issue #55 / RFC-0032).

    Application assets from the call site and the live registry are topo-sorted
    by ``depends_on`` and placed at ``head``, ``after_htmx_core``, or ``body_end``.
    When head-support is planned, head-placement assets are merged via
    :func:`merge_registered_head` (not also emitted here) to avoid double scripts.
    """
    html_text = inject_page_theme(html_text, mode, theme, preference=theme_preference)
    requires_htmx = bool(re.search(r"\s(?:data-)?hx-[a-z][a-z0-9-]*=", html_text))
    if not demand_driven or requires_htmx:
        html_text = inject_htmx_core(html_text, mode, policy=policy, static_href=static_href)
    if requires_htmx:
        html_text = inject_htmx_bridge(html_text, mode, static_href=static_href)
    html_text = inject_alpine_plan(html_text, mode, browser_plan, static_href=static_href)
    if mode is not RenderMode.PAGE:
        reject_invented_fragment_scripts(html_text)
        return html_text

    resolved = _plan_or_compat(plan)
    head_support_on = "head-support" in resolved.ids
    emit_specs = _collect_emit_specs(assets, asset_attributes)

    head_tags: list[str] = []
    after_core_tags: list[str] = []
    body_end_tags: list[str] = []
    seen_href: set[str] = set()
    head_merge_refs: list[AssetRef] = []

    def take(spec: ApplicationAssetSpec) -> bool:
        if spec.href in seen_href or spec.href in html_text:
            return False
        seen_href.add(spec.href)
        return True

    if include_default_styles:
        css = _prefix_href(f"{DEFAULT_STATIC_PREFIX}/hedron-default.css", static_href=static_href)
        if css not in seen_href and css not in html_text:
            seen_href.add(css)
            head_tags.append(f'<link rel="stylesheet" href="{css}">')

    for spec in emit_specs:
        if not take(spec):
            continue
        if head_support_on and spec.placement == "head":
            # Head-support merge owns head placement (consistent defer + no double).
            head_merge_refs.append(application_spec_to_asset_ref(spec))
            continue
        tag = _render_asset_tag(spec, defer_js=spec.placement != "body_end")
        if spec.placement == "after_htmx_core":
            after_core_tags.append(tag)
        elif spec.placement == "body_end":
            body_end_tags.append(tag)
        else:
            head_tags.append(tag)

    ui_demand = any(
        marker in html_text
        for marker in (
            "hedron-tabs",
            "data-hedron-password-toggle",
            "data-hedron-toast",
            "data-hedron-reveal",
            "data-hedron-nav-toggle",
            "data-hedron-after-load",
            "data-hedron-clipboard-copy",
        )
    )
    disclose_demand = "<hedron-" in html_text
    if include_ui_modules and (not demand_driven or ui_demand or disclose_demand):
        if (not demand_driven or disclose_demand) and "hedron-disclose.mjs" not in html_text:
            disclose = _prefix_href(
                f"{DEFAULT_STATIC_PREFIX}/hedron-disclose.mjs", static_href=static_href
            )
            if disclose not in seen_href:
                seen_href.add(disclose)
                head_tags.append(f'<script type="module" src="{disclose}"></script>')
        if (not demand_driven or ui_demand) and "hedron-ui.mjs" not in html_text:
            ui = _prefix_href(f"{DEFAULT_STATIC_PREFIX}/hedron-ui.mjs", static_href=static_href)
            if ui not in seen_href:
                seen_href.add(ui)
                head_tags.append(f'<script type="module" src="{ui}"></script>')

    if head_tags:
        injection = "\n".join(head_tags)
        if "</head>" in html_text:
            html_text = html_text.replace("</head>", f"{injection}\n</head>", 1)
        elif "</body>" in html_text:
            html_text = html_text.replace("</body>", f"{injection}\n</body>", 1)
        else:
            html_text = html_text + injection

    if after_core_tags:
        injection = "\n".join(after_core_tags)
        core_end = htmx_core_script_end(html_text)
        if core_end is not None:
            html_text = html_text[:core_end] + "\n" + injection + html_text[core_end:]
        else:
            html_text = _insert_before_close(html_text, "</body>", injection)

    if body_end_tags:
        html_text = _insert_before_close(html_text, "</body>", "\n".join(body_end_tags))

    # Call-site head assets when head-support is off were already emitted above.
    # When on, merge only head-placement refs (href-deduped inside merge).
    merge_assets: Sequence[AssetRef] | None = tuple(head_merge_refs) if head_support_on else None
    html_text = merge_registered_head(
        html_text,
        merge_assets,
        enabled=head_support_on,
    )
    if demand_driven and not requires_htmx:
        return html_text
    return inject_htmx_extensions(html_text, static_href=static_href, plan=resolved)
