"""Scaffold for ``hedron new`` FastAPI apps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from hedron.cli.discovery import _scaffold_dep


def _scaffold_fastapi(args: argparse.Namespace, dest: Path) -> int:
    (dest / "pyproject.toml").write_text(
        f'''[project]
name = "{args.name}"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "{_scaffold_dep("hedron")}",
    "uvicorn[standard]>=0.30",
]

[tool.hedron]
component_roots = ["components"]
theme = "default"
explorer = "off"
''',
        encoding="utf-8",
    )
    (dest / "app.py").write_text(
        """import os
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="Hedron App",
    security="standard",
    explorer="off",
    session_secret=os.environ.get(
        "HEDRON_SESSION_SECRET", "replace-in-production"
    ),
)

status = app.region("service-status", description="Live status panel")


def status_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "created": str(dest),
                "framework": "fastapi",
                "files": ["pyproject.toml", "app.py", "components/"],
            },
            indent=2,
        )
    )
    return 0
