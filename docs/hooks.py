"""MkDocs hooks for Read the Docs / local builds."""

from __future__ import annotations

from pathlib import Path


def on_config(config):  # noqa: ANN001
    """Mirror the root ROADMAP into docs/ with paths rewritten for docs_dir."""
    docs_dir = Path(config["docs_dir"])
    root = docs_dir.parent
    source = root / "ROADMAP.md"
    target = docs_dir / "ROADMAP.md"
    text = source.read_text(encoding="utf-8")
    # Root ROADMAP links like docs/acceptance/X.md become acceptance/X.md in docs/.
    text = text.replace("](docs/", "](")
    # Avoid retriggering MkDocs' file watcher when the generated copy is current.
    if not target.exists() or target.read_text(encoding="utf-8") != text:
        target.write_text(text, encoding="utf-8")
    return config
