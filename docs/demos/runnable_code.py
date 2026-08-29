"""Load pasteable Hedron ``app.py`` sources that reproduce docs sim demos.

Each file under ``docs/demos/runnable/`` is a minimal real Hedron app (not
``hedron-sim``). Aliases let related sims share one source of truth.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["ALIASES", "runnable_ids", "runnable_path", "runnable_source"]

_ROOT = Path(__file__).resolve().parent / "runnable"

# Sims that reuse another demo's runnable app.
ALIASES: dict[str, str] = {
    "component-auto-form": "component-form",
    "component-main-panel": "component-app-shell",
    "component-nav-link": "component-app-shell",
    "hello-refresh-quickstart": "hello-refresh",
    "edron-showcase-dashboard": "edron-showcase",
    "jobs-poll": "live-poll",
    "showcase-dashboard": "showcase",
}


def runnable_path(sim_id: str) -> Path:
    """Return the on-disk path for a sim's runnable ``app.py`` source."""
    resolved = ALIASES.get(sim_id, sim_id)
    return _ROOT / f"{resolved}.py"


def runnable_source(sim_id: str) -> str:
    """Return the runnable app source for ``sim_id``."""
    path = runnable_path(sim_id)
    if not path.is_file():
        raise FileNotFoundError(f"Missing runnable demo code for {sim_id!r} (expected {path.name})")
    return path.read_text(encoding="utf-8")


def runnable_ids() -> frozenset[str]:
    """Canonical sim ids that have a runnable file (excluding alias keys)."""
    return frozenset(path.stem for path in _ROOT.glob("*.py") if path.name != "__init__.py")
