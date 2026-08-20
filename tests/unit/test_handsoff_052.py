"""HANDSOFF-052 evidence."""

from __future__ import annotations

from hedron_posit import HedronPosit, PositConfig
from hedron_posit.config import WorkbenchConfig, WorkbenchMode


def test_hands_off_enables_mount_adaptation_without_workbench() -> None:
    app = HedronPosit(
        title="handsoff-052",
        root_path="/apps/demo",
        posit=PositConfig(hands_off=True, workbench=WorkbenchConfig(mode=WorkbenchMode.OFF)),
    )
    assert app.hands_off is True
    assert bool(getattr(app.state, "hedron_posit_hands_off", False)) is True
    assert app._workbench_asgi.active is True
    assert app._workbench_asgi.expected_mount == "/apps/demo"
    assert app.adapt_local_url("/profile") == "/apps/demo/profile"


def test_hands_off_off_by_default() -> None:
    app = HedronPosit(title="handsoff-default")
    assert app.hands_off is False
