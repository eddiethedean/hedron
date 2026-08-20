"""CLI command: generate reviewable interaction tests from a sealed catalog."""

from __future__ import annotations

import argparse
from pathlib import Path

from hedron.cli.discovery import _load_app
from hedron_core.catalog import compile_interaction_catalog
from hedron_core.testgen import GENERATOR_VERSION, generate_interaction_tests


def _cmd_testgen(args: argparse.Namespace) -> int:
    app = _load_app(getattr(args, "app", None))
    if app is not None:
        from hedron.interactions import app_interactions

        catalog = app_interactions(app)
    else:
        catalog = compile_interaction_catalog()
    source = generate_interaction_tests(
        catalog,
        profile=str(getattr(args, "profile", None) or "default"),
        generator_version=str(getattr(args, "generator_version", None) or GENERATOR_VERSION),
    )
    out = getattr(args, "out", None)
    if out:
        path = Path(out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
        print(f"wrote {path}")
    else:
        print(source, end="")
    return 0
