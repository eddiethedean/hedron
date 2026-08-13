"""HedronWorkbench remains a thin subclass of HedronPosit."""

from __future__ import annotations

from hedron_posit import HedronPosit
from hedron_workbench import HedronWorkbench


def test_workbench_is_subclass_of_posit() -> None:
    assert issubclass(HedronWorkbench, HedronPosit)


def test_markers_and_facade() -> None:
    app = HedronWorkbench()
    assert getattr(app, "__hedron_workbench__", False) is True
    assert getattr(app, "__hedron_posit__", False) is True
    assert isinstance(app, HedronPosit)


def test_public_reexports() -> None:
    import hedron_workbench as wb

    for name in (
        "WorkbenchConfig",
        "WorkbenchMode",
        "resolve_deployment",
        "workbenchify",
        "prepare_app",
    ):
        assert hasattr(wb, name)
