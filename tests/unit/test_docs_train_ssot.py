"""Regression tests for release-train documentation pin validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_docs_train_ssot as ssot  # noqa: E402


def test_025_satellite_floors_require_fixed_patch_releases() -> None:
    assert ssot._has_compatible_satellite_floor('pip install "hedron[charts]>=0.25.1,<0.26"')
    assert ssot._has_compatible_satellite_floor(
        'pip install "hedron-charts[matplotlib]>=0.1.6,<0.2"'
    )
    assert ssot._has_compatible_satellite_floor('uv add "hedron-sample-kit>=0.1.6,<0.2"')
    assert not ssot._has_compatible_satellite_floor('pip install "hedron[charts]>=0.25.0,<0.26"')
    assert not ssot._has_compatible_satellite_floor('pip install "hedron-charts>=0.1.5,<0.2"')


def test_unbounded_fixed_charts_floor_is_rejected() -> None:
    assert ssot.UNBOUNDED_CHARTS_PKG.search("hedron-charts>=0.1.6")
    assert not ssot.UNBOUNDED_CHARTS_PKG.search("hedron-charts>=0.1.6,<0.2")
