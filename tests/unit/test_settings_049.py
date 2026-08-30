"""SETTINGS-049 retain-custom-loader for Workbench/Posit only."""

from __future__ import annotations

import importlib.metadata

import fastapi_workbench
from fastapi_workbench.config import WorkbenchConfig
from hedron_core.settings_disposition import (
    ALLOWED,
    NOT_CANDIDATES,
    SETTINGS_CANDIDATES,
    SETTINGS_DISPOSITIONS,
)


def test_settings_candidates_retain_custom_loader() -> None:
    assert SETTINGS_CANDIDATES == ("fastapi-workbench", "hedron-posit")
    assert "hedron.config.HedronSettings" in NOT_CANDIDATES
    for name in SETTINGS_CANDIDATES:
        assert SETTINGS_DISPOSITIONS[name] in ALLOWED
        assert SETTINGS_DISPOSITIONS[name] == "retain-custom-loader"
    assert isinstance(WorkbenchConfig(), WorkbenchConfig)
    assert "pydantic_settings" not in str(getattr(fastapi_workbench, "__file__", ""))
    dists = {item.metadata["Name"] for item in importlib.metadata.distributions()}
    # Flagship train does not adopt pydantic-settings.
    names = {name.lower() for name in dists}
    assert "pydantic-settings" not in names or SETTINGS_DISPOSITIONS["fastapi-workbench"] != "adopt"
