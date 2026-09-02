"""Deployable proving application for hedron-docs 0.2."""

from pathlib import Path

from hedron_docs import compile_site, create_docs_app, load_config

APP_ROOT = Path(__file__).resolve().parent
config = load_config(APP_ROOT / "hedron-docs.toml")
manifest = compile_site(config)
app = create_docs_app(manifest)

__all__ = ["app"]
