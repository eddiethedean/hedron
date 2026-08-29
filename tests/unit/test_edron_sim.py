from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import edron as ed
from edron_sim import Simulation, SimulationConfig


def _app() -> ed.App:
    app = ed.App(title="Simulation test", session_secret="test-secret")

    @app.page("/", title="Home")
    class Home(ed.Page):
        @ed.fragment(path="/status")
        def status(self) -> None:
            self.success("Ready")

        @ed.action(path="/refresh")
        def refresh(self) -> ed.Outcome:
            return ed.refresh(self.status)

        def render(self) -> None:
            self.heading("Simulation home")
            self.status()

    return app


def test_simulation_executes_real_edron_surfaces() -> None:
    artifact = Simulation.from_app(_app(), config=SimulationConfig(demo_id="test-app")).build()

    assert "Simulation home" in artifact.html
    assert "Ready" in artifact.html
    assert 'data-hedron-sim="test-app"' in artifact.html
    assert artifact.manifest["schema"] == "edron-sim/1"
    assert {route["kind"] for route in artifact.manifest["routes"]} == {
        "page",
        "fragment",
        "action",
    }
    action = artifact.responses["POST /refresh"].value
    assert action.role.value == "refresh"
    assert artifact.manifest["callbacks_executed"] is True


@pytest.mark.anyio
async def test_async_build_is_available_inside_async_pipelines() -> None:
    artifact = await Simulation.from_app(_app()).build_async()

    assert artifact.manifest["entrypoint"] == "/"


def test_simulation_bounds_are_enforced() -> None:
    with pytest.raises(ValueError, match="max_routes"):
        SimulationConfig(max_routes=0)
    with pytest.raises(ValueError, match="entrypoint"):
        SimulationConfig(entrypoint="home")


def test_showcase_preview_is_generated_from_the_real_edron_source() -> None:
    root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "generate_edron_sim_showcase.py"), "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr

    source = (root / "examples" / "edron-showcase" / "app.py").read_text(encoding="utf-8")
    preview = (root / "docs" / "includes" / "sim" / "edron-showcase.html").read_text(
        encoding="utf-8"
    )
    assert "import edron as ed" in source
    assert "from hedron" not in source
    assert 'data-hedron-sim="edron-showcase"' in preview
    assert "Command center" in preview
    assert "Preview clock · 12:42:18 UTC" in preview
    assert '"effects":[{"type":"refresh"' in preview
