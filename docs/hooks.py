"""MkDocs hooks for Read the Docs / local builds.

- Sync ``hedron-sim`` JS/CSS into ``docs/javascript`` and ``docs/stylesheets``.
- Expand ``<!-- hedron-sim:NAME -->`` markers from ``docs/includes/sim/``.
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


def on_page_markdown(markdown: str, **kwargs: object) -> str:  # noqa: ARG001
    """Replace ``<!-- hedron-sim:name -->`` with generated include HTML."""

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

    return _SIM_MARKER.sub(repl, markdown)
