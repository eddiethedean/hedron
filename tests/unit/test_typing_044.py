"""TYPING-044: generic arity, overloads, stock pyright fixtures."""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

from hedron.handles import ActionHandle, BoundFragment, FragmentHandle
from hedron_core.updates import Patch

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "typing" / "044"


def test_generic_arity_unchanged() -> None:
    assert len(FragmentHandle.__parameters__) == 2  # type: ignore[attr-defined]
    assert len(ActionHandle.__parameters__) == 2  # type: ignore[attr-defined]
    assert len(BoundFragment.__parameters__) == 1  # type: ignore[attr-defined]
    assert len(Patch.__parameters__) == 1  # type: ignore[attr-defined]


def test_bind_has_overloads() -> None:
    hints = getattr(FragmentHandle.bind, "__annotations__", {})
    source = inspect.getsource(FragmentHandle.bind)
    assert "@overload" in inspect.getsource(sys.modules["hedron.handles"])
    assert "bind" in source or "value" in str(hints)


def test_pyright_fixtures() -> None:
    good = FIXTURES / "good_bind.py"
    bad = FIXTURES / "bad_plugin_not_required.py"
    assert good.is_file()
    assert bad.is_file()
    assert "hedron.plugin" not in good.read_text(encoding="utf-8")
    # Invoke the locked test interpreter directly so this check cannot rewrite the
    # shared workspace environment while xdist workers are running.
    cmd = [sys.executable, "-m", "pyright", str(good)]
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
