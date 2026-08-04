"""MkDocs hooks for Read the Docs / local builds.

STATUS.md and ROADMAP.md are canonical under ``docs/``. Sync them to the repository
root with ``scripts/sync_status_roadmap.py`` — this hook must not overwrite ``docs/``
from the root mirrors (that previously clobbered in-progress docs edits).
"""

from __future__ import annotations


def on_config(config):  # noqa: ANN001
    """No-op config hook kept so ``mkdocs.yml`` can retain an explicit hooks entry."""
    return config
