"""Scaffold for ``hedron new --flask``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hedron.cli.discovery import scaffold_dep as _scaffold_dep


def scaffold_flask(args: argparse.Namespace, dest: Path) -> int:
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "{_scaffold_dep("hedron-flask")}",
    "{_scaffold_dep("hedron-core")}",
    "flask>=3,<4",
]

[tool.hedron]
component_roots = ["components"]
''',
        encoding="utf-8",
    )
    (dest / "app.py").write_text(
        """import os
from datetime import datetime, timezone

from hedron_core import FragmentRegion, InteractionResult, Page, Text, html
from hedron_core.interaction import InteractionPolicy
from hedron_flask import HedronFlask

app = HedronFlask(__name__, security="standard")
assert app.flask is not None
app.flask.config["SECRET_KEY"] = os.environ.get(
    "HEDRON_SESSION_SECRET", "replace-in-production"
)

PANEL = FragmentRegion(id="panel", selector="#panel")


def panel_body() -> object:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(Text(f"Flask status · {stamp}"), id="panel")


@app.page("/")
def home() -> Page:
    return Page(
        html.div(
            Text("Hello from hedron new --flask"),
            panel_body(),
            html.button(
                Text("Refresh"),
                **{
                    "hx-get": "/status",
                    "hx-target": "#panel",
                    "hx-swap": "outerHTML",
                },
            ),
        ),
        title="Home",
    )


@app.view("/status", fragment_regions=(PANEL,))
def status() -> InteractionResult:
    return InteractionResult(
        content=panel_body(),
        region_id="panel",
        policy=InteractionPolicy(declared_regions=(PANEL,)),
    )


# WSGI entry: `flask --app app run` uses module-level Flask app
flask_app = app.flask
""",
        encoding="utf-8",
    )
    (dest / "README.md").write_text(
        "# Hedron Flask app\n\n"
        "Set `HEDRON_SESSION_SECRET` before production. "
        "Under `HEDRON_ENV=production`, placeholder secrets are refused "
        "unless listed in `HEDRON_SECURITY_RISK_ACCEPTANCE`.\n\n"
        "```bash\nuv sync && uv run flask --app app run\n```\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "flask",
                "files": ["pyproject.toml", "app.py", "README.md", "components/"],
            },
            indent=2,
        )
    )
    return 0


_scaffold_flask = scaffold_flask
