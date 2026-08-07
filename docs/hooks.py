"""MkDocs hooks for Read the Docs / local builds.

- Sync ``hedron-sim`` JS/CSS into ``docs/javascript`` and ``docs/stylesheets``.
- Expand ``<!-- hedron-sim:NAME -->`` markers from ``docs/includes/sim/`` *after*
  Markdown runs, so tokens like ``__HEDRON_SIM_UTC__`` are not turned into
  ``<strong>`` and so absolute demo ``href``s are not rewritten by the MD pipeline.
- STATUS.md / ROADMAP.md stay canonical under ``docs/`` (synced to root separately).
"""

from __future__ import annotations

import re
from pathlib import Path

_DOCS = Path(__file__).resolve().parent
_SIM_INCLUDES = _DOCS / "includes" / "sim"
_SIM_MARKER = re.compile(r"<!--\s*hedron-sim:([a-z0-9-]+)\s*-->", re.IGNORECASE)


def on_config(config):  # noqa: ANN001
    """Copy hedron-sim assets into the docs static tree when the package is available."""
    try:
        from hedron_sim.assets import copy_assets
    except ImportError:
        return config
    copy_assets(_DOCS / "javascript", _DOCS / "stylesheets")
    return config


def _expand_sim_markers(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        path = _SIM_INCLUDES / f"{name}.html"
        if not path.is_file():
            return (
                '<p class="hedron-sim-missing"><em>Missing sim demo '
                f"<code>{name}</code> — run "
                "<code>uv run python scripts/generate_sim_demos.py</code>."
                "</em></p>"
            )
        return path.read_text(encoding="utf-8").strip()

    return _SIM_MARKER.sub(repl, text)


def on_page_content(html: str, page: object, **kwargs: object) -> str:  # noqa: ARG001
    """Expand sim islands after Markdown, then mark the homepage Demo|Code tabs."""
    html = _expand_sim_markers(html)
    meta = getattr(page, "file", None)
    src = getattr(meta, "src_uri", "") if meta is not None else ""
    if src in {"index.md", "index.html"}:
        html = html.replace(
            '<div class="tabbed-set tabbed-alternate" data-tabs="1:2">',
            '<div class="tabbed-set tabbed-alternate hedron-try-it-tabs" data-tabs="1:2">',
            1,
        )
    return html
