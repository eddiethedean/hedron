"""MkDocs hooks for Read the Docs / local builds.

- Sync ``hedron-sim`` JS/CSS into ``docs/javascript`` and ``docs/stylesheets``.
- Expand ``<!-- hedron-sim:NAME -->`` markers from ``docs/includes/sim/`` *after*
  Markdown runs, so tokens like ``__HEDRON_SIM_UTC__`` are not turned into
  ``<strong>`` and so absolute demo ``href``s are not rewritten by the MD pipeline.
- STATUS.md stays canonical under ``docs/`` (synced to root). ROADMAP.md lives only under ``docs/``.
"""

from __future__ import annotations

import os
import re
import tomllib
from pathlib import Path

_DOCS = Path(__file__).resolve().parent
_SIM_INCLUDES = _DOCS / "includes" / "sim"
_SIM_MARKER = re.compile(r"<!--\s*hedron-sim:([a-z0-9-]+)\s*-->", re.IGNORECASE)
_RELEASE_STATUS_MARKER = "<!-- hedron-release-status -->"
_INSTALL_MATRIX_MARKER = "<!-- hedron-install-matrix -->"


def _release_facts() -> dict[str, object]:
    return tomllib.loads((_DOCS / "release.toml").read_text(encoding="utf-8"))


def _release_status_markdown(facts: dict[str, object]) -> str:
    release = facts["release"]
    assert isinstance(release, dict)
    return (
        '!!! success "1.0 is published"\n\n'
        f'    **Hedron {release["pypi_version"]}** is available from PyPI. '
        "The documentation describes the stable Hedron 1.0 API contract.\n"
    )


def _install_matrix_markdown(facts: dict[str, object]) -> str:
    release = facts["release"]
    assert isinstance(release, dict)
    hedron_pin = f'>={release["pin_floor"]},<{release["pin_ceiling"]}'
    return (
        "| Package | Install | Best for |\n"
        "|---|---|---|\n"
        f'| Hedron | `hedron{hedron_pin}` | FastAPI-native routes, component trees, '
        "data applications, and host integration |\n"
    )


def on_config(config):
    """Expose release metadata and copy optional simulation assets."""
    facts = _release_facts()
    release = facts["release"]
    edron = facts["edron"]
    version = os.environ.get("READTHEDOCS_VERSION", "local")
    version_type = os.environ.get("READTHEDOCS_VERSION_TYPE", "branch")
    config.extra["hedron_docs"] = {
        "version": version,
        "published_version": release["published_version"],
        "published_minor": ".".join(release["published_version"].split(".")[:2]),
        "development_version": release["development_version"],
        "is_development": version in {"local", "latest", "main"}
        or version_type == "branch",
        "hedron_pin": f'>={release["pin_floor"]},<{release["pin_ceiling"]}',
        "edron_version": edron["published_version"],
        "edron_pin": f'>={edron["pin_floor"]},<{edron["pin_ceiling"]}',
    }
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


def on_page_markdown(markdown: str, **kwargs: object) -> str:
    """Expand release facts before Markdown rendering."""
    page = kwargs.get("page")
    file = getattr(page, "file", None)
    source = getattr(file, "src_uri", "")
    if re.fullmatch(r"guides/whats-new-0\.\d+\.md", source):
        metadata = getattr(page, "meta", None)
        if isinstance(metadata, dict):
            search = metadata.setdefault("search", {})
            if isinstance(search, dict):
                search["exclude"] = True
    facts = _release_facts()
    return markdown.replace(
        _RELEASE_STATUS_MARKER, _release_status_markdown(facts)
    ).replace(_INSTALL_MATRIX_MARKER, _install_matrix_markdown(facts))


def on_page_content(html: str, **kwargs: object) -> str:
    """Expand sim islands after Markdown so tokens are not mangled."""
    return _expand_sim_markers(html)
