"""Host-neutral PAGE asset injection and static directory locator.

Adapters (FastAPI, Flask, Django) mount :func:`static_directory` at
``/hedron-static`` and call :func:`inject_page_assets` on PAGE HTML so HTMX and
bundled extensions load without depending on the FastAPI flagship package.
"""

from __future__ import annotations

import html as html_lib
from collections.abc import Callable, Mapping, Sequence
from importlib import resources
from pathlib import Path
from typing import Protocol

from hedron_core.htmx_extensions import known_extensions
from hedron_core.rendering import AssetRef, RenderMode
from hedron_core.security_policy import SecurityPolicy

__all__ = [
    "DEFAULT_STATIC_PREFIX",
    "htmx_core_script_end",
    "inject_htmx_core",
    "inject_htmx_extensions",
    "inject_page_assets",
    "static_directory",
]

DEFAULT_STATIC_PREFIX = "/hedron-static"


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


def inject_htmx_extensions(
    html_text: str,
    *,
    static_href: Callable[[str], str] | None = None,
) -> str:
    """Insert non-deferred HTMX extensions after the core runtime script."""
    tags: list[str] = []
    for ext in sorted(known_extensions(), key=lambda e: e.load_order):
        if ext.deferred:
            continue
        ext_path = _prefix_href(ext.path, static_href=static_href)
        if ext.path in html_text or ext_path in html_text:
            continue
        tags.append(f'<script src="{ext_path}" defer></script>')
    if not tags:
        return html_text
    injection = "\n".join(tags)
    core_end = htmx_core_script_end(html_text)
    if core_end is not None:
        return html_text[:core_end] + "\n" + injection + html_text[core_end:]
    if "</body>" in html_text:
        return html_text.replace("</body>", f"{injection}\n</body>", 1)
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
) -> str:
    """Inject HTMX core, default CSS/UI modules, build assets, then extensions.

    Extension scripts are pinned immediately after the core runtime so deferred
    scripts execute in dependency order (issue #55 / RFC-0032).
    """
    del asset_attributes  # reserved for future attribute passthrough
    html_text = inject_htmx_core(html_text, mode, policy=policy, static_href=static_href)
    if mode is not RenderMode.PAGE:
        return html_text
    tags: list[str] = []
    seen: set[str] = set()

    def add(tag: str) -> None:
        if tag in html_text or tag in seen:
            return
        seen.add(tag)
        tags.append(tag)

    if include_default_styles:
        css = _prefix_href(f"{DEFAULT_STATIC_PREFIX}/hedron-default.css", static_href=static_href)
        add(f'<link rel="stylesheet" href="{css}">')

    for asset in assets or ():
        href = html_lib.escape(asset.href, quote=True)
        if asset.kind == "css":
            add(f'<link rel="stylesheet" href="{href}">')
        elif asset.kind in {"js", "module"}:
            typ = ' type="module"' if asset.kind == "module" else ""
            add(f'<script{typ} src="{href}"></script>')

    if include_ui_modules:
        if "hedron-disclose.mjs" not in html_text:
            disclose = _prefix_href(
                f"{DEFAULT_STATIC_PREFIX}/hedron-disclose.mjs", static_href=static_href
            )
            add(f'<script type="module" src="{disclose}"></script>')
        if "hedron-ui.mjs" not in html_text:
            ui = _prefix_href(f"{DEFAULT_STATIC_PREFIX}/hedron-ui.mjs", static_href=static_href)
            add(f'<script type="module" src="{ui}"></script>')

    if tags:
        injection = "\n".join(tags)
        if "</head>" in html_text:
            html_text = html_text.replace("</head>", f"{injection}\n</head>", 1)
        elif "</body>" in html_text:
            html_text = html_text.replace("</body>", f"{injection}\n</body>", 1)
        else:
            html_text = html_text + injection
    return inject_htmx_extensions(html_text, static_href=static_href)
