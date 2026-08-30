"""Explorer HTML shell, nav, and mount-aware hrefs."""

from __future__ import annotations

import html as html_lib
from typing import Any, cast

from fastapi import Request

from hedron_explorer.services.fs import safe_read_text
from hedron_explorer.services.runtime import TRACE, redact

NAV = (
    ("components", "Components", "/hedron-explorer/"),
    ("routes", "Routes", "/hedron-explorer/routes"),
    ("graph", "Graph", "/hedron-explorer/graph"),
    ("security", "Security", "/hedron-explorer/security"),
    ("a11y", "Accessibility", "/hedron-explorer/a11y"),
    ("cache", "Cache", "/hedron-explorer/cache"),
    ("data", "Data", "/hedron-explorer/data"),
    ("charts", "Charts", "/hedron-explorer/charts"),
    ("maps", "Maps", "/hedron-explorer/maps"),
    ("extensions", "HTMX extensions", "/hedron-explorer/extensions"),
    ("auto", "Auto", "/hedron-explorer/auto"),
    ("packages", "Packages", "/hedron-explorer/packages"),
    ("elements", "Elements", "/hedron-explorer/elements"),
    ("inventory", "Inventory", "/hedron-explorer/inventory"),
    ("interactions", "Interactions", "/hedron-explorer/interactions"),
    ("features", "Features", "/hedron-explorer/features"),
    ("theme-lab", "Theme Lab", "/hedron-explorer/theme-lab"),
    ("settings", "Settings", "/hedron-explorer/settings"),
)


def mount_path(request: Request) -> str:
    from hedron_core.mount import normalize_mount_path

    configured = getattr(request.app.state, "hedron_mount_path", None)
    if isinstance(configured, str) and configured:
        return normalize_mount_path(configured)
    return normalize_mount_path(str(request.scope.get("root_path") or ""))


def explorer_href(request: Request, path: str) -> str:
    normalized_path = "/" + path.lstrip("/")
    mount = mount_path(request)
    href = f"{mount}{normalized_path}" if mount else normalized_path
    return html_lib.escape(href, quote=True)


def nav_link(request: Request, key: str, label: str, href: str, active: str) -> str:
    css_class = "active" if key == active else ""
    return (
        f'<a href="{explorer_href(request, href)}" class="{css_class}">{html_lib.escape(label)}</a>'
    )


def component_href(request: Request, name: str) -> str:
    return explorer_href(request, "/hedron-explorer/component/" + name)


def preview_frame(html: str) -> str:
    srcdoc = html_lib.escape(html, quote=True)
    return (
        '<iframe class="preview-frame" sandbox="" referrerpolicy="no-referrer" '
        f'srcdoc="{srcdoc}" title="Component preview"></iframe>'
    )


def shell(title: str, body: str, *, request: Request, active: str = "components") -> str:
    links = "".join(nav_link(request, key, label, href, active) for key, label, href in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{html_lib.escape(title)} · Hedron Explorer</title>
  <link rel="stylesheet" href="{explorer_href(request, "/hedron-explorer/static/explorer.css")}">
  <script src="{explorer_href(request, "/hedron-static/htmx.min.js")}" defer></script>
  <script src="{explorer_href(request, "/hedron-static/ext/head-support.js")}" defer></script>
  <script src="{explorer_href(request, "/hedron-static/ext/sse.js")}" defer></script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header>
    <h1>Hedron Explorer</h1>
    <nav aria-label="Explorer">{links}</nav>
  </header>
  <main id="main" tabindex="-1">{body}</main>
</body>
</html>"""


def component_detail_body(meta: object, request: Request) -> str:
    from hedron_core.registry import ComponentMeta
    from hedron_core.rendering import RenderMode, render

    if not isinstance(meta, ComponentMeta):
        raise TypeError(f"component_detail_body expected ComponentMeta; got {type(meta).__name__}")
    styles = safe_read_text(meta.styles_path, meta, request)
    styles_block = (
        html_lib.escape(styles)
        if styles is not None
        else (
            "(styles unavailable or outside allowlisted component roots)"
            if meta.styles_path
            else "(no styles.css)"
        )
    )
    explanations = [
        f"Style symbols: {dict(meta.style_symbols) or '{}'}",
        "Jinja templates are application-level sources managed by hedron-jinja.",
        "Browser modules register as fingerprinted assets when present.",
        "Override style symbols via component STYLE_COMPONENT_ID / local eject.",
    ]
    preview_html = ""
    try:
        from hedron_core import Text

        result = render(Text(f"Preview of {meta.name}"), mode=RenderMode.FRAGMENT)
        preview_html = result.html
        TRACE.appendleft({"kind": "render", "component": meta.logical_id, "mode": "fragment"})
    except Exception as exc:  # noqa: BLE001
        preview_html = html_lib.escape(str(exc))
    return f"""
        <h2>{html_lib.escape(meta.name)}</h2>
        <p><code>{html_lib.escape(meta.logical_id)}</code></p>
        <section>
          <h3>Preview</h3>
          <div class="preview">{preview_frame(preview_html)}</div>
        </section>
        <section>
          <h3>Inference explanations</h3>
          <ul>{"".join(f"<li>{html_lib.escape(x)}</li>" for x in explanations)}</ul>
        </section>
        <section>
          <h3>Styles</h3>
          <pre>{styles_block}</pre>
        </section>
        <section>
          <h3>Assets</h3>
          <p>Roots: {html_lib.escape(str([redact(r) for r in meta.asset_roots]))}</p>
          <p>Browser modules: {html_lib.escape(str([redact(m) for m in meta.browser_modules]))}</p>
        </section>
        """


def handle_graph_html(request: Request) -> str:
    from hedron_core.updates import handle_graph_payload

    app_id = str(getattr(getattr(request.app, "state", None), "hedron_app_id", "") or "")
    payload = handle_graph_payload(app_id=app_id or None)
    nodes_raw = payload.get("nodes")
    if not isinstance(nodes_raw, list) or not nodes_raw:
        return "<p>No refreshable views or commands registered.</p>"
    nodes = cast(list[Any], nodes_raw)
    rows: list[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        typed_node = cast(dict[str, Any], node)
        kind = html_lib.escape(str(typed_node.get("kind", "")))
        effect = html_lib.escape(str(typed_node.get("effect", "dynamic")))
        ident = html_lib.escape(str(typed_node.get("id", "")))
        path = html_lib.escape(str(typed_node.get("path", "")))
        rows.append(f"<tr><td>{ident}</td><td>{kind}</td><td>{effect}</td><td>{path}</td></tr>")
    body = "".join(rows)
    return (
        "<p>Command effects are labeled <code>dynamic</code> or <code>observed</code>, "
        "never declared.</p>"
        "<table><thead><tr><th>Handle</th><th>Kind</th><th>Effect</th><th>Path</th></tr></thead>"
        f"<tbody>{body}</tbody></table>"
    )
