"""CLI command: compile CSS/assets into a build manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _cmd_build(args: argparse.Namespace) -> int:
    from hedron.build import run_build
    from hedron.cli.discovery import _load_app
    from hedron.config import load_hedron_settings

    base = Path(args.project or Path.cwd()).resolve()
    if getattr(args, "app", None):
        _load_app(args.app)
    settings = load_hedron_settings(base)
    result = run_build(project_dir=base, settings=settings, production=not args.dev)
    print(
        json.dumps(
            {
                "build_dir": str(result.build_dir),
                "digest": result.manifest.digest or result.manifest.to_dict()["digest"],
                "theme": result.manifest.theme,
                "assets": len(result.manifest.assets.assets),
            },
            indent=2,
        )
    )
    return 0
